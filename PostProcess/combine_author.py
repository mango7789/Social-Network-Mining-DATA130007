import pandas as pd
from pathlib import Path


def process_author_data(
    author_node_df,
    author_edge_df,
    filtered_ids,
    community_path="./CommunityMining/results/author/community_label_propagation.csv",
    output_dir="visualize",
):
    # Load community data
    community_df = pd.read_csv(community_path)
    community_df["id"] = community_df["id"].astype(str)

    # Merge and filter top-10 communities
    author_node_df = author_node_df.merge(
        community_df[["id", "community"]], on="id", how="left"
    )
    top_communities = author_node_df["community"].value_counts().head(10).index.tolist()
    author_node_df = author_node_df[author_node_df["community"].isin(top_communities)]

    # Load filtered IDs
    filtered_ids_set = set(filtered_ids)

    # Filter nodes and edges
    author_node_df_filtered = author_node_df[
        author_node_df["id"].isin(filtered_ids_set)
    ]
    author_edge_df_filtered = author_edge_df[
        author_edge_df["src"].isin(filtered_ids_set)
        & author_edge_df["dst"].isin(filtered_ids_set)
    ]

    # Save filtered data
    vis_dir = Path(output_dir)
    vis_dir.mkdir(parents=True, exist_ok=True)

    author_node_out_path = vis_dir / "author_node.csv"
    author_edge_out_path = vis_dir / "author_edge.csv"

    author_node_df_filtered.to_csv(author_node_out_path, index=False)
    author_edge_df_filtered.to_csv(author_edge_out_path, index=False)


if __name__ == "__main__":
    process_author_data()
