import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

# Set up directory for logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

MAX_LOG_FILES = 20


def _delete_old_logs():
    """
    Deletes the oldest half of the log files if the number of log files exceeds MAX_LOG_FILES.
    """
    log_files = sorted(LOG_DIR.glob("*.log"), key=os.path.getmtime)

    # Check if the number of log files exceeds the limit
    if len(log_files) > MAX_LOG_FILES:
        files_to_delete = log_files[: len(log_files) // 2]
        for file in files_to_delete:
            file.unlink()


def _setup_logger(name: str, level: int = logging.INFO):
    """
    Configures and returns a logger instance with a time-stamped log file.

    Args:
        name (str): Name of the logger.
        level (int): Logging level.
    """
    # Generate log file name with timestamp
    log_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

    # Full path to log file
    log_file_path = LOG_DIR / log_filename

    # Delete old logs if there are more than `MAX_LOG_FILES` log files
    _delete_old_logs()

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Initialize the global logger for the project
logger = _setup_logger("SocialNetwork")
