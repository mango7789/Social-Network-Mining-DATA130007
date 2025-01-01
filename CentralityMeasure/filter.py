import pandas as pd

# Example data
data = pd.read_csv("./results/centrality_measures.csv")

# Create a DataFrame
df = pd.DataFrame(data)

# Filter by degree and pagerank conditions
# Assuming "first 10,000" implies sorting by the columns and taking top entries
df_filtered = df.nlargest(10000, "degree_centrality").merge(
    df.nlargest(10000, "pagerank_centrality"),
    on=["id", "degree_centrality", "pagerank_centrality"],
)

print(df_filtered)
