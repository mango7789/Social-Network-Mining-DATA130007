import pandas as pd
from typing import Dict
import networkx as nx
from community import community_louvain
from tqdm import tqdm
from pathlib import Path


def louvain(node: pd.DataFrame, edge: pd.DataFrame, path: Path, **kwargs: Dict) -> None:
    """
    Perform community detection on the given node and edge data. The nodes and edges are expected
    to be provided as DataFrames, which are generated after pre-processing. `kwargs` can include
    additional hyperparameters to fine-tune the algorithm.

    This function should also assign a community label to each node and save these labels in a static
    file for future use. Make sure to update the `config.yaml` file once the function is complete.

    NOTE: For large graphs, it is recommended to use `igraph` over `networkx` for improved performance.

    >>> # Example usage
    >>> louvain(paper_node, paper_edge)
    """
    node = node[node["single"] != True]

    G = nx.DiGraph()

    for index in tqdm(node.index, total=len(node), desc="Adding nodes to graph"):
        row = node.loc[index]
        G.add_node(row["id"])

    for index in tqdm(edge.index, total=len(edge), desc="Adding edges to graph"):
        row = edge.loc[index]
        G.add_edge(row["src"], row["dst"])

    partition = community_louvain.best_partition(G.to_undirected())

    node["community"] = node["id"].map(partition)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    result_df = node[["id", "community"]]
    result_df.to_csv(output_path, index=False)

    print(f"Community detection completed and results saved to {output_path}")


if __name__ == "__main__":
    node_data = pd.read_csv("../test/paper/node.csv", sep=",", low_memory=False)
    edge_data = pd.read_csv("../test/paper/edge.csv", sep=",", low_memory=False)
    louvain(node_data, edge_data)
