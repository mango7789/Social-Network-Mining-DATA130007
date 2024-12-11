import gc
import pandas as pd
from tqdm import tqdm
from typing import Final, List
from itertools import chain, combinations
from collections import defaultdict
from .logger import logger
from .wrapper import timer


def _group_records(lines: List[str]) -> List[List[str]]:
    """
    Groups lines into records, ensuring each group corresponds to a complete paper object.
    """
    records = []
    current_record = []

    for line in tqdm(lines, desc="Grouping records..."):
        if line.strip() == "":
            continue
        if line.startswith("#*") and current_record:
            # Start of a new record, save the current one
            records.append(current_record)
            current_record = []
        current_record.append(line)

    # Add the last record
    if current_record:
        records.append(current_record)

    del current_record
    gc.collect()

    return records


def _process_records_to_dataframe(records: List[List[str]]) -> pd.DataFrame:
    """
    Process records to extract paper objects and convert them to a DataFrame.
    """
    data = []
    with tqdm(total=len(records), desc="Creating dataframes...") as pbar:
        for record in records:
            vertex_dict = {}
            for line in record:
                line = line.strip()
                if line.startswith("#*"):
                    vertex_dict["title"] = line[2:]
                elif line.startswith("#@"):
                    vertex_dict["authors"] = line[2:]
                elif line.startswith("#t"):
                    vertex_dict["year"] = int(line[2:]) if line[2:] else ""
                elif line.startswith("#c"):
                    vertex_dict["venue"] = line[2:]
                elif line.startswith("#index"):
                    vertex_dict["index"] = line[6:]
                elif line.startswith("#%"):
                    if "references" not in vertex_dict:
                        vertex_dict["references"] = []
                    vertex_dict["references"].append(line[2:])

            # Handle missing fields
            for str_name in ["title", "year", "venue", "authors"]:
                if str_name not in vertex_dict:
                    vertex_dict[str_name] = ""
            for lst_name in ["references"]:
                if lst_name not in vertex_dict:
                    vertex_dict[lst_name] = []

            # Append to data
            data.append(
                {
                    "id": vertex_dict["index"],
                    "title": vertex_dict["title"],
                    "authors": vertex_dict["authors"].replace(", ", "#"),
                    "year": vertex_dict["year"],
                    "venue": vertex_dict["venue"],
                    "references": "#".join(vertex_dict["references"]),
                }
            )

            pbar.update(1)

    return pd.DataFrame(data)


def _get_dataframe(data_path: str) -> pd.DataFrame:
    """
    Get dataframe from the dataset in given `data_path`.
    """
    with open(data_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Group lines into records
    records = _group_records(lines)

    # Process all records into a single DataFrame
    combined_data = _process_records_to_dataframe(records)

    del lines
    del records
    gc.collect()

    return combined_data


@timer
def _save_paper_chunk(df: pd.DataFrame, paper_node: str, paper_edge: str):
    logger.info("Start saving information of the papers...")
    paper_node.parent.mkdir(parents=True, exist_ok=True)

    # Split the references
    df["ref_list"] = df["references"].str.split("#")
    df["ref_list"] = df["ref_list"].apply(
        lambda x: x if isinstance(x, list) and x != [""] else []
    )

    # Out degree, number of references
    df["out_d"] = df["ref_list"].apply(len)

    # In degree, number of being citated
    in_degree = defaultdict(int)
    edge_list = []

    for ref_list, paper_id in tqdm(
        zip(df["ref_list"], df["id"]), desc="Calculating paper infos", total=len(df)
    ):
        for reference in ref_list:
            edge_list.append((paper_id, reference))
            in_degree[reference] += 1

    df["in_d"] = df["id"].map(in_degree).fillna(0).astype(int)
    df.drop(columns=["references", "ref_list"], inplace=True)
    df.to_csv(paper_node, index=False)

    # Save the edges of references in papers
    edge_list = [{"src": source, "dst": target} for (source, target) in edge_list]
    edges_df = pd.DataFrame(edge_list)
    edges_df.to_csv(paper_edge, index=False)

    logger.info(
        f"There are total {len(df)} nodes and {len(edges_df)} edges in \033[34mpaper\033[0m."
    )
    logger.info(
        f"Successfully save the information of papers to {paper_node} and {paper_edge}!"
    )

    del in_degree
    del edge_list
    del edges_df
    gc.collect()


@timer
def _save_author_chunk(df: pd.DataFrame, author_node: str, author_edge: str):
    logger.info("Start saving information of the authors...")
    author_node.parent.mkdir(parents=True, exist_ok=True)

    # Assign unique IDs to authors
    df["authors"] = df["authors"].str.split("#")
    authors = set(chain.from_iterable(df["authors"]))
    author_to_id = {author: idx for idx, author in enumerate(sorted(authors), start=1)}
    id_to_author = {v: k for k, v in author_to_id.items()}
    df["authors"] = df["authors"].apply(
        lambda x: [author_to_id[author] for author in x]
    )

    # Create a co-author mapping and paper list for each author
    lists = {
        author_id: {"co-authors": set(), "papers": set()}
        for author_id in author_to_id.values()
    }
    # Edge dictionary to store weights
    edges = defaultdict(int)

    for authors, paper_id in tqdm(
        zip(df["authors"], df["id"]), desc="Creating author infos", total=len(df)
    ):
        for author_id in authors:
            lists[author_id]["papers"].add(paper_id)
            lists[author_id]["co-authors"].update(set(authors) - {author_id})

        for author1, author2 in combinations(authors, 2):
            edge = tuple(sorted((author1, author2)))
            edges[edge] += 1

    # Convert author info to a DataFrame
    authors_list = []
    for author_id, data in lists.items():
        authors_list.append(
            {
                "id": author_id,
                "name": id_to_author[author_id],
                "co-authors": "#".join(map(str, sorted(data["co-authors"]))),
                "papers": "#".join(data["papers"]),
            }
        )

    # Save the author lists
    authors_df = pd.DataFrame(authors_list)
    authors_df.to_csv(author_node, index=False)

    # Save the author edges
    edges_list = [
        {"src": source, "dst": target, "w": weight}
        for (source, target), weight in edges.items()
    ]
    edges_df = pd.DataFrame(edges_list)
    edges_df.to_csv(author_edge, index=False)

    logger.info(
        f"There are total {len(authors_df)} nodes and {len(edges_df)} edges in \033[34mauthors\033[0m."
    )
    logger.info(
        f"Successfully save the information of authors to {author_node} and {author_edge}!"
    )

    df["authors"] = df["authors"].apply(
        lambda x: "" if x == [1] else "#".join(map(str, x))
    )

    del edges_df
    del edges_list
    gc.collect()


@timer
def save_records_to_csv(
    data_path: str,
    paper_node: str,
    paper_edge: str,
    author_node: str,
    author_edge: str,
) -> None:
    """
    Load and preprocess the dataset, then save as csv files in a single process.
    The csv files include node and edge infos of paper and author, respectively.
    """
    # Process all records into a single DataFrame
    combined_data = _get_dataframe(data_path)
    # combined_data = load_records_from_csv(paper_node)

    _save_author_chunk(combined_data, author_node, author_edge)
    _save_paper_chunk(combined_data, paper_node, paper_edge)

    gc.collect()

    return
