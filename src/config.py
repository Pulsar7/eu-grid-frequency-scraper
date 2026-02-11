import os
import logging
from pathlib import Path
from dotenv import load_dotenv
#
from src.utils import get_dotenv_filepath
from src.custom_exceptions import InvalidConfigError

logger = logging.getLogger(__name__)

#----------------------------------------
# Load environment variables
#----------------------------------------
dotenv_filepath:Path = get_dotenv_filepath()
logger.debug(f"Using dotenv-filepath '{dotenv_filepath.absolute()}'")
load_dotenv(
    dotenv_path=dotenv_filepath, override=True
)


#
# NTFY 
#
enable_ntfy:str = os.getenv('ENABLE_NTFY', 'false').strip().upper()
ENABLE_NTFY:bool = True if enable_ntfy == "TRUE" else False

NTFY_TOPIC_URL:str|None = os.getenv('NTFY_TOPIC_URL', None)
if ENABLE_NTFY and not NTFY_TOPIC_URL:
    raise InvalidConfigError("Missing 'NTFY_TOPIC_URL', when 'ENABLE_NTFY' is true!")

NTFY_AUTH_TOKEN:str|None = os.getenv('NTFY_AUTH_TOKEN', None)
if ENABLE_NTFY and not NTFY_AUTH_TOKEN:
    raise InvalidConfigError("Missing 'NTFY_AUTH_TOKEN', when 'ENABLE_NTFY' is true!")

min_hz_alert_threshold:str = os.getenv('MIN_HZ_ALERT_THRESHOLD', "49.95")
try:
    MIN_HZ_ALERT_THRESHOLD:float = float(min_hz_alert_threshold)
except ValueError as _e:
    raise InvalidConfigError("Got an invalid 'MIN_HZ_ALERT_THRESHOLD'! Must be a float.") from _e

max_hz_alert_threshold:str = os.getenv('MAX_HZ_ALERT_THRESHOLD', "50.05")
try:
    MAX_HZ_ALERT_THRESHOLD:float = float(max_hz_alert_threshold)
except ValueError as _e:
    raise InvalidConfigError("Got an invalid 'MAX_HZ_ALERT_THRESHOLD'! Must be a float.") from _e


#
# API
#
NETZFREQUENZ_DE_API_URL:str = os.getenv('NETZFREQUENZ_DE_API_URL', '')
if not NETZFREQUENZ_DE_API_URL:
    raise InvalidConfigError("Missing 'NETZFREQUENZ_DE_API_URL'!")


#
# HTTP-requests
#
http_request_timeout:str = os.getenv('HTTP_REQUEST_TIMEOUT', '10')
try:
    HTTP_REQUEST_TIMEOUT:int = int(http_request_timeout)
except ValueError as _e:
    raise InvalidConfigError("Got an invalid 'HTTP_REQUEST_TIMEOUT'! Must be an integer.") from _e

