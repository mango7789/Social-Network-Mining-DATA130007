import pandas as pd
from pathlib import Path
import json

from utils.loader import (
    load_paper_node,
    load_paper_edge,
    load_author_node,
    load_author_edge,
    load_map_dict,
)


paper_node_df = load_paper_node("./data/paper/node.csv", skip_isolate=True)
paper_edge_df = load_paper_edge("./data/paper/edge.csv")
venue_map = load_map_dict("./data/venue/map.json")
title_map = load_map_dict("./data/paper/map.json")

# Get the top-10 community
community_df = pd.read_csv("./CommunityMining/results/louvain.csv")
paper_node_df = paper_node_df.merge(
    community_df[["id", "community"]], on="id", how="left"
)
top_communities = paper_node_df["community"].value_counts().head(10).index.tolist()
paper_node_df = paper_node_df[paper_node_df["community"].isin(top_communities)]

centrality_df = pd.read_csv("./CentralityMeasure/results/centrality_measures.csv")
paper_node_df = paper_node_df.merge(
    centrality_df[["id", "pagerank_centrality"]], on="id", how="left"
)

# Calculate the average 'in_d' for each community
average_in_d = paper_node_df.groupby("community")["in_d"].mean().reset_index()
sorted_average_in_d = average_in_d.sort_values(by="in_d", ascending=False)
average_in_d_dict = sorted_average_in_d.to_dict(orient="records")
with open("./vis/citation.json", "w") as f:
    json.dump(average_in_d_dict, f, indent=4)

# Calculate the average `centrality` for each community
average_centrality = (
    paper_node_df.groupby("community")["pagerank_centrality"].mean().reset_index()
)
sorted_average_centrality = average_centrality.sort_values(
    by="pagerank_centrality", ascending=False
)
average_centrality_dict = sorted_average_centrality.to_dict(orient="records")
with open("./vis/centrality.json", "w") as f:
    json.dump(average_centrality_dict, f, indent=4)


# Degree
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

degree_path = "./vis/degree.json"
with open(degree_path, "w") as f:
    json.dump(degree_counts, f, indent=4)

# Community proportions
total_nodes = paper_node_df.shape[0]
community_counts = paper_node_df["community"].value_counts()
community_proportions_dict = community_counts.to_dict()
proport_path = "./vis/counts.json"
with open(proport_path, "w") as f:
    json.dump(community_proportions_dict, f, indent=4)


filtered_ids = pd.read_json(
    "./CommunityMining/results/id.json", orient="records", lines=True
)
filtered_ids_set = set(filtered_ids.values.flatten())

# Filter paper node and paper edge
paper_node_df_filtered = paper_node_df[paper_node_df["id"].isin(filtered_ids_set)]
paper_edge_df_filtered = paper_edge_df[
    paper_edge_df["src"].isin(filtered_ids_set)
    & paper_edge_df["dst"].isin(filtered_ids_set)
]

# Readd columns
paper_node_df_filtered.loc[:, "title"] = paper_node_df_filtered["id"].map(title_map)
paper_node_df_filtered.loc[:, "venue"] = paper_node_df_filtered["venue"].map(venue_map)

# paper_node_df_filtered = paper_node_df_filtered.merge(
#     community_df[["id", "community"]], on="id", how="left"
# )

# paper_node_df_filtered = paper_node_df_filtered.merge(
#     centrality_df[["id", "pagerank_centrality"]], on="id", how="left"
# )

# Drop other columns
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


# Save to vis folder
vis_dir = Path("vis")
vis_dir.mkdir(parents=True, exist_ok=True)

paper_node_path = vis_dir / "paper_node.csv"
paper_edge_path = vis_dir / "paper_edge.csv"

paper_node_df_filtered.to_csv(paper_node_path, index=False)
paper_edge_df_filtered.to_csv(paper_edge_path, index=False)
