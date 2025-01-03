import pandas as pd
import igraph as ig
import json
from collections import defaultdict
from typing import Dict
from tqdm import tqdm  # 导入 tqdm 用于显示进度条


def compute_community_metrics(node: pd.DataFrame, edge: pd.DataFrame, community_file: str, output_json: str) -> None:
    """
    Calculate the shortest paths and radius for each community and save the results to a JSON file.

    Parameters:
        - node (pd.DataFrame): DataFrame containing node information, including an "id" column.
        - edge (pd.DataFrame): DataFrame containing edge information, including "src" and "dst" columns.
        - community_file (str): Path to the CSV file containing community labels.
        - output_json (str): Path to the output JSON file where results will be saved.
    """
    # Load community labels
    community_labels = pd.read_csv(community_file)

    # Create igraph Graph
    G = ig.Graph()
    G.add_vertices(node["id"].unique())
    G.add_edges([(src, dst)
                for src, dst in zip(edge["src"], edge["dst"]) if src != dst])

    G.vs["name"] = node["id"].tolist()

    # Map the community labels to the graph nodes
    community_mapping = dict(
        zip(community_labels["id"], community_labels["community"]))
    G.vs["community"] = [community_mapping[node_id]
                         for node_id in G.vs["name"]]

    # Dictionary to store community metrics
    community_metrics = defaultdict(
        lambda: {"shortest_paths": [], "radii": [], "diameters": []})

    # Iterate over all communities and calculate the shortest paths and radii with a progress bar
    community_ids = set(community_labels["community"])
    for community_id in tqdm(community_ids, desc="Processing Communities", unit="community"):
        community_nodes = [
            v.index for v in G.vs if v["community"] == community_id]
        subgraph = G.subgraph(community_nodes)

        # Calculate the diameter and radius for this community
        community_diameter = subgraph.diameter()
        community_radius = subgraph.radius()

        community_metrics[community_id]["diameters"] = community_diameter
        community_metrics[community_id]["radii"] = community_radius

    # Save the results to a JSON file
    with open(output_json, 'w') as f:
        json.dump(community_metrics, f, indent=4)

    print(f"Results saved to {output_json}")


if __name__ == "__main__":
    from utils import load_paper_node, load_paper_edge

    node_data = load_paper_node("./data/paper/node.csv", skip_isolate=True)
    edge_data = load_paper_edge("./data/paper/edge.csv")
    community_file = "./CommunityMining/results/louvain/louvain.csv"
    output_json = "./CommunityMining/results/community_metrics.json"

    compute_community_metrics(node_data, edge_data,
                              community_file, output_json)
