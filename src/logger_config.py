import sys
import logging

def configure_logger(log_level:str) -> None:
    """
    Configure logging module for this project.
    """
    # Prevent adding multiple handlers if this function is called multiple times
    if logging.getLogger().handlers:
        return
    
    handlers:list[logging.StreamHandler] = [
        logging.StreamHandler(sys.stdout)
    ]

    logging.basicConfig(
        level=log_level,
        format="(%(asctime)s) [%(levelname)s] [%(threadName)s] %(name)s.%(funcName)s: %(message)s",
        handlers=handlers,
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )