import json
from tqdm import tqdm
import pandas as pd
import igraph as ig


def calculate_community_diameters(community_file, node_file, edge_file, output_file):
    # Load the community and graph data
    community_df = pd.read_csv(community_file)
    paper_node_df = load_paper_node(node_file, skip_isolate=True)
    paper_edge_df = load_paper_edge(edge_file)

    # Merge the community information with the node data
    paper_node_df = paper_node_df.merge(
        community_df[["id", "community"]], on="id", how="left"
    )

    # Create a graph using igraph
    g = ig.Graph()

    # Add vertices (nodes) to the graph
    g.add_vertices(paper_node_df["id"].tolist())

    # Add edges to the graph (assuming paper_edge_df contains 'source' and 'target')
    edges = list(zip(paper_edge_df["src"], paper_edge_df["dst"]))
    g.add_edges(edges)

    # Get the top-10 communities
    top_10_communities = (
        paper_node_df["community"].value_counts().head(10).index.tolist()
    )

    # Function to calculate the diameter of a community using igraph
    def calculate_diameter(community_nodes):
        subgraph = g.subgraph(community_nodes)  # Get subgraph for community
        if len(subgraph.vs) == 1:
            return 0  # A single node has a diameter of 0

        # Calculate the diameter using igraph's built-in function
        try:
            return subgraph.diameter()
        except ig.GraphError:
            return float("inf")

    # Calculate the diameters for the top-10 communities
    community_diameters = {}
    for community in tqdm(top_10_communities):
        community_nodes = paper_node_df[paper_node_df["community"] == community][
            "id"
        ].tolist()
        diameter = calculate_diameter(community_nodes)
        community_diameters[community] = diameter

    # Save the diameters to a JSON file
    with open(output_file, "w") as json_file:
        json.dump(community_diameters, json_file, indent=4)


if __name__ == "__main__":
    from utils import load_paper_node, load_paper_edge

    calculate_community_diameters(
        community_file="./CommunityMining/results/louvain.csv",
        node_file="./data/paper/node.csv",
        edge_file="./data/paper/edge.csv",
        output_file="./CentralityMeasure/results/diameter.json",
    )
