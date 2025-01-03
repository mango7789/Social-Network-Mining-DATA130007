import os
import torch
import random
import numpy as np


def set_global_seed(seed: int):
    # Set the seed for the random module
    random.seed(seed)

    # Set the seed for numpy
    np.random.seed(seed)

    # Set the seed for PyTorch (if used)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.manual_seed(seed)

    # Set deterministic behavior in PyTorch (optional, useful for debugging)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # Ensure reproducibility for Python's os module (for random file shuffling, etc.)
    os.environ["PYTHONHASHSEED"] = str(seed)


set_global_seed(42)
