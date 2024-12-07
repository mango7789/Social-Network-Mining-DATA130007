import os
import yaml
from typing import Final

from utils import load_save_vertex_to_csv
from utils.logger import logger

# Open and parse the configuration file
with open("./config/config.yaml", "r") as file:
    config = yaml.safe_load(file)
logger.info("Successfully load the configuration file!")

DATA_PATH: Final = config["data"]["dblp"]
CSV_DIR: Final = config["data"]["vertex"]["csv"]
CHUNK_CFG: Final = config["data"]["vertex"]["cfg"]
os.makedirs(CSV_DIR, exist_ok=True)
logger.info("Successfully parse the configuration file!")

if __name__ == "__main__":

    # Preprocess the original dataset and save it to csv files
    logger.info("Start preprocessing the original dataset...")
    num_vertices = load_save_vertex_to_csv(DATA_PATH, CSV_DIR, CHUNK_CFG)
    logger.info(f"There are total {num_vertices} vertices in the dataset!")
    logger.info("Successfully preprocess the dblp-v9 dataset!")
