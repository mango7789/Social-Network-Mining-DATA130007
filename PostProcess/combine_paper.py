import json
import shutil
import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")


def process_paper_data(
    paper_node_df,
    paper_edge_df,
    title_map,
    venue_map,
    filtered_ids,
    community_path="./CommunityMining/results/paper/louvain.csv",
    centrality_path="./CentralityMeasure/results/centrality_measures.csv",
    diameter_path="./CentralityMeasure/results/diameter.json",
    output_dir="visualize",
):
    """
    Processes paper data to generate various metrics and filter nodes and edges.

    Args:
        paper_node_df
        paper_edge_df
        community_path (str): Path to the community data CSV file.
        centrality_path (str): Path to the centrality measures CSV file.
        diameter_path (str): Path to the diameter JSON file.
        venue_map_path (str): Path to the venue mapping JSON file.
        title_map_path (str): Path to the title mapping JSON file.
        output_dir (str): Directory to save the processed data.

    Returns:
        dict: Paths to the output files.
    """
    # Create output directory
    vis_dir = Path(output_dir)
    vis_dir.mkdir(parents=True, exist_ok=True)

    # Load and process community data
    community_df = pd.read_csv(community_path)
    paper_node_df = paper_node_df.merge(
        community_df[["id", "community"]], on="id", how="left"
    )
    top_communities = paper_node_df["community"].value_counts().head(10).index.tolist()
    paper_node_df = paper_node_df[paper_node_df["community"].isin(top_communities)]

    # Move diameter file
    shutil.move(diameter_path, vis_dir / "diameter.json")

    # Add centrality column
    centrality_df = pd.read_csv(centrality_path)
    paper_node_df = paper_node_df.merge(
        centrality_df[["id", "pagerank_centrality"]], on="id", how="left"
    )

    # Calculate average in-degree
    average_in_d = paper_node_df.groupby("community")["in_d"].mean().reset_index()
    sorted_average_in_d = average_in_d.sort_values(by="in_d", ascending=False)
    average_in_d_dict = sorted_average_in_d.to_dict(orient="records")
    with open(vis_dir / "citation.json", "w") as f:
        json.dump(average_in_d_dict, f, indent=4)

    # Calculate average centrality
    average_centrality = (
        paper_node_df.groupby("community")["pagerank_centrality"].mean().reset_index()
    )
    sorted_average_centrality = average_centrality.sort_values(
        by="pagerank_centrality", ascending=False
    )
    average_centrality_dict = sorted_average_centrality.to_dict(orient="records")
    with open(vis_dir / "centrality.json", "w") as f:
        json.dump(average_centrality_dict, f, indent=4)

    # Calculate degree distribution
    degree_counts_by_community = (
        paper_node_df.groupby("community")["out_d"].value_counts().unstack(fill_value=0)
    )
    degree_counts = {}
    for community, row in degree_counts_by_community.iterrows():
        non_zero_degrees = row[row > 0]
        if not non_zero_degrees.empty:
            min_degree = non_zero_degrees.index.min()
            max_degree = non_zero_degrees.index.max()
            degree_counts[community] = {
                degree: row[degree] if degree in non_zero_degrees.index else 0
                for degree in range(min_degree, max_degree + 1)
            }
    with open(vis_dir / "degree.json", "w") as f:
        json.dump(degree_counts, f, indent=4)

    # Save community proportions
    community_counts = paper_node_df["community"].value_counts()
    community_proportions_dict = community_counts.to_dict()
    with open(vis_dir / "counts.json", "w") as f:
        json.dump(community_proportions_dict, f, indent=4)

    # Filter nodes and edges
    filtered_ids_set = set(filtered_ids)

    paper_node_df_filtered = paper_node_df[paper_node_df["id"].isin(filtered_ids_set)]
    paper_edge_df_filtered = paper_edge_df[
        paper_edge_df["src"].isin(filtered_ids_set)
        & paper_edge_df["dst"].isin(filtered_ids_set)
    ]

    # Map title and venue
    paper_node_df_filtered["title"] = paper_node_df_filtered["id"].map(title_map)
    paper_node_df_filtered["venue"] = paper_node_df_filtered["venue"].map(venue_map)

    # Select and save columns
    columns_to_save = [
        "id",
        "authors",
        "year",
        "venue",
        "out_d",
        "in_d",
        "title",
        "community",
        "pagerank_centrality",
    ]
    paper_node_df_filtered = paper_node_df_filtered[columns_to_save]

    paper_node_path = vis_dir / "paper_node.csv"
    paper_edge_path = vis_dir / "paper_edge.csv"

    paper_node_df_filtered.to_csv(paper_node_path, index=False)
    paper_edge_df_filtered.to_csv(paper_edge_path, index=False)

    # return {
    #     "paper_node": paper_node_path,
    #     "paper_edge": paper_edge_path,
    #     "citation": vis_dir / "citation.json",
    #     "centrality": vis_dir / "centrality.json",
    #     "degree": vis_dir / "degree.json",
    #     "counts": vis_dir / "counts.json",
    # }


if __name__ == "__main__":
    output_files = process_paper_data()
    print(f"Files saved: {output_files}")
