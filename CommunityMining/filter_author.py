import pandas as pd

# Sample data
df = pd.read_csv("./results/author_community_label_propagation.csv")

# Count the occurrences of each community
community_counts = df["community"].value_counts().head(10)  # Get top 10 communities

# Display the result
print(community_counts)
