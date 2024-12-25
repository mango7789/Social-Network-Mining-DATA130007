def extract_author_features(src_author, dst_author, nodes_df, edges_df):
    """
    Efficiently extract features for predicting a link between two authors (src_author and dst_author).
    Features include co-authorship count, year similarity, venue similarity, and common co-authors.

    Parameters:
    - src_author: The ID of the source author.
    - dst_author: The ID of the destination author.
    - nodes_df: DataFrame containing paper information (with authors, year, venue, and start/end).
    - edges_df: DataFrame containing edge information between authors (src, dst).

    Returns:
    - A list of features: [coauthorship_count, jaccard_index, same_year, same_venue, common_coauthors]
    """

    # Find the rows in nodes_df corresponding to src_author and dst_author
    src_data = nodes_df[nodes_df["authors"].apply(lambda x: src_author in x)]
    dst_data = nodes_df[nodes_df["authors"].apply(lambda x: dst_author in x)]

    # Initialize the set to store paper IDs for both authors
    src_paper_ids = set()
    dst_paper_ids = set()

    # Collect paper IDs for src_author using start and end ranges from nodes_df
    for _, row in src_data.iterrows():
        start, end = row["start"], row["end"]
        edges = edges_df[start:end]  # Use the paper ID range for efficient edge lookup
        src_paper_ids.update(edges["dst"])

    # Collect paper IDs for dst_author using start and end ranges from nodes_df
    for _, row in dst_data.iterrows():
        start, end = row["start"], row["end"]
        edges = edges_df[start:end]  # Use the paper ID range for efficient edge lookup
        dst_paper_ids.update(edges["dst"])

    # Co-authorship count: count the number of shared papers between src and dst authors
    common_papers = src_paper_ids.intersection(dst_paper_ids)
    coauthorship_count = len(common_papers)

    # Calculate Jaccard Index for authorship similarity (using paper ids)
    jaccard_index = (
        len(common_papers)
        / (len(src_paper_ids) + len(dst_paper_ids) - len(common_papers))
        if (len(src_paper_ids) + len(dst_paper_ids) - len(common_papers)) != 0
        else 0
    )

    # Year similarity: Check if authors have collaborated in the same years
    common_years = set(src_data["year"]).intersection(dst_data["year"])
    same_year = 1 if common_years else 0

    # Venue similarity: Check if authors have collaborated in the same venues
    common_venues = set(src_data["venue"]).intersection(dst_data["venue"])
    same_venue = 1 if common_venues else 0

    # Common co-authors: Count how many co-authors both authors have worked with in common
    src_coauthors = set()
    dst_coauthors = set()
    for paper_id in src_paper_ids:
        paper_authors = nodes_df[nodes_df["id"] == paper_id]["authors"].values[0]
        src_coauthors.update(paper_authors)

    for paper_id in dst_paper_ids:
        paper_authors = nodes_df[nodes_df["id"] == paper_id]["authors"].values[0]
        dst_coauthors.update(paper_authors)

    # Remove the src_author and dst_author from their own co-authors set
    src_coauthors.discard(src_author)
    dst_coauthors.discard(dst_author)

    common_coauthors = len(src_coauthors.intersection(dst_coauthors))

    # Return the feature vector
    features = [
        coauthorship_count,
        jaccard_index,
        same_year,
        same_venue,
        common_coauthors,
    ]
    return features
