import pandas as pd
import json

# Load the data
community_data = pd.read_csv("./results/paper/louvain.csv")
pagerank_data = pd.read_csv("../CentralityMeasure/results/centrality_measures.csv")

merged_data = pd.merge(community_data, pagerank_data, on="id")

# Count the number of nodes in each community and get the top 10 largest communities
community_counts = merged_data["community"].value_counts().head(10)
largest_communities = community_counts.index

# List to store selected node IDs
selected_ids = []

# Iterate over each of the largest 10 communities
for community in largest_communities:
    # Filter nodes for the community
    community_nodes = merged_data[merged_data["community"] == community]

    # Sort by pagerank_centrality and select the top 50 nodes
    top_nodes = community_nodes.nlargest(50, "pagerank_centrality")

    # Append the selected node IDs to the list
    selected_ids.extend(top_nodes["id"].tolist())
# Save the result as a JSON file
with open("./results/paper_id.json", "w") as json_file:
    json.dump(selected_ids, json_file)

# Output the result
print(len(selected_ids))
