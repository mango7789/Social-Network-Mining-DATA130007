import pandas as pd
import igraph as ig
import leidenalg as la
from typing import Dict
from tqdm import tqdm
from pathlib import Path

from utils.logger import logger
from utils.wrapper import timer


@timer
def louvain_ig(
    node: pd.DataFrame, edge: pd.DataFrame, path: Path, **kwargs: Dict
) -> None:
    """
    Perform community detection on the given node and edge data using the Leiden algorithm for improved performance.
    The nodes and edges are expected to be provided as DataFrames, which are generated after pre-processing.
    `kwargs` can include additional hyperparameters to fine-tune the algorithm.

    This function assigns a community label to each node and saves these labels in a static file for future use.

    Parameters:
        - node (pd.DataFrame): DataFrame containing node information, including an "id" column.
        - edge (pd.DataFrame): DataFrame containing edge information, including "src" and "dst" columns.
        - path (Path): Output path to save the results.
        - kwargs (Dict): Additional parameters for fine-tuning.

    NOTE: The Leiden algorithm is used here for its efficiency on large graphs.

    Example usage:
    >>> louvain_ig(paper_node, paper_edge, output_path)
    """
    # Convert edge data to igraph-compatible format
    edges = [(src, dst) for src, dst in zip(edge["src"], edge["dst"]) if src != dst]

    # Create igraph Graph
    G = ig.Graph()
    G.add_vertices(node["id"].unique())
    G.add_edges(edges)

    G.vs["name"] = node["id"].tolist()
    G = G.simplify(loops=True, combine_edges=None)
    logger.info("The graph is successfully simplified!")

    # Perform community detection using Leiden algorithm
    partition = la.find_partition(G, la.ModularityVertexPartition)

    # Map the community membership to the node DataFrame
    membership = partition.membership
    vertex_to_community = dict(zip(G.vs["name"], membership))
    node["community"] = node["id"].map(vertex_to_community)

    # Save results
    path.parent.mkdir(parents=True, exist_ok=True)
    result_df = node[["id", "community"]]
    result_df.to_csv(path, index=False)

    logger.info(f"Community detection completed and results saved to {path}")
    logger.info(f"Modularity: {partition.modularity}")


if __name__ == "__main__":
    from utils import load_paper_node, load_paper_edge

    node_data = load_paper_node("./data/paper/node.csv", skip_isolate=True)
    edge_data = load_paper_edge("./data/paper/edge.csv")
    output_path = Path("./CommunityMining/results/louvain.csv")
    louvain_ig(node_data, edge_data, output_path)
