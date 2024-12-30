import gc
import json
import pandas as pd
from tqdm import tqdm
from typing import Final, List
from itertools import chain, combinations
from collections import defaultdict
from pathlib import Path
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


def _get_dataframe(data_path: Path) -> pd.DataFrame:
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
def _save_author_chunk(df: pd.DataFrame, author_node: Path, author_edge: Path):
    logger.info("Start saving information of the authors...")
    author_node.parent.mkdir(parents=True, exist_ok=True)

    # Assign unique IDs to authors
    df["authors"] = df["authors"].str.split("#")
    authors = set(chain.from_iterable(df["authors"]))
    author_to_id = {
        author: idx
        for idx, author in tqdm(
            enumerate(sorted(authors), start=1),
            desc="Building author index...",
            total=len(authors),
        )
    }
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
        zip(df["authors"], df["id"]), desc="Creating author infos...", total=len(df)
    ):
        for author_id in authors:
            lists[author_id]["papers"].add(paper_id)
            lists[author_id]["co-authors"].update(set(authors) - {author_id})

        for author1, author2 in combinations(authors, 2):
            edge = tuple(sorted((author1, author2)))
            edges[edge] += 1

    # Convert author info to a DataFrame
    authors_list = []
    for author_id, data in tqdm(
        lists.items(), desc="Converting infos to dataframe...", total=len(lists.items())
    ):
        co_authors_list = list(map(str, sorted(data["co-authors"])))
        authors_list.append(
            {
                "id": author_id,
                "name": id_to_author[author_id],
                "co_authors": "#".join(co_authors_list),
                "papers": "#".join(data["papers"]),
                "num_co_authors": len(co_authors_list),
                "num_papers": len(data["papers"]),
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

    del edges_df
    del edges_list
    gc.collect()


@timer
def _build_venue_index(df: pd.DataFrame, venue_map: Path):
    logger.info("Start building the index of venue...")
    venue_map.parent.mkdir(parents=True, exist_ok=True)

    venues = set(df["venue"].unique())
    venue_to_id = {venue: idx for idx, venue in enumerate(sorted(venues), start=1)}
    id_to_venue = {v: k for k, v in venue_to_id.items()}
    df["venue"] = df["venue"].map(venue_to_id)

    with open(venue_map, "w") as f:
        json.dump(id_to_venue, f, indent=4)

    logger.info(f"Successfully save the mapping of 'id: venue' to {venue_map}!")


@timer
def _save_paper_chunk(
    df: pd.DataFrame,
    paper_map: Path,
    citation: Path,
    paper_node: Path,
    paper_edge: Path,
):
    logger.info("Start saving information of the papers...")
    paper_node.parent.mkdir(parents=True, exist_ok=True)

    # Split the references
    df["ref_list"] = df["references"].str.split("#")
    df["ref_list"] = df["ref_list"].apply(
        lambda x: x if isinstance(x, list) and x != [""] else []
    )

    # Out degree, number of references
    df["out_d"] = df["ref_list"].apply(len)

    # Save the mapping of id: (title, start, end)
    start = 1

    def calculate_range(row):
        nonlocal start
        row_start = start
        row_end = start + row["out_d"]
        start = row_end
        return {"title": row["title"], "start": row_start, "end": row_end}

    tqdm.pandas(desc="Building paper mapping...", total=len(df))
    df["paper_mapping"] = df.progress_apply(calculate_range, axis=1)

    # Extract title and store start/end in original df
    df["title"] = df["paper_mapping"].apply(lambda x: x["title"])
    df["start"] = df["paper_mapping"].apply(lambda x: x["start"])
    df["end"] = df["paper_mapping"].apply(lambda x: x["end"])

    # Save the mapping of id: title
    map_dict = df.set_index("id")["title"].to_dict()

    # Save the mapping to JSON file
    with open(paper_map, "w") as f:
        json.dump(map_dict, f, indent=4)

    # In degree, number of being citated
    in_degree = defaultdict(int)
    edge_list = []

    for ref_list, paper_id in tqdm(
        zip(df["ref_list"], df["id"]),
        desc="Computing paper citations...",
        total=len(df),
    ):
        for reference in ref_list:
            edge_list.append((paper_id, reference))
            in_degree[reference] += 1

    df["in_d"] = df["id"].map(in_degree).fillna(0).astype(int)

    # Save the yearly citation for each author
    author_year_citation = (
        df[df["in_d"] != 0][["authors", "year", "in_d"]]
        .explode("authors")
        .groupby(["authors", "year"], sort=False)
        .agg(total_citations=("in_d", "sum"))
        .reset_index()
    )
    author_citation_dict = {}
    for author, group in tqdm(
        author_year_citation.groupby("authors"),
        total=len(author_year_citation.groupby("authors")),
        desc="Processing author citations...",
    ):
        yearly_citations = group.set_index("year")["total_citations"].to_dict()
        author_citation_dict[author] = {
            year: int(yearly_citations.get(year, 0))
            for year in range(group["year"].min(), group["year"].max() + 1)
        }

    with open(citation, "w") as f:
        json.dump(author_citation_dict, f, indent=4)

    # Save the paper node
    df.drop(columns=["title", "references", "ref_list", "paper_mapping"], inplace=True)
    df["authors"] = df["authors"].apply(
        lambda x: "" if x == [1] else "#".join(map(str, x))
    )
    df["isolate"] = (df["in_d"] == 0) & (df["out_d"] == 0)
    df.to_csv(paper_node, index=False)

    # Save the edges of references in papers
    edge_list = [{"src": source, "dst": target} for (source, target) in edge_list]
    edges_df = pd.DataFrame(edge_list)
    edges_df.to_csv(paper_edge, index=False)

    logger.info(
        f"There are total {len(df)} nodes and {len(edges_df)} edges in \033[34mpaper\033[0m."
    )
    logger.info(
        f"Successfully save the information of papers to {paper_map}, {paper_node} and {paper_edge}!"
    )

    del in_degree
    del edge_list
    del edges_df
    gc.collect()


@timer
def save_records_to_csv(
    data_path: Path,
    author_node: Path,
    author_edge: Path,
    venue_map: Path,
    paper_map: Path,
    citation: Path,
    paper_node: Path,
    paper_edge: Path,
) -> None:
    """
    Load and preprocess the dataset, then save as csv files in a single process.
    The csv files include node and edge infos of paper and author, respectively.
    """
    # Process all records into a single DataFrame
    df = _get_dataframe(data_path)

    _save_author_chunk(df, author_node, author_edge)
    _build_venue_index(df, venue_map)
    _save_paper_chunk(df, paper_map, citation, paper_node, paper_edge)

    gc.collect()

    return
