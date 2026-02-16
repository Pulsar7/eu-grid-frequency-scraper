from pathlib import Path
from datetime import datetime, timezone

def get_dotenv_filepath() -> Path:
    """
    Get absolute filepath of dotenv-file.
    """
    return Path(".env")

def get_iso8601_timestamp() -> str:
    """
    Get current UTC-datetime in ISO8601 format.
    """
    return datetime.now(timezone.utc).isoformat()
    