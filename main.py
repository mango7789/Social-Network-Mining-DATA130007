import yaml
import argparse
import warnings
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
from CommunityMining import louvain


PREPROCESS: Final = True
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
    PAPER_NODE: Final = base_path / config["data"]["paper"]["node"]
    PAPER_EDGE: Final = base_path / config["data"]["paper"]["edge"]

    community_path = (
        Path("CommunityMining") if not args.test else Path("test/CommunityMining")
    )
    COMM_LOUVAIN: Final = community_path / config["community"]["louvain"]
    # COMM_G_N: Final = community_path / config["community"]["girvan_newman"]
    # COMM_L_P: Final = community_path / config["community"]["label_propagation"]

    centrality_path = Path("CentralityMeasure")

    logger.info("Successfully parse the configuration file!")
    logger.info(SEPERATOR)

    ############################################################
    #            Preprocess and load the dataset               #
    ############################################################
    if PREPROCESS:
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
    df_paper_node = load_paper_node(PAPER_NODE, fillna=True, skip_isolate=True)
    df_paper_edge = load_paper_edge(PAPER_EDGE)
    logger.info("Successfully load dataframes and mappings for dblp-v9 dataset!")
    logger.info(SEPERATOR)

    ############################################################
    #                    Community Mining                      #
    ############################################################
    logger.info("Start mining the community of nodes...")
    louvain(df_paper_node, df_paper_edge, COMM_LOUVAIN)
    logger.info("Succesfully conduct community mining on the dataset!")
    logger.info(SEPERATOR)

    ############################################################
    #                 Centrality Measurement                   #
    ############################################################
    logger.info("Start commputing the centrality measurement of nodes...")
    logger.info("Successfully commpute the centrality on the dataset!")
    logger.info(SEPERATOR)

    ############################################################
    #                     Link Prediction                      #
    ############################################################
    logger.info("Start training model for link prediction...")
