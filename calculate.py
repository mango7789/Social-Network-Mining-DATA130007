import pandas as pd
import igraph as ig
import json
from collections import defaultdict
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor


def compute_community_metrics(node: pd.DataFrame, edge: pd.DataFrame, community_file: str, output_json: str) -> None:
    """
    计算每个社区的最短路径、半径和直径，并将结果保存到 JSON 文件。
    """

    # 加载社区标签
    try:
        community_labels = pd.read_csv(community_file)
    except FileNotFoundError:
        print(f"错误: 找不到社区文件 {community_file} 。")
        return
    except pd.errors.EmptyDataError:
        print(f"错误: 社区文件 {community_file} 为空。")
        return

    # 创建图
    G = ig.Graph()
    G.add_vertices(node["id"].unique())
    G.add_edges([(src, dst)
                for src, dst in zip(edge["src"], edge["dst"]) if src != dst])

    G.vs["name"] = node["id"].tolist()

    # 将社区标签映射到图的节点
    community_mapping = dict(
        zip(community_labels["id"], community_labels["community"]))

    G.vs["community"] = [community_mapping.get(
        node_id, None) for node_id in G.vs["name"]]

    # 处理没有社区标签的节点
    missing_community_nodes = [v["name"]
                               for v in G.vs if v["community"] is None]
    if missing_community_nodes:
        print(f"警告: 以下节点缺少社区标签: {missing_community_nodes}")

    # 存储社区的度量数据
    community_metrics = defaultdict(
        lambda: {"shortest_paths": [], "radii": [], "diameters": []})

    # 计算每个社区的节点数量
    community_sizes = defaultdict(int)
    for v in G.vs:
        community_sizes[v["community"]] += 1

    # 获取节点数最多的10个社区
    largest_communities = sorted(
        community_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
    largest_community_ids = [
        community_id for community_id, size in largest_communities]

    print(f"最大的10个社区的社区ID: {largest_community_ids}")

    # 使用并行处理来加速社区计算
    def calculate_community_metrics(community_id):
        community_nodes = [
            v.index for v in G.vs if v["community"] == community_id]

        if len(community_nodes) > 1:  # 忽略单节点社区，直径/半径无法定义
            subgraph = G.subgraph(community_nodes)

            # 计算直径和半径
            community_diameter = subgraph.diameter()
            community_radius = subgraph.radius()

            return community_id, community_diameter, community_radius
        return None

    # 使用进度条和并行处理
    with ProcessPoolExecutor(max_workers=8) as executor:  # 调整工作进程数
        results = list(tqdm(executor.map(calculate_community_metrics, largest_community_ids),
                            total=len(largest_community_ids),
                            desc="处理社区",
                            unit="社区"))

    # 将结果存储到字典中
    for result in results:
        if result:
            community_id, community_diameter, community_radius = result
            community_metrics[community_id]["diameters"] = community_diameter
            community_metrics[community_id]["radii"] = community_radius

    # 将结果保存到 JSON 文件
    with open(output_json, 'w') as f:
        json.dump(community_metrics, f, indent=4)

    print(f"结果已保存到 {output_json}")


if __name__ == "__main__":
    from utils import load_paper_node, load_paper_edge

    node_data = load_paper_node("./data/paper/node.csv", skip_isolate=True)
    edge_data = load_paper_edge("./data/paper/edge.csv")
    community_file = "./CommunityMining/results/louvain/louvain.csv"
    output_json = "./CommunityMining/results/community_metrics.json"

    compute_community_metrics(node_data, edge_data,
                              community_file, output_json)
