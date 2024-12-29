import pandas as pd
import networkx as nx
from community import community_louvain
from typing import Dict
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
    G = nx.DiGraph()

    for index in tqdm(node.index, total=len(node), desc="Adding nodes to graph"):
        row = node.loc[index]
        G.add_node(row["id"])

    for index in tqdm(edge.index, total=len(edge), desc="Adding edges to graph"):
        row = edge.loc[index]
        G.add_edge(row["src"], row["dst"])

    partition = community_louvain.best_partition(G.to_undirected())
    modularity = community_louvain.modularity(partition, G.to_undirected())

    node["community"] = node["id"].map(partition)

    path.parent.mkdir(parents=True, exist_ok=True)
    node.to_csv(path, index=False)

    result_df = node[["id", "community"]]
    result_df.to_csv(path, index=False)

    print(f"Community detection completed and results saved to {path}")
    print(f"Modularity: {modularity}")


if __name__ == "__main__":
    from utils import load_paper_node, load_paper_edge

    node_data = load_paper_node("./test/paper/node.csv")
    edge_data = load_paper_edge("./test/paper/edge.csv")
    output_path = Path("./CommunityMining/result/community_output.csv")
    louvain(node_data, edge_data, output_path)
