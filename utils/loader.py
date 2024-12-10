import pandas as pd
from .logger import logger
from .wrapper import timer


def _load_logger(df: pd.DataFrame, path: str):
    logger.info(
        f"Load {path} as dataframe, memory usage {df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB"
    )


@timer
def load_paper_node(path: str, fillna: bool = True) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=True).astype(
        {
            "id": "string",
            "title": "string",
            "authors": "string",
            "year": "int16",
            "venue": "string",
            "out_d": "int16",
            "in_d": "int16",
        }
    )

    if fillna:
        df["authors"] = df["authors"].fillna("")
        df["venue"] = df["venue"].fillna("")

    df["authors"] = df["authors"].str.split("#")

    _load_logger(df, path)

    return df


@timer
def load_paper_edge(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=True).astype(
        {
            "src": "string",
            "dst": "string",
        }
    )

    _load_logger(df, path)

    return df


@timer
def load_author_node(path: str, fillna: bool = True) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=True).astype(
        {
            "id": "int64",
            "name": "string",
            "co-authors": "string",
            "papers": "string",
        }
    )

    if fillna:
        df["name"] = df["name"].fillna("")
        df["co-authors"] = df["co-authors"].fillna("")
        df["papers"] = df["papers"].fillna("")

    df["co-authors"] = df["co-authors"].str.split("#")
    df["papers"] = df["papers"].str.split("#")

    _load_logger(df, path)

    return df


@timer
def load_author_edge(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=True).astype(
        {"src": "string", "dst": "string", "w": "int16"}
    )

    _load_logger(df, path)

    return df
