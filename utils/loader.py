import json
import pandas as pd
from pathlib import Path
from .logger import logger
from .wrapper import timer


def _load_logger(df: pd.DataFrame, path: Path):
    logger.info(
        f"Load {path} as dataframe, memory usage {df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB"
    )


@timer
def load_paper_node(
    path: Path, fillna: bool = True, skip_isolate: bool = False
) -> pd.DataFrame:
    """
    For the `paper/node.csv` file:
    - The columns include: `id`, `authors`, `year`, `venue`, `out_d`, `start`, `end`, `in_d`, `isolate`
    - `year = 0` indicates that the year value is missing.
    - `venue = 1` indicates that the venue value is missing.
    - An empty string in the `authors` column indicates a missing value in the original file.
    - When loading the `authors` column as a list, the value `[]` is treated as `NaN` in the DataFrame.
    """
    df = pd.read_csv(path, low_memory=True).astype(
        {
            "id": "string",
            "authors": "string",
            "year": "Int16",
            "venue": "str",
            "out_d": "Int16",
            "start": "Int64",
            "end": "Int64",
            "in_d": "Int16",
            "isolate": "bool",
        }
    )

    if fillna:
        df["authors"] = df["authors"].fillna("")

    df["authors"] = df["authors"].str.split("#")
    df["authors"] = df["authors"].apply(lambda x: x if x != [""] else [])

    if skip_isolate:
        df = df[~df["isolate"]].drop(columns=["isolate"])

    _load_logger(df, path)

    return df


@timer
def load_paper_edge(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=True).astype(
        {
            "src": "string",
            "dst": "string",
        }
    )

    _load_logger(df, path)

    return df


@timer
def load_author_node(path: Path, fillna: bool = True) -> pd.DataFrame:
    """
    For the `author/node.csv` file:
    - The columns include: `id`, `name`, `co_authors`, `papers`, `num_co_authors` and `num_papers`.
    - `id = 1` indicates that the `name` of the author and the list of `co_authors` are missing.
    """
    df = pd.read_csv(path, low_memory=True).astype(
        {
            "id": "str",
            "name": "string",
            "co_authors": "string",
            "papers": "string",
            "num_co_authors": "Int32",
            "num_papers": "Int32",
        }
    )

    if fillna:
        df["name"] = df["name"].fillna("")
        df["co_authors"] = df["co_authors"].fillna("")
        df["papers"] = df["papers"].fillna("")

    df["co_authors"] = df["co_authors"].str.split("#")
    df["co_authors"] = df["co_authors"].apply(lambda x: x if x != [""] else [])
    df["papers"] = df["papers"].str.split("#")
    df["papers"] = df["papers"].apply(lambda x: x if x != [""] else [])

    _load_logger(df, path)

    return df


@timer
def load_author_edge(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=True).astype(
        {"src": "str", "dst": "str", "w": "int16"}
    )

    _load_logger(df, path)

    return df


@timer
def load_map_dict(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            map_dict = json.load(f)
        logger.info(f"Successfully loaded JSON from: {path}")
        return map_dict
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise
