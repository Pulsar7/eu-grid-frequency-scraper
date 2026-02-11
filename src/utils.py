import requests
from pathlib import Path

def get_dotenv_filepath() -> Path:
    """
    Get absolute filepath of dotenv-file.
    """
    return Path(".env")
    