import os
import yaml
import argparse
import warnings
import subprocess
from pathlib import Path
from typing import Final


from utils import (
    save_records_to_csv,
    load_paper_node,
    load_paper_edge,
    load_author_node,
    load_author_edge,
    load_map_dict,
)
from utils.logger import logger


PREPROCESS: Final = False
SEPERATOR: Final = "=" * 85
warnings.filterwarnings("ignore")


if __name__ == "__main__":
    ############################################################
    #   Add an argument parser to specify the mode of main.py  #
    ############################################################
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

    ############################################################
    #           Open and parse the configuration file          #
    ############################################################
    with open("./config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    logger.info("Successfully load the configuration file!")

    DATA_PATH: Final = base_path / config["data"]["dblp"]
    AUTHOR_NODE: Final = base_path / config["data"]["author"]["node"]
    AUTHOR_EDGE: Final = base_path / config["data"]["author"]["edge"]
    VENUE_MAP: Final = base_path / config["data"]["venue"]["map"]
    PAPER_MAP: Final = base_path / config["data"]["paper"]["map"]
    CITATION: Final = base_path / config["data"]["citation"]
    PAPER_NODE: Final = base_path / config["data"]["paper"]["node"]
    PAPER_EDGE: Final = base_path / config["data"]["paper"]["edge"]

    centrality_path = Path("CentralityMeasure")

    logger.info("Successfully parse the configuration file!")
    logger.info(SEPERATOR)

    if PREPROCESS:
        ############################################################
        #                   Preprocess the dataset                 #
        ############################################################
        logger.info("Start preprocessing the original dataset...")
        save_records_to_csv(
            DATA_PATH,
            AUTHOR_NODE,
            AUTHOR_EDGE,
            VENUE_MAP,
            PAPER_MAP,
            CITATION,
            PAPER_NODE,
            PAPER_EDGE,
        )
        logger.info("Successfully preprocess the dblp-v9 dataset!")
        logger.info(SEPERATOR)

    ############################################################
    #                     Load the dataset                     #
    ############################################################
    logger.info("Start loading dataframes and mappings...")
    df_author_node = load_author_node(AUTHOR_NODE)
    df_author_edge = load_author_edge(AUTHOR_EDGE)
    dict_venue_map = load_map_dict(VENUE_MAP)
    dict_paper_map = load_map_dict(PAPER_MAP)
    dict_citation = load_map_dict(CITATION)
    df_paper_node = load_paper_node(PAPER_NODE, fillna=True, skip_isolate=True)
    df_paper_edge = load_paper_edge(PAPER_EDGE)
    logger.info("Successfully load dataframes and mappings for dblp-v9 dataset!")
    logger.info(SEPERATOR)

    ############################################################
    #           Conducting tasks on the dataset                #
    ############################################################
    if not args.test:
        # Community Mining
        logger.info("Start conducting community mining...")
        subprocess.run(["python", "-m", "CommunityMining.author_community"])
        subprocess.run(["python", "-m", "CommunityMining.louvain"])
        logger.info("Successfully mine the community of each node!")
        logger.info(SEPERATOR)

        # Centrality Measure and diameter
        logger.info("Start calculating centrality and diameter...")
        subprocess.run(["python", "-m", "CentralityMeasure.centrality"])
        subprocess.run(["python", "-m", "CentralityMeasure.diameter"])
        logger.info("Successfully calculate centrality and diameter!")
        logger.info(SEPERATOR)

        # Filter ids for visualization
        logger.info("Start filtering ids for visualization...")
        os.chdir("CommunityMining")
        subprocess.run(["python", "filter_author.py"], check=True)
        subprocess.run(["python", "filter_paper.py"], check=True)
        os.chdir("..")
        logger.info("Successfully filter out ids for visualization!")
        logger.info(SEPERATOR)

        # Generate data for visualization
        logger.info("Start generating data for visualization...")
        subprocess.run(["python", "combine_author.py"])
        subprocess.run(["python", "combine_paper.py"])
        logger.info("Successfully generate data for visualization!")
        logger.info(SEPERATOR)
        logger.info("Now you can use `liveserver` to open the visualization page!!!")
