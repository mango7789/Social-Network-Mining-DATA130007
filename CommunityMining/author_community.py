import igraph as ig
import pandas as pd
from typing import Dict
from pathlib import Path
from utils.logger import logger
from utils.wrapper import timer


@timer
def community_detection_with_filter(
    node: pd.DataFrame, edge: pd.DataFrame, path: Path, algorithm: str, **kwargs: Dict
) -> None:
    """
    Perform community detection on the given node and edge data using the specified algorithm.

    The nodes and edges are expected to be provided as DataFrames, which are generated after pre-processing.
    `kwargs` can include additional parameters for fine-tuning the algorithm, such as weights for edges if applicable.

    This function assigns a community label to each node and saves these labels in a file for future use.

    Parameters:
        - node (pd.DataFrame): DataFrame containing node information, including an "id" column.
        - edge (pd.DataFrame): DataFrame containing edge information, including "src" and "dst" columns.
        - path (Path): Output path to save the results.
        - algorithm (str): Name of the community detection algorithm to use.
        - kwargs (Dict): Additional parameters for fine-tuning.
    """
    # Check for required columns in the DataFrames
    required_node_columns = [
        "id",
        "name",
        "co_authors",
        "papers",
        "num_co_authors",
        "num_papers",
    ]
    required_edge_columns = ["src", "dst", "w"]

    for col in required_node_columns:
        if col not in node.columns:
            raise ValueError(f"Node DataFrame must contain '{col}' column.")

    for col in required_edge_columns:
        if col not in edge.columns:
            raise ValueError(f"Edge DataFrame must contain '{col}' column.")

    # Filter out isolated nodes (assuming authors with no co-authors) and authors with more than 50 co-authors
    node = node[
        (node["num_papers"] > 1)
        & (node["num_co_authors"] > 0)
        & (node["num_co_authors"] <= 50)
    ]

    # Ensure that all edges refer to nodes that exist in the node_data
    valid_edges = edge[edge["src"].isin(node["id"]) & edge["dst"].isin(node["id"])]

    # Filter out edges with missing weights (if applicable)
    valid_edges = valid_edges[valid_edges["w"].notna()]

    # Extract the weights from the valid edges
    weights = valid_edges["w"].tolist()

    # Check that the number of weights matches the number of edges
    if len(weights) != len(valid_edges):
        raise ValueError(
            "The number of weights does not match the number of valid edges."
        )

    # Convert valid edge data to igraph-compatible format
    edges = list(zip(valid_edges["src"], valid_edges["dst"]))

    # Create igraph Graph
    G = ig.Graph()
    # Add all unique node ids from the node DataFrame
    G.add_vertices(node["id"].unique())
    G.add_edges(edges)

    G.vs["name"] = node["id"].tolist()

    # Perform community detection using the specified algorithm
    try:
        if algorithm == "community_fastgreedy":
            communities = G.community_fastgreedy(**kwargs)
            partition = communities.as_clustering()
        elif algorithm == "community_infomap":
            partition = G.community_infomap()
        elif algorithm == "community_leading_eigenvector":
            partition = G.community_leading_eigenvector()
        elif algorithm == "community_label_propagation":
            partition = G.community_label_propagation(weights=weights)
        elif algorithm == "community_multilevel":
            partition = G.community_multilevel()
        elif algorithm == "community_optimal_modularity":
            partition = G.community_optimal_modularity()
        elif algorithm == "community_edge_betweenness":
            communities = G.community_edge_betweenness()
            partition = communities.as_clustering()
        elif algorithm == "community_spinglass":
            partition = G.community_spinglass()
        elif algorithm == "community_walktrap":
            communities = G.community_walktrap()
            partition = communities.as_clustering()
        elif algorithm == "community_leiden":
            partition = G.community_leiden()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    except Exception as e:
        logger.error(f"Error during community detection: {e}")
        return

    # Map the community membership to the node DataFrame
    membership = partition.membership
    vertex_to_community = dict(zip(G.vs["name"], membership))
    node["community"] = node["id"].map(vertex_to_community)
    logger.info(
        f"Type: author, algorithm: {algorithm}, modularity: {partition.modularity}"
    )

    # Save results
    try:
        path = path / f"{algorithm}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        result_df = node[["id", "community"]]
        result_df.to_csv(path, index=False)
        logger.info(f"Community detection results saved to: {path}")
        logger.info("-" * 85)
    except Exception as e:
        logger.error(f"Error saving the results: {e}")

    # Optionally return the community labels for further use
    return node[["id", "community"]]


if __name__ == "__main__":
    from utils import load_author_node, load_author_edge
    from pathlib import Path

    # Load the node and edge data for authors
    node_data = load_author_node("./data/author/node.csv")
    edge_data = load_author_edge("./data/author/edge.csv")

    algorithm = "community_label_propagation"

    # Set output path for the results
    output_path = Path(f"./CommunityMining/results/author")

    # Run community detection with the 'community_walktrap' algorithm
    community_detection_with_filter(
        node_data,
        edge_data,
        output_path,
        algorithm,
    )
