from pathlib import Path
import yaml
import json
from typing import Final
from flask import Flask, jsonify, render_template

from utils import load_save_vertex_to_csv
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
    CSV_DIR: Final = Path(config["data"]["vertex"]["csv"])
    CHUNK_CFG: Final = Path(config["data"]["vertex"]["cfg"])
    logger.info("Successfully parse the configuration file!")

    if DEBUG:
        # Preprocess the original dataset and save it to csv files
        logger.info("Start preprocessing the original dataset...")
        num_vertices = load_save_vertex_to_csv(DATA_PATH, CSV_DIR, CHUNK_CFG)
        logger.info(f"There are total {num_vertices} vertices in the dataset!")
        logger.info("Successfully preprocess the dblp-v9 dataset!")
    else:
        app.run(port=80, debug=True)
