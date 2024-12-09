from pathlib import Path
import yaml
import json
from typing import Final
from flask import Flask, jsonify, render_template

from utils import save_records_to_csv, load_records_from_csv
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
    PAPER_LIST: Final = Path(config["data"]["paper"]["list"])
    AUTHOR_LIST: Final = Path(config["data"]["author"]["list"])
    AUTHOR_EDGE: Final = Path(config["data"]["author"]["edge"])

    logger.info("Successfully parse the configuration file!")

    if DEBUG:
        logger.info("Start preprocessing the original dataset...")
        df = save_records_to_csv(DATA_PATH, PAPER_LIST, AUTHOR_LIST, AUTHOR_EDGE)
        logger.info("Successfully preprocess the dblp-v9 dataset!")
    else:
        logger.info("Start loading the original dataset into dataframe...")
        df = load_records_from_csv(PAPER_LIST)
        logger.info("Successfully load the dblp-v9 dataset!")

    # app.run(port=80, debug=True)
