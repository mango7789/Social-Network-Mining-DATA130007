import yaml
import json
from typing import Final
from pathlib import Path
from flask import Flask, jsonify, render_template

import warnings
warnings.filterwarnings("ignore")

from utils import (
    save_records_to_csv,
    load_paper_node,
    load_paper_edge,
    load_author_node,
    load_author_edge,
)
from utils.logger import logger


DEBUG: Final = True

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
    # Open and parse the configuration file
    with open("./config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    logger.info("Successfully load the configuration file!")

    DATA_PATH: Final = Path(config["data"]["dblp"])
    PAPER_NODE: Final = Path(config["data"]["paper"]["node"])
    PAPER_EDGE: Final = Path(config["data"]["paper"]["edge"])
    AUTHOR_NODE: Final = Path(config["data"]["author"]["node"])
    AUTHOR_EDGE: Final = Path(config["data"]["author"]["edge"])

    logger.info("Successfully parse the configuration file!")

    if DEBUG:
        logger.info("Start preprocessing the original dataset...")
        df = save_records_to_csv(
            DATA_PATH, PAPER_NODE, PAPER_EDGE, AUTHOR_NODE, AUTHOR_EDGE
        )
        logger.info("Successfully preprocess the dblp-v9 dataset!")
    else:
        logger.info("Start loading the dataframe...")
        df_paper_node = load_paper_node(PAPER_NODE)
        df_paper_edge = load_paper_edge(PAPER_EDGE)
        df_author_node = load_author_node(AUTHOR_NODE)
        df_author_edge = load_author_edge(AUTHOR_EDGE)
        logger.info("Successfully load dataframes for dblp-v9 dataset!")

    # app.run(port=80, debug=True)
