import pandas as pd
from pathlib import Path
import json

from utils.loader import (
    load_paper_node,
    load_author_node,
    load_author_edge,
    load_map_dict,
)


author_node_df = load_author_node("./data/author/node.csv")
author_edge_df = load_author_edge("./data/author/edge.csv")
venue_map = load_map_dict("./data/venue/map.json")
title_map = load_map_dict("./data/paper/map.json")

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

# Get the set of all papers across all authors
all_papers_set = set()

# Iterate through the dataframe to collect papers from all authors
for papers_list in author_node_df["papers"]:
    all_papers_set.update(papers_list)

all_papers_list = list(all_papers_set)

# Save the list of papers as a JSON file
output_path = "./vis/author_paper.csv"
with open(output_path, "w") as json_file:
    json.dump(all_papers_list, json_file)


# Save to vis folder
vis_dir = Path("vis")
vis_dir.mkdir(parents=True, exist_ok=True)

author_node_path = vis_dir / "author_node.csv"
author_edge_path = vis_dir / "author_edge.csv"

author_node_df_filtered.to_csv(author_node_path, index=False)
author_edge_df_filtered.to_csv(author_edge_path, index=False)

# Paper list
paper_node_df = load_paper_node("./data/paper/node.csv", skip_isolate=True)


paper_node_df_filtered = paper_node_df[paper_node_df["id"].isin(all_papers_list)]
paper_node_df_filtered.loc[:, "title"] = paper_node_df_filtered["id"].map(title_map)
paper_node_df_filtered.loc[:, "venue"] = paper_node_df_filtered["venue"].map(venue_map)
columns_to_save = [
    "id",
    "year",
    "venue",
    "out_d",
    "in_d",
    "title",
]
paper_node_df_filtered = paper_node_df_filtered[columns_to_save]
paper_node_path = vis_dir / "author_paper.csv"

paper_node_df_filtered.to_csv(paper_node_path, index=False)
