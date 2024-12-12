import yaml
import json
from typing import Final
from pathlib import Path
from flask import Flask, jsonify, render_template
import argparse

import warnings
warnings.filterwarnings("ignore")

from utils import (
    save_records_to_csv,
    load_paper_node,
    load_paper_edge,
    load_author_node,
    load_author_edge,
    load_map_dict,
)
from utils.logger import logger


DEBUG: Final = True
SEPERATOR: Final = "=" * 85

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/community")
def community():
    # Load the community data from the JSON file
    with open("community.json", "r") as f:
        data = json.load(f)
    return jsonify(data)


if __name__ == "__main__":
    # An argument parser to specify the mode of main.py
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test", action="store_true", help="Run the script in test mode"
    )
    args = parser.parse_args()
    root_dir = "data" if not args.test else "test"
    base_path = Path(f"./{root_dir}")
    logger.info(
        "=" * 20 + f"       Run script main.py in {root_dir} mode       " + "=" * 20
    )

    # Open and parse the configuration file
    with open("./config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    logger.info("Successfully load the configuration file!")

    DATA_PATH: Final = base_path / config["data"]["dblp"]
    AUTHOR_NODE: Final = base_path / config["data"]["author"]["node"]
    AUTHOR_EDGE: Final = base_path / config["data"]["author"]["edge"]
    VENUE_MAP: Final = base_path / config["data"]["venue"]["map"]
    PAPER_MAP: Final = base_path / config["data"]["paper"]["map"]
    PAPER_NODE: Final = base_path / config["data"]["paper"]["node"]
    PAPER_EDGE: Final = base_path / config["data"]["paper"]["edge"]

    logger.info("Successfully parse the configuration file!")
    logger.info(SEPERATOR)

    # Save or load the dataset
    if DEBUG:
        logger.info("Start preprocessing the original dataset...")
        save_records_to_csv(
            DATA_PATH,
            AUTHOR_NODE,
            AUTHOR_EDGE,
            VENUE_MAP,
            PAPER_MAP,
            PAPER_NODE,
            PAPER_EDGE,
        )
        logger.info("Successfully preprocess the dblp-v9 dataset!")
        logger.info(SEPERATOR)

    logger.info("Start loading dataframes and mappings...")
    df_author_node = load_author_node(AUTHOR_NODE)
    df_author_edge = load_author_edge(AUTHOR_EDGE)
    dict_venue_map = load_map_dict(VENUE_MAP)
    dict_paper_map = load_map_dict(PAPER_MAP)
    df_paper_node = load_paper_node(PAPER_NODE)
    df_paper_edge = load_paper_edge(PAPER_EDGE)
    logger.info("Successfully load dataframes and mappings for dblp-v9 dataset!")
    logger.info(SEPERATOR)

    # app.run(port=80, debug=True)
