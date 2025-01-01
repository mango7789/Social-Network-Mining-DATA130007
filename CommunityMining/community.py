import igraph as ig
import pandas as pd
from enum import Enum
from typing import Dict
from pathlib import Path

from utils.logger import logger
from utils.wrapper import timer


class Algorithm(Enum):
    FAST_GREEDY = "community_fastgreedy"
    INFOMAP = "community_infomap"
    LEADING_EIGENVECTOR = "community_leading_eigenvector"
    LABEL_PROPAGATION = "community_label_propagation"
    MULTILEVEL = "community_multilevel"
    OPTIMAL_MODULARITY = "community_optimal_modularity"
    EDGE_BETWEENNESS = "community_edge_betweenness"
    SPINGLASS = "community_spinglass"
    WALKTRAP = "community_walktrap"
    LEIDEN = "community_leiden"


@timer
def community_detection(
    node: pd.DataFrame,
    edge: pd.DataFrame,
    path: Path,
    algorithm: Algorithm,
    **kwargs: Dict,
) -> None:
    """
    Perform community detection on the given node and edge data using the specified algorithm.
    The nodes and edges are expected to be provided as DataFrames, which are generated after pre - processing.
    `kwargs` can include additional parameters if needed.

    This function assigns a community label to each node and saves these labels in a file for future use.

    Parameters:
        - node (pd.DataFrame): DataFrame containing node information, including an "id" column.
        - edge (pd.DataFrame): DataFrame containing edge information, including "src" and "dst" columns.
        - path (Path): Output path to save the results.
        - algorithm (str): Name of the community detection algorithm to use.
        - kwargs (Dict): Additional parameters for fine - tuning.
    """
    # Convert edge data to igraph-compatible format, remove self-loop
    edges = [(src, dst) for src, dst in zip(edge["src"], edge["dst"]) if src != dst]

    # Create igraph Graph
    G = ig.Graph()
    G.add_vertices(node["id"].unique())
    G.add_edges(edges)

    G.vs["name"] = node["id"].tolist()
    G = G.simplify(loops=True, combine_edges=None)
    logger.info("The graph is successfully simplified!")

    # Perform community detection using the specified algorithm
    try:
        if algorithm == Algorithm.FAST_GREEDY:
            communities = G.community_fastgreedy()
            partition = communities.as_clustering()
        elif algorithm == Algorithm.INFOMAP:
            partition = G.community_infomap()
        elif algorithm == Algorithm.LEADING_EIGENVECTOR:
            partition = G.community_leading_eigenvector()
        elif algorithm == Algorithm.LABEL_PROPAGATION:
            partition = G.community_label_propagation()
        elif algorithm == Algorithm.MULTILEVEL:
            partition = G.community_multilevel()
        elif algorithm == Algorithm.OPTIMAL_MODULARITY:
            partition = G.community_optimal_modularity()
        elif algorithm == Algorithm.EDGE_BETWEENNESS:
            communities = G.community_edge_betweenness()
            partition = communities.as_clustering()
        elif algorithm == Algorithm.SPINGLASS:
            partition = G.community_spinglass()
        elif algorithm == Algorithm.WALKTRAP:
            communities = G.community_walktrap()
            partition = communities.as_clustering()
        elif algorithm == Algorithm.LEIDEN:
            partition = G.community_leiden()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    except Exception as e:
        logger.info(f"Error during community detection: {e}")
        return

    # Map the community membership to the node DataFrame
    membership = partition.membership
    vertex_to_community = dict(zip(G.vs["name"], membership))
    node["community"] = node["id"].map(vertex_to_community)

    # Save results
    path.parent.mkdir(parents=True, exist_ok=True)
    result_df = node[["id", "community"]]
    result_df.to_csv(path, index=False)
    logger.info(f"Community detection results saved to: {path}")

    logger.info(f"Community detection completed and results saved to {path}")
    logger.info(f"Modularity of algorithm {algorithm.value}: {partition.modularity}")


if __name__ == "__main__":
    import pandas as pd
    from pathlib import Path
    from utils import load_paper_node, load_paper_edge

    algorithm = Algorithm.LABEL_PROPAGATION
    # algorithm = Algorithm.MULTILEVEL

    node_data = load_paper_node("./data/paper/node.csv", skip_isolate=True)
    edge_data = load_paper_edge("./data/paper/edge.csv")
    output_path = Path(f"./CommunityMining/results/{algorithm.value}.csv")

    community_detection(
        node_data,
        edge_data,
        output_path,
        algorithm,
    )
