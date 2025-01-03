import pandas as pd
from pathlib import Path
import igraph as ig
from tqdm import tqdm
from utils.logger import logger


def calculate_centrality_and_statistics(
    node_data: pd.DataFrame,
    edge_data: pd.DataFrame,
    output_path: Path,
):
    """
    Calculate centrality measures for the nodes and compute graph statistics including degree distribution,
    shortest path, radius, etc.

    Parameters:
        - node_data (pd.DataFrame): Node data (including 'id' column)
        - edge_data (pd.DataFrame): Edge data (including 'src', 'dst' columns)
        - output_path (Path): Path to save the results
    """
    # Step 1: Build the graph
    edges = list(zip(edge_data["src"], edge_data["dst"]))
    G = ig.Graph()
    G.add_vertices(node_data["id"].unique())
    G.add_edges(edges)

    # Step 2: Calculate centrality measures
    centrality_dict = {}

    # Calculate degree centrality with progress bar
    degree_centrality = []
    for node in tqdm(node_data["id"], desc="Calculating Degree Centrality..."):
        degree_centrality.append(G.degree(node))
    centrality_dict["degree_centrality"] = degree_centrality

    # Calculate pagerank centrality
    pagerank_centrality = G.pagerank()
    centrality_dict["pagerank_centrality"] = pagerank_centrality

    # Step 3: Save results to files
    output_path.mkdir(parents=True, exist_ok=True)

    # Save centrality measures to CSV
    centrality_df = pd.DataFrame(
        {
            "id": node_data["id"],
            "degree_centrality": centrality_dict["degree_centrality"],
            "pagerank_centrality": centrality_dict["pagerank_centrality"],
        }
    )
    centrality_df.to_csv(output_path / "centrality_measures.csv", index=False)

    logger.info(f"Results saved to: {output_path}")


if __name__ == "__main__":
    # Define file paths
    from utils import load_paper_node, load_paper_edge

    node_data = load_paper_node("./data/paper/node.csv", skip_isolate=True)
    edge_data = load_paper_edge("./data/paper/edge.csv")

    output_path = Path("./CentralityMeasure/results")
    # Calculate centrality measures and statistics
    calculate_centrality_and_statistics(node_data, edge_data, output_path)
