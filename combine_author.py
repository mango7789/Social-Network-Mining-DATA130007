import pandas as pd
from pathlib import Path

from utils.loader import (
    load_author_node,
    load_author_edge,
)


author_node_df = load_author_node("./data/author/node.csv")
author_edge_df = load_author_edge("./data/author/edge.csv")

# Get the top-10 community
community_df = pd.read_csv(
    "./CommunityMining/results/author_community_label_propagation.csv"
)
community_df["id"] = community_df["id"].astype(str)

author_node_df = author_node_df.merge(
    community_df[["id", "community"]], on="id", how="left"
)
top_communities = author_node_df["community"].value_counts().head(10).index.tolist()
author_node_df = author_node_df[author_node_df["community"].isin(top_communities)]


filtered_ids = pd.read_json(
    "./CommunityMining/results/author_id.json", orient="records", lines=True
)
filtered_ids_set = set(filtered_ids.values.flatten().astype(str))

# Filter author node and author edge
author_node_df_filtered = author_node_df[author_node_df["id"].isin(filtered_ids_set)]
author_edge_df_filtered = author_edge_df[
    author_edge_df["src"].isin(filtered_ids_set)
    & author_edge_df["dst"].isin(filtered_ids_set)
]


# Save to visualize folder
vis_dir = Path("visualize")
vis_dir.mkdir(parents=True, exist_ok=True)

author_node_path = vis_dir / "author_node.csv"
author_edge_path = vis_dir / "author_edge.csv"

author_node_df_filtered.to_csv(author_node_path, index=False)
author_edge_df_filtered.to_csv(author_edge_path, index=False)
