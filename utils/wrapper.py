import functools
import time
from .logger import logger


def timer(func):
    """
    A decorator that measures and logs the execution time of a function.

    The execution time is logged in minutes and seconds using the `logger` module.
    The decorator ensures that the function's metadata (e.g., name, docstring) is
    preserved using `functools.wraps`.

    Args:
        func (Callable): The function whose execution time is to be measured.

    Returns:
        Callable: The wrapped function that logs its execution time.

    Example:
    >>>  @timer
    >>>  def my_function():
    >>>      # Function implementation
    >>>      pass

    Notes:
        - This decorator uses `time.time()` to calculate the execution time.
        - It logs the execution time using a `logger` object, so ensure that
          a logger is properly configured in your application.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        # Log the function name and execution time in minutes and seconds
        minutes, seconds = divmod(execution_time, 60)
        if int(minutes) > 0:
            logger.info(
                f"Function '{func.__name__}' executed in {int(minutes)} minute(s) and {seconds:.2f} second(s)"
            )
        else:
            logger.info(
                f"Function '{func.__name__}' executed in {seconds:.2f} second(s)"
            )
        return result

    return wrapper
