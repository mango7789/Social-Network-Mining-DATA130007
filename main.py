import os
import yaml
import argparse
import warnings
import subprocess
from pathlib import Path
from typing import Final
import concurrent.futures

from utils import (
    save_records_to_csv,
    load_paper_node,
    load_paper_edge,
    load_author_node,
    load_author_edge,
    load_map_dict,
)
from utils.logger import logger
from CommunityMining import (
    louvain_ig,
    community_detection_with_filter,
    community_detection_no_filter,
    Algorithm,
)
from CentralityMeasure import (
    calculate_centrality_and_statistics,
    calculate_community_diameters,
)

PREPROCESS: Final = False
SEPERATOR: Final = "=" * 85
LINEBREAK: Final = "-" * 85
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

    community_path = Path("CommunityMining")
    AUTHOR_COMM: Final = community_path / config["community"]["author"]
    PAPER_COMM: Final = community_path / config["community"]["paper"]

    centrality_path = Path("CentralityMeasure")
    CENTRALITY_DIR: Final = centrality_path / config["centrality"]["results"]

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
    df_author_node: Final = load_author_node(AUTHOR_NODE)
    df_author_edge: Final = load_author_edge(AUTHOR_EDGE)
    dict_venue_map = load_map_dict(VENUE_MAP)
    dict_paper_map = load_map_dict(PAPER_MAP)
    dict_citation = load_map_dict(CITATION)
    df_paper_node: Final = load_paper_node(PAPER_NODE, fillna=True, skip_isolate=True)
    df_paper_edge: Final = load_paper_edge(PAPER_EDGE)
    logger.info("Successfully load dataframes and mappings for dblp-v9 dataset!")
    logger.info(SEPERATOR)

    ############################################################
    #           Conducting tasks on the dataset                #
    ############################################################
    if not args.test:
        # Community Mining
        def community_mining():
            logger.info("Start conducting community mining...")

            with concurrent.futures.ProcessPoolExecutor() as executor:
                # Start the tasks in parallel
                futures = [
                    executor.submit(
                        community_detection_with_filter,
                        df_author_node,
                        df_author_edge,
                        AUTHOR_COMM,
                        Algorithm.LABEL_PROPAGATION.value,
                    ),
                    executor.submit(
                        louvain_ig, df_paper_node, df_paper_edge, PAPER_COMM
                    ),
                    executor.submit(
                        community_detection_no_filter,
                        df_paper_node,
                        df_paper_edge,
                        PAPER_COMM,
                        Algorithm.LABEL_PROPAGATION,
                    ),
                    executor.submit(
                        community_detection_no_filter,
                        df_paper_node,
                        df_paper_edge,
                        PAPER_COMM,
                        Algorithm.MULTILEVEL,
                    ),
                ]

                # Wait for all tasks to complete
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Error during community mining: {e}")

            logger.info("Successfully mine the community of each node!")
            logger.info(SEPERATOR)

        community_mining()

        # Centrality Measure and diameter
        logger.info("Start calculating centrality and diameter...")
        calculate_centrality_and_statistics(
            df_paper_node, df_paper_edge, CENTRALITY_DIR
        )
        logger.info(LINEBREAK)

        calculate_community_diameters(
            df_paper_node,
            df_paper_edge,
            PAPER_COMM / "louvain.csv",
            CENTRALITY_DIR / "diameter.json",
        )
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
