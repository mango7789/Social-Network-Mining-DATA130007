import pandas as pd
import igraph as ig
from pathlib import Path


def analyze_community_result(node_df, community_file, edge_df, output_path):
    """
    从划分结果文件分析社区划分，计算每个社区的占比，并保存模块度。

    Parameters:
        - node_df (pd.DataFrame): DataFrame containing node information (with 'id' column).
        - community_file (Path): Path to the file with community division result (id, community).
        - edge_df (pd.DataFrame): DataFrame containing edge information.
        - output_path (Path): Output path to save results.
    """
    # Step 1: Load the community division results (id, community)
    community_df = pd.read_csv(community_file)
    community_df.set_index("id", inplace=True)

    # Map community labels back to the node_df based on 'id'
    node_df["community"] = node_df["id"].map(community_df["community"])

    # Step 2: Handle NaN values in community labels
    if node_df["community"].isnull().any():
        print("Found NaN values in community labels. Filling with a default value (0).")
        # Fill NaN with 0 or another valid community ID
        node_df["community"].fillna(0, inplace=True)

    # Ensure that community labels are integers (this can also help avoid issues with modularity calculation)
    node_df["community"] = node_df["community"].astype(int)

    # Step 3: Calculate community proportions
    community_sizes = node_df["community"].value_counts()
    total_nodes = len(node_df)
    community_proportions = community_sizes / total_nodes

    # Save community proportions
    community_proportions_df = pd.DataFrame(
        {
            "community_id": community_proportions.index,
            "node_count": community_sizes.values,
            "proportion": community_proportions.values,
        }
    )
    # Ensure the output path exists
    output_path.mkdir(parents=True, exist_ok=True)
    community_proportions_df.to_csv(
        output_path / "community_proportions.csv", index=False
    )
    print(
        f"Community proportions saved to: {output_path / 'community_proportions.csv'}"
    )

    # Step 4: Build igraph from the edge data
    edges = list(zip(edge_df["src"], edge_df["dst"]))
    G = ig.Graph()
    G.add_vertices(node_df["id"].unique())
    G.add_edges(edges)

    # Add community attribute to nodes
    G.vs["community"] = node_df["community"].tolist()

    # Step 5: Calculate Modularity
    modularity = G.modularity(node_df["community"])
    print(f"Modularity: {modularity}")

    # Save modularity result
    with open(output_path / "modularity.txt", "w") as f:
        f.write(f"Modularity: {modularity}")
    print(f"Modularity saved to: {output_path / 'modularity.txt'}")


if __name__ == "__main__":
    # Load node and edge data
    node_data = pd.read_csv("./data/paper/node.csv")
    edge_data = pd.read_csv("./data/paper/edge.csv")
    community_file = Path("./CommunityMining/results/louvain.csv")
    output_path = Path("./CommunityMining/results")

    # Perform the analysis
    analyze_community_result(node_data, community_file, edge_data, output_path)
