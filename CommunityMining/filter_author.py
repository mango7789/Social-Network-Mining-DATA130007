import pandas as pd
import json

# Load the data
community_df = pd.read_csv("./results/author_community_label_propagation.csv")
author_node_df = pd.read_csv("../data/author/node.csv")

# Get the top 10 communities with the most nodes
top_communities = community_df["community"].value_counts().head(10).index.tolist()


ids = []

for community in top_communities:
    # Filter the authors in the specific community
    community_authors = community_df[community_df["community"] == community]

    # Merge with the author_node_df to get 'num_co_authors'
    merged_df = pd.merge(
        community_authors, author_node_df, left_on="id", right_on="id", how="inner"
    )

    # Sort the authors by 'num_co_authors' and get the top 50
    top_50_authors = merged_df.nlargest(50, "num_co_authors")
    top_50_authors["id"] = top_50_authors["id"].astype(str)

    # Save the top 50 authors for this community
    ids.extend(top_50_authors["id"].tolist())

# Step 3: Save the result to a JSON file
with open("./results/author_id.json", "w") as f:
    json.dump(ids, f)
