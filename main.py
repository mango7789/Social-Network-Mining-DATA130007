import os
from typing import Final

from utils import *

DATA_PATH: Final = os.path.join("data", "dblp.v9", "dblp.txt")
PKL_DIR: Final = os.path.join("data", "vertices")
os.makedirs(PKL_DIR, exist_ok=True)


if __name__ == "__main__":
    load_save_vertex_parallel(DATA_PATH, PKL_DIR, 4)
