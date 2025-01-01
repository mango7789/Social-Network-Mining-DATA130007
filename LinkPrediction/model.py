import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import scipy.sparse as sp
import numpy as np

# 设置随机种子
seed = 42
torch.manual_seed(seed)
np.random.seed(seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed(seed)

def sparse_feeder(M):
    """
    将稀疏矩阵转换为 PyTorch 稀疏张量所需的格式。
    """
    M = sp.coo_matrix(M, dtype=np.float32)
    indices = torch.LongTensor([M.row, M.col])
    values = torch.FloatTensor(M.data)
    shape = M.shape
    return indices, values, shape

class LACE(nn.Module):
    def __init__(self, args):
        super(LACE, self).__init__()
        self.N, self.D = args.X.shape
        self.L = args.embedding_dim
        self.n_hidden = [512]

        # 构建模型
        self.build_model(args)

        # 如果不是使用全部数据进行验证，准备验证集相关
        self.val_set = False
        if not args.is_all:
            self.val_edges = torch.LongTensor(args.val_edges)
            self.val_ground_truth = torch.FloatTensor(args.val_ground_truth)
            self.val_set = True

    def build_model(self, args):
        # 处理稀疏输入
        indices, values, shape = sparse_feeder(args.X)
        self.register_buffer('X_indices', indices)
        self.register_buffer('X_values', values)
        self.X_shape = torch.Size(shape)  # 将 X_shape 作为普通属性存储

        # 定义隐藏层
        layers = []
        input_dim = self.D
        for hidden_dim in self.n_hidden:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim
        self.encoder = nn.Sequential(*layers)

        # 嵌入层
        self.embedding_layer = nn.Linear(input_dim, self.L)

        # 上下文嵌入层（用于 proximity）
        context_layers = []
        input_dim = self.D
        for hidden_dim in self.n_hidden:
            context_layers.append(nn.Linear(input_dim, hidden_dim))
            context_layers.append(nn.ReLU())
            input_dim = hidden_dim
        self.context_encoder = nn.Sequential(*context_layers)
        self.context_embedding_layer = nn.Linear(input_dim, self.L)

        # 优化器
        self.optimizer = optim.Adam(self.parameters(), lr=args.learning_rate)

    def forward(self, u_i, u_j, proximity='first-order'):
        # 稀疏矩阵乘法
        X_sparse = torch.sparse.FloatTensor(self.X_indices, self.X_values, self.X_shape).to(u_i.device)
        X_dense = X_sparse.to_dense()
        encoded = self.encoder(X_dense)
        embedding = self.embedding_layer(encoded)

        if proximity == 'first-order':
            u_j_embedding = embedding[u_j]
        else:
            context_encoded = self.context_encoder(X_dense)
            context_embedding = self.context_embedding_layer(context_encoded)
            u_j_embedding = context_embedding[u_j]

        # 获取嵌入向量
        u_i_embedding = embedding[u_i]

        # 计算相似度
        similarity = torch.sum(u_i_embedding * u_j_embedding, dim=1)

        return similarity, embedding, context_embedding if proximity != 'first-order' else None

    def compute_loss(self, similarity, label):
        """
        计算损失函数
        """
        loss = -torch.mean(F.logsigmoid(label * similarity))
        return loss

    def get_validation_energy(self, embedding):
        if self.val_set:
            u_i = self.val_edges[:, 0]
            u_j = self.val_edges[:, 1]
            u_i_emb = embedding[u_i]
            u_j_emb = embedding[u_j]
            neg_val_energy = torch.sum(u_i_emb * u_j_emb, dim=1)
            return neg_val_energy
        else:
            return None

class GLACE(nn.Module):
    def __init__(self, args):
        super(GLACE, self).__init__()
        self.N, self.D = args.X.shape
        self.L = args.embedding_dim
        self.n_hidden = [512]

        # 构建模型
        self.build_model(args)

        # 如果不是使用全部数据进行验证，准备验证集相关
        self.val_set = False
        if not args.is_all:
            self.val_edges = torch.LongTensor(args.val_edges)
            self.val_ground_truth = torch.FloatTensor(args.val_ground_truth)
            self.val_set = True

    def build_model(self, args):
        # 处理稀疏输入
        indices, values, shape = sparse_feeder(args.X)
        self.register_buffer('X_indices', indices)
        self.register_buffer('X_values', values)
        self.X_shape = torch.Size(shape)  # 将 X_shape 作为普通属性存储

        # 定义隐藏层
        layers = []
        input_dim = self.D
        for hidden_dim in self.n_hidden:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim
        self.encoder = nn.Sequential(*layers)

        # 均值和方差嵌入层
        self.mu_layer = nn.Linear(input_dim, self.L)
        self.sigma_layer = nn.Linear(input_dim, self.L)

        # 上下文嵌入层（仅在 second-order proximity 时使用）
        if args.proximity == 'second-order':
            context_layers = []
            input_dim = self.D
            for hidden_dim in self.n_hidden:
                context_layers.append(nn.Linear(input_dim, hidden_dim))
                context_layers.append(nn.ReLU())
                input_dim = hidden_dim
            self.context_encoder = nn.Sequential(*context_layers)
            self.ctx_mu_layer = nn.Linear(input_dim, self.L)
            self.ctx_sigma_layer = nn.Linear(input_dim, self.L)

        # 优化器
        self.optimizer = optim.Adam(self.parameters(), lr=args.learning_rate)

    def forward(self, u_i, u_j, proximity='first-order'):
        # 稀疏矩阵乘法
        X_sparse = torch.sparse.FloatTensor(self.X_indices, self.X_values, self.X_shape).to(u_i.device)
        X_dense = X_sparse.to_dense()
        encoded = self.encoder(X_dense)
        mu = self.mu_layer(encoded)
        log_sigma = self.sigma_layer(encoded)
        sigma = F.elu(log_sigma) + 1 + 1e-14

        if proximity == 'second-order':
            ctx_encoded = self.context_encoder(X_dense)
            ctx_mu = self.ctx_mu_layer(ctx_encoded)
            ctx_log_sigma = self.ctx_sigma_layer(ctx_encoded)
            ctx_sigma = F.elu(ctx_log_sigma) + 1 + 1e-14

        # 获取嵌入向量
        mu_i = mu[u_i]
        sigma_i = sigma[u_i]

        if proximity == 'first-order':
            mu_j = mu[u_j]
            sigma_j = sigma[u_j]
        elif proximity == 'second-order':
            mu_j = ctx_mu[u_j]
            sigma_j = ctx_sigma[u_j]

        # 计算 KL 散度
        kl_distance = self.compute_kl(mu_i, sigma_i, mu_j, sigma_j)

        return kl_distance, mu, sigma, ctx_mu if proximity == 'second-order' else None

    def compute_kl(self, mu_i, sigma_i, mu_j, sigma_j):
        """
        计算 KL 散度
        """
        # KL(P||Q)
        sigma_ratio = sigma_j / sigma_i
        trace_fac = torch.sum(sigma_ratio, dim=1)
        log_det = torch.sum(torch.log(sigma_ratio + 1e-14), dim=1)
        mu_diff_sq = torch.sum((mu_i - mu_j) ** 2 / sigma_i, dim=1)
        kl_ij = 0.5 * (trace_fac + mu_diff_sq - self.L - log_det)

        # KL(Q||P)
        sigma_ratio = sigma_i / sigma_j
        trace_fac = torch.sum(sigma_ratio, dim=1)
        log_det = torch.sum(torch.log(sigma_ratio + 1e-14), dim=1)
        mu_diff_sq = torch.sum((mu_j - mu_i) ** 2 / sigma_j, dim=1)
        kl_ji = 0.5 * (trace_fac + mu_diff_sq - self.L - log_det)

        kl_distance = 0.5 * (kl_ij + kl_ji)
        return kl_distance

    def compute_loss(self, energy, label):
        """
        计算损失函数
        """
        loss = -torch.mean(F.logsigmoid(label * energy))
        return loss

    def energy_kl(self, u_i, u_j, proximity='first-order'):
        kl_distance, _, _, _ = self.forward(u_i, u_j, proximity)
        return -kl_distance  # 负的 KL 散度作为能量

    def get_validation_energy(self, proximity='first-order'):
        if self.val_set:
            kl_distance = self.energy_kl(self.val_edges[:, 0], self.val_edges[:, 1], proximity)
            neg_val_energy = -kl_distance
            return neg_val_energy
        else:
            return None

# 示例用法
if __name__ == "__main__":
    # 假设 args 是一个包含所有必要属性的对象
    class Args:
        def __init__(self):
            self.X = sp.csr_matrix(np.random.rand(1000, 500))  # 示例稀疏矩阵
            self.embedding_dim = 128
            self.batch_size = 32
            self.K = 5
            self.is_all = False
            self.val_edges = np.random.randint(0, 1000, size=(100, 2))
            self.val_ground_truth = np.random.rand(100)
            self.proximity = 'first-order'  # 或 'second-order'
            self.learning_rate = 0.001

    args = Args()

    # 初始化模型
    lace_model = LACE(args)
    glace_model = GLACE(args)

    # 示例输入
    u_i = torch.LongTensor(np.random.randint(0, args.X.shape[0], size=(args.batch_size * (args.K + 1),)))
    u_j = torch.LongTensor(np.random.randint(0, args.X.shape[0], size=(args.batch_size * (args.K + 1),)))
    label = torch.FloatTensor(np.random.choice([-1, 1], size=(args.batch_size * (args.K + 1),)))

    # 将模型移动到 GPU（如果可用）
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    lace_model.to(device)
    glace_model.to(device)
    u_i = u_i.to(device)
    u_j = u_j.to(device)
    label = label.to(device)

    # 前向传播和损失计算（以 LACE 为例）
    similarity, embedding, context_embedding = lace_model(u_i, u_j, proximity=args.proximity)
    loss = lace_model.compute_loss(similarity, label)

    # 反向传播和优化
    lace_model.optimizer.zero_grad()
    loss.backward()
    lace_model.optimizer.step()

    print(f"LACE Loss: {loss.item()}")

    # 类似地，可以进行 GLACE 模型的训练