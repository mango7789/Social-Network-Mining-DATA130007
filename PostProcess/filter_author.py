import json
import pandas as pd


def extract_top_authors_by_community(
    author_node_df,
    community_file="./CommunityMining/results/author/community_label_propagation.csv",
    top_n_communities=10,
    top_authors_per_community=50,
) -> list[str]:
    """
    Extracts the top authors by number of co-authors from the top N communities.

    Args:
        community_file (str): Path to the community CSV file.
        author_node_file (str): Path to the author node CSV file.
        output_file (str): Path to save the resulting JSON file.
        top_n_communities (int): Number of top communities to consider.
        top_authors_per_community (int): Number of top authors to extract per community.

    Returns:
        str: Path to the output JSON file.
    """
    # Load the data
    community_df = pd.read_csv(community_file)

    # Get the top N communities with the most nodes
    top_communities = (
        community_df["community"].value_counts().head(top_n_communities).index.tolist()
    )

    ids = []

    for community in top_communities:
        # Filter the authors in the specific community
        community_authors = community_df[community_df["community"] == community]

        # Merge with the author_node_df to get 'num_co_authors'
        merged_df = pd.merge(
            community_authors, author_node_df, left_on="id", right_on="id", how="inner"
        )

        # Sort the authors by 'num_co_authors' and get the top authors
        top_authors = merged_df.nlargest(top_authors_per_community, "num_co_authors")
        top_authors["id"] = top_authors["id"].astype(str)

        # Add to the list of IDs
        ids.extend(top_authors["id"].tolist())

    return ids


if __name__ == "__main__":
    extract_top_authors_by_community()
