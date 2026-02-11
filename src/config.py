import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
#
from src.utils import get_dotenv_filepath
from src.custom_exceptions import InvalidConfigError

logger:logging.Logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Config:
    enable_ntfy: bool
    ntfy_topic_url: str | None
    ntfy_auth_token: str | None
    ntfy_http_request_timeout:int 
    min_hz_alert_threshold: float
    max_hz_alert_threshold: float
    api_url: str
    api_http_request_timeout: int
    

def load_config() -> Config:
    """
    Load configuration of dotenv-file into dataclass-object.
    
    Raises 'InvalidConfigError' when an invalid config is given.
    """
    load_dotenv(dotenv_path=get_dotenv_filepath(), override=True)
    
    #
    # NTFY
    #
    enable_ntfy:bool = os.getenv('ENABLE_NTFY', 'false').strip().upper() == "TRUE"
    
    ntfy_topic_url:str|None = os.getenv('NTFY_TOPIC_URL', None)
    if enable_ntfy and not ntfy_topic_url:
        raise InvalidConfigError("Missing 'NTFY_TOPIC_URL', when 'ENABLE_NTFY' is true!")
    
    ntfy_auth_token:str|None = os.getenv('NTFY_AUTH_TOKEN', None)
    if enable_ntfy and not ntfy_auth_token:
        raise InvalidConfigError("Missing 'NTFY_AUTH_TOKEN', when 'ENABLE_NTFY' is true!")
    
    try:
        ntfy_http_request_timeout:int = int(os.getenv('NTFY_HTTP_REQUEST_TIMEOUT', '10'))
    except ValueError as _e:
        raise InvalidConfigError("Got an invalid 'NTFY_HTTP_REQUEST_TIMEOUT'! Must be an integer.") from _e
    
    if ntfy_http_request_timeout < 0:
        raise InvalidConfigError("'NTFY_HTTP_REQUEST_TIMEOUT' must be >= 0")
    
    try:
        min_hz_alert_threshold:float = float(os.getenv('MIN_HZ_ALERT_THRESHOLD', "49.95"))
    except ValueError as _e:
        raise InvalidConfigError("Got an invalid 'MIN_HZ_ALERT_THRESHOLD'! Must be a float.") from _e
    
    try:
        max_hz_alert_threshold:float = float(os.getenv('MAX_HZ_ALERT_THRESHOLD', "50.05"))
    except ValueError as _e:
        raise InvalidConfigError("Got an invalid 'MAX_HZ_ALERT_THRESHOLD'! Must be a float.") from _e

    if min_hz_alert_threshold >= max_hz_alert_threshold:
        raise InvalidConfigError("'MIN_HZ_ALERT_THRESHOLD' needs to be lower than 'MAX_HZ_ALERT_THRESHOLD'!")

    #
    # API
    #
    api_url:str = os.getenv('NETZFREQUENZ_DE_API_URL', '')
    if not api_url:
        raise InvalidConfigError("Missing 'NETZFREQUENZ_DE_API_URL'!")
    
    try:
        api_http_request_timeout:int = int(os.getenv('API_HTTP_REQUEST_TIMEOUT', '10'))
    except ValueError as _e:
        raise InvalidConfigError("Got an invalid 'API_HTTP_REQUEST_TIMEOUT'! Must be an integer.") from _e
    
    if api_http_request_timeout < 0:
        raise InvalidConfigError("'API_HTTP_REQUEST_TIMEOUT' must be >= 0")
    
    return Config(
        enable_ntfy=enable_ntfy,
        ntfy_topic_url=ntfy_topic_url,
        ntfy_auth_token=ntfy_auth_token,
        ntfy_http_request_timeout=ntfy_http_request_timeout,
        min_hz_alert_threshold=min_hz_alert_threshold,
        max_hz_alert_threshold=max_hz_alert_threshold,
        api_url=api_url,
        api_http_request_timeout=api_http_request_timeout
    )