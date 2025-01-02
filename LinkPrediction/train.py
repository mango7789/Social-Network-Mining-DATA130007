import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from model import LACE, GLACE
from pipeline import DataUtils, score_link_prediction
import pickle
import time
import scipy.sparse as sp
import numpy as np
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", default="cora_ml", help="Dataset name")
    parser.add_argument("model", default="glace", help="Model type: lace or glace")
    parser.add_argument("--suf", default="", help="Suffix for dataset")
    parser.add_argument(
        "--proximity",
        default="first-order",
        help="Proximity type: first-order or second-order",
    )
    parser.add_argument(
        "--embedding_dim", type=int, default=64, help="Dimension of embeddings"
    )
    parser.add_argument("--batch_size", type=int, default=128, help="Batch size")
    parser.add_argument("--K", type=int, default=5, help="Number of negative samples")
    parser.add_argument(
        "--learning_rate", type=float, default=0.001, help="Learning rate"
    )
    parser.add_argument(
        "--num_batches", type=int, default=100000, help="Number of training batches"
    )
    parser.add_argument(
        "--is_all",
        action="store_true",
        help="Train with all edges; no validation or test set",
    )
    args = parser.parse_args()

    train(args)


def train(args):
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 构建图文件路径
    graph_file = f"./LinkPrediction/data/{args.name}/{args.name}.npz"
    if not args.is_all:
        graph_file = graph_file.replace(".npz", "_train.npz")

    # 初始化数据加载器
    data_loader = DataUtils(graph_file, args.is_all)

    # 处理输入特征
    suffix = args.proximity
    if args.suf != "oh":
        args.X = data_loader.X
    else:
        args.X = sp.identity(data_loader.X.shape[0]).astype(np.float32)

    if not args.is_all:
        args.val_edges = data_loader.val_edges
        args.val_ground_truth = data_loader.val_ground_truth

    # 初始化模型
    model_type = args.model.lower()
    if model_type == "lace":
        model = LACE(args)
    elif model_type == "glace":
        model = GLACE(args)
    else:
        raise ValueError("模型类型必须为 'lace' 或 'glace'")

    model.to(device)

    # 定义优化器（假设模型没有内部优化器）
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    # 设置模型为训练模式
    model.train()

    # 创建保存嵌入的目录
    os.makedirs("emb", exist_ok=True)

    print(
        "-------------------------- "
        + model_type.upper()
        + " --------------------------"
    )
    if model.val_set:
        print("batches\tloss\tval_auc\tval_ap\tsampling_time\ttraining_time\tdatetime")
    else:
        print("batches\tloss\tsampling_time\ttraining_time\tdatetime")

    sampling_time_total, training_time_total = 0, 0

    for b in range(args.num_batches):
        t1 = time.time()

        # 获取一个批次的数据
        u_i, u_j, label = data_loader.fetch_next_batch(
            batch_size=args.batch_size, K=args.K
        )

        # 转换为张量并移动到设备
        u_i = torch.LongTensor(u_i).to(device)
        u_j = torch.LongTensor(u_j).to(device)
        label = torch.FloatTensor(label).to(device)

        t2 = time.time()
        sampling_time = t2 - t1
        sampling_time_total += sampling_time

        # 清零梯度
        optimizer.zero_grad()

        # 前向传播
        if model_type == "lace":
            similarity, embedding, context_embedding = model(
                u_i, u_j, proximity=args.proximity
            )
            loss = model.compute_loss(similarity, label)
        elif model_type == "glace":
            kl_distance, mu, sigma, ctx_mu = model(u_i, u_j, proximity=args.proximity)
            energy = model.energy_kl(u_i, u_j, proximity=args.proximity)
            loss = model.compute_loss(energy, label)

        # 反向传播
        loss.backward()
        optimizer.step()

        training_time = time.time() - t2
        training_time_total += training_time

        # 打印日志
        if (b + 1) % 50 == 0 or b == args.num_batches - 1:
            if model.val_set and ((b + 1) % 50 == 0 or b == args.num_batches - 1):
                with torch.no_grad():
                    model.eval()
                    if model_type == "lace":
                        val_energy = model.get_validation_energy(embedding)
                    elif model_type == "glace":
                        # 计算验证集上的能量
                        val_u_i = torch.LongTensor(args.val_edges[:, 0]).to(device)
                        val_u_j = torch.LongTensor(args.val_edges[:, 1]).to(device)
                        val_energy = model.energy_kl(
                            val_u_i, val_u_j, proximity=args.proximity
                        )
                        val_energy = val_energy.cpu().numpy()
                    if model_type == "glace":
                        val_auc, val_ap = score_link_prediction(
                            data_loader.val_ground_truth, val_energy
                        )
                    elif model_type == "lace":
                        val_auc, val_ap = score_link_prediction(
                            data_loader.val_ground_truth, val_energy.cpu().numpy()
                        )
                    model.train()
                print(
                    f"{b}\t{loss.item():.6f}\t{val_auc:.6f}\t{val_ap:.6f}\t{sampling_time_total:.2f}\t{training_time_total:.2f}\t{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
                )
            else:
                print(
                    f"{b}\t{loss.item():.6f}\t{sampling_time_total:.2f}\t{training_time_total:.2f}\t{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
                )

            sampling_time_total, training_time_total = 0, 0

        # 保存嵌入
        if (b + 1) % 50 == 0 or b == args.num_batches - 1:
            with torch.no_grad():
                model.eval()
                if model_type == "glace":
                    # 计算所有节点的mu和sigma
                    # 假设DataUtils有一个方法来获取所有节点的索引
                    all_nodes = torch.arange(args.X.shape[0]).long().to(device)
                    kl_distance_all, mu_all, sigma_all, _ = model(
                        all_nodes, all_nodes, proximity=args.proximity
                    )
                    mu_all = mu_all.cpu().numpy()
                    sigma_all = sigma_all.cpu().numpy()
                    embedding_data = {
                        "mu": data_loader.embedding_mapping(mu_all),
                        "sigma": data_loader.embedding_mapping(sigma_all),
                    }
                    with open(
                        f"emb/{model_type}_{args.name}_embedding_{suffix}.pkl", "wb"
                    ) as f:
                        pickle.dump(embedding_data, f)
                else:
                    # 对于LACE模型，保存embedding
                    all_nodes = torch.arange(args.X.shape[0]).long().to(device)
                    similarity_all, embedding_all, _ = model(
                        all_nodes, all_nodes, proximity=args.proximity
                    )
                    embedding_all = embedding_all.cpu().numpy()
                    embedding_mapped = data_loader.embedding_mapping(embedding_all)
                    with open(
                        f"emb/{model_type}_{args.name}_embedding_{suffix}.pkl", "wb"
                    ) as f:
                        pickle.dump(embedding_mapped, f)
                model.train()


if __name__ == "__main__":
    main()
