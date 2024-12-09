import functools
import time
from .logger import logger

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        # Log the function name and execution time in minutes and seconds
        minutes, seconds = divmod(execution_time, 60)
        if int(minutes) > 0:
            logger.info(f"Function '{func.__name__}' executed in {int(minutes)} minute(s) and {seconds:.2f} second(s)")
        else:
            logger.info(f"Function '{func.__name__}' executed in {seconds:.2f} second(s)")
        return result

    return wrapper
