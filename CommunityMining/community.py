import igraph as ig
import pandas as pd
from typing import Dict
from pathlib import Path


def community_detection(node: pd.DataFrame, edge: pd.DataFrame, path: Path, algorithm: str, **kwargs: Dict) -> None:
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
    # Convert edge data to igraph-compatible format
    edges = list(zip(edge["src"], edge["dst"]))

    # Create igraph Graph
    G = ig.Graph()
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
            partition = G.community_label_propagation()
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
        print(f"Error during community detection: {e}")
        return

    # Map the community membership to the node DataFrame
    membership = partition.membership
    vertex_to_community = dict(zip(G.vs["name"], membership))
    node["community"] = node["id"].map(vertex_to_community)

    # Save results
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        result_df = node[["id", "community"]]
        result_df.to_csv(path, index=False)
        print(f"Community detection results saved to: {path}")
    except Exception as e:
        print(f"Error saving the results: {e}")


if __name__ == "__main__":
    from utils import load_paper_node, load_paper_edge
    from pathlib import Path
    import pandas as pd

    node_data = load_paper_node("./test/paper/node.csv")
    edge_data = load_paper_edge("./test/paper/edge.csv")
    output_path = Path("./CommunityMining/result/output.csv")

    community_detection(node_data, edge_data, output_path,
                        "community_leading_eigenvector", weights=edge_data.get("weight"))
