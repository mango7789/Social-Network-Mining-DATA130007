import pandas as pd


VIS_NUM = 10000


if __name__ == "__main__":

    data = pd.read_csv("./results/centrality_measures.csv")
    df = pd.DataFrame(data)

    # Filter by degree and pagerank conditions
    df_filtered = df.nlargest(VIS_NUM, "degree_centrality").merge(
        df.nlargest(VIS_NUM, "pagerank_centrality"),
        on=["id", "degree_centrality", "pagerank_centrality"],
    )

    output_file = "./results/id.json"
    df_filtered["id"].to_json(output_file, orient="records", lines=True)

    print(f"Filtered IDs saved to {output_file}")
