import json
import pandas as pd


def extract_top_nodes_by_pagerank(
    community_file="./CommunityMining/results/paper/louvain.csv",
    pagerank_file="./CentralityMeasure/results/centrality_measures.csv",
    top_n_communities=10,
    top_nodes_per_community=50,
) -> list[str]:
    """
    Extracts the top nodes by PageRank centrality from the largest communities.

    Args:
        community_file (str): Path to the community CSV file.
        pagerank_file (str): Path to the PageRank centrality CSV file.
        top_n_communities (int): Number of top communities to consider.
        top_nodes_per_community (int): Number of top nodes to extract per community.

    Returns:
        tuple: Path to the output JSON file and the total number of selected IDs.
    """
    # Load the data
    community_data = pd.read_csv(community_file)
    pagerank_data = pd.read_csv(pagerank_file)

    # Merge community data with pagerank centrality
    merged_data = pd.merge(community_data, pagerank_data, on="id")

    # Count nodes in each community and get the largest communities
    community_counts = merged_data["community"].value_counts().head(top_n_communities)
    largest_communities = community_counts.index

    # List to store selected node IDs
    selected_ids = []

    # Iterate over each of the largest communities
    for community in largest_communities:
        # Filter nodes for the community
        community_nodes = merged_data[merged_data["community"] == community]

        # Sort by pagerank_centrality and select top nodes
        top_nodes = community_nodes.nlargest(
            top_nodes_per_community, "pagerank_centrality"
        )

        # Append the selected node IDs to the list
        selected_ids.extend(top_nodes["id"].tolist())

    return selected_ids


if __name__ == "__main__":
    output_path, total_ids = extract_top_nodes_by_pagerank()
    print(f"Saved {total_ids} IDs to {output_path}")
