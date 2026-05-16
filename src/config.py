import os, sys
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
#
from src.exceptions import *
import src.http_utils as http_utils

logger:logging.Logger = logging.getLogger(__name__)

def configure_logging(log_level:str) -> None:
    """
    Configure the logging-module for this project.
    """
    #
    # Prevent adding multiple handlers if this function is called multiple times
    if logging.getLogger().handlers:
        return
    
    handlers:list[logging.StreamHandler] = [
        logging.StreamHandler(sys.stdout)
    ]

    logging.basicConfig(
        level=log_level.upper(),
        format="(%(asctime)s) [%(levelname)s] [%(threadName)s] %(name)s.%(funcName)s: %(message)s",
        handlers=handlers,
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )
    #
    # Surpress requests TLS-warnings
    requests.packages.urllib3.disable_warnings()

@dataclass(frozen=True)
class Config:
    dotenv_filepath:Path
    #
    ntfy_topic_url:str
    ntfy_auth_token:str
    ntfy_http_requests_timeout:int
    ntfy_http_requests_tls_verify:bool
    #
    frequency_source_url:str
    frequency_source_http_requests_timeout:int
    frequency_source_http_requests_tls_verify:bool
    #
    warning_min_hz_alert_threshold: float
    warning_max_hz_alert_threshold: float
    critical_min_hz_alert_threshold: float
    critical_max_hz_alert_threshold: float

def load_config(dotenv_filepath:Path) -> Config:
    """
    Load configuration from dotenv file into dataclass-Object.
    
    Raises `ConfigError`-exceptions:
    - `InvalidConfigError`: invalid dotenv-variable or invalid dotenv-filepath
    - `MissingConfigError`: missing dotenv-variable
    """
    #
    # Check whether the dotenv filepath exists
    if not dotenv_filepath.exists() or not dotenv_filepath.is_file():
        raise InvalidConfigError(f"The given dotenv-filepath '{dotenv_filepath}' is invalid!")
    #
    # Load dotenv
    load_dotenv(dotenv_path=dotenv_filepath)
    
    ntfy_topic_url:str|None = os.getenv('NTFY_TOPIC_URL', None)
    if ntfy_topic_url is None:
        raise MissingConfigError("Missing 'NTFY_TOPIC_URL'")
    if not ntfy_topic_url:
        raise InvalidConfigError("Invalid 'NTFY_TOPIC_URL'")
    
    ntfy_auth_token:str|None = os.getenv('NTFY_AUTH_TOKEN', None)
    if not ntfy_auth_token:
        raise MissingConfigError("Missing 'NTFY_AUTH_TOKEN'")
    
    ntfy_http_requests_timeout_string:str = os.getenv('NTFY_HTTP_REQUESTS_TIMEOUT', '10')
    try:
        ntfy_http_requests_timeout:int = int(ntfy_http_requests_timeout_string)
        if ntfy_http_requests_timeout <= 0:
            raise ValueError("The 'NTFY_HTTP_REQUESTS_TIMEOUT' is cannot be below 1")
    except (TypeError, ValueError) as _e:
        raise InvalidConfigError("The 'NTFY_HTTP_REQUESTS_TIMEOUT' needs to be a valid integer greater than 0") from _e

    ntfy_http_requests_tls_verify:bool = True if os.getenv('NTFY_HTTP_REQUESTS_TLS_VERIFY', 'true').lower() == "true" else False

    frequency_source_url:str = os.getenv('FREQUENCY_SOURCE_URL', 'https://dat.netzfrequenzmessung.de:9080/frequenz.xml')
    if not http_utils.is_valid_frequency_source_url(url=frequency_source_url):
        raise InvalidConfigError("The provided 'FREQUENCY_SOURCE_URL' is invalid!")
    
    frequency_source_http_requests_timeout_string:str = os.getenv('FREQUENCY_SOURCE_HTTP_REQUESTS_TIMEOUT', '10')
    try:
        frequency_source_http_requests_timeout:int = int(frequency_source_http_requests_timeout_string)
        if frequency_source_http_requests_timeout <= 0:
            raise ValueError("The 'FREQUENCY_SOURCE_HTTP_REQUESTS_TIMEOUT' is cannot be below 1")
    except (TypeError, ValueError) as _e:
        raise InvalidConfigError("The 'FREQUENCY_SOURCE_HTTP_REQUESTS_TIMEOUT' needs to be a valid integer greater than 0") from _e

    frequency_source_http_requests_tls_verify:bool = True if os.getenv('FREQUENCY_SOURCE_HTTP_REQUESTS_TLS_VERIFY', 'true').lower() == "true" else False

    warning_min_hz_alert_threshold_string:str = os.getenv('WARNING_MIN_HZ_ALERT_THRESHOLD', '49.850')
    try:
        warning_min_hz_alert_threshold:float = float(warning_min_hz_alert_threshold_string)
    except (ValueError, TypeError) as _e:
        raise InvalidConfigError("The 'WARNING_MIN_HZ_ALERT_THRESHOLD' needs to be a valid float")

    warning_max_hz_alert_threshold_string:str = os.getenv('WARNING_MAX_HZ_ALERT_THRESHOLD', '50.150')
    try:
        warning_max_hz_alert_threshold:float = float(warning_max_hz_alert_threshold_string)
    except (ValueError, TypeError) as _e:
        raise InvalidConfigError("The 'WARNING_MAX_HZ_ALERT_THRESHOLD' needs to be a valid float")
    #
    # Check whether WARNING-MIN is below WARNING-MAX
    if warning_min_hz_alert_threshold >= warning_max_hz_alert_threshold:
        raise InvalidConfigError("The 'WARNING_MIN_HZ_ALERT_THRESHOLD' needs to be below 'WARNING_MAX_HZ_ALERT_THRESHOLD'")

    critical_min_hz_alert_threshold_string:str = os.getenv('CRITICAL_MIN_HZ_ALERT_THRESHOLD', '49.600')
    try:
        critical_min_hz_alert_threshold:float = float(critical_min_hz_alert_threshold_string)
    except (ValueError, TypeError) as _e:
        raise InvalidConfigError("The 'CRITICAL_MIN_HZ_ALERT_THRESHOLD' needs to be a valid float")
    
    critical_max_hz_alert_threshold_string:str = os.getenv('CRITICAL_MAX_HZ_ALERT_THRESHOLD', '50.400')
    try:
        critical_max_hz_alert_threshold:float = float(critical_max_hz_alert_threshold_string)
    except (ValueError, TypeError) as _e:
        raise InvalidConfigError("The 'CRITICAL_MAX_HZ_ALERT_THRESHOLD' needs to be a valid float")
    #
    # Check whether CRITICAL-MIN is below CRITICAL-MAX
    if critical_min_hz_alert_threshold >= critical_max_hz_alert_threshold:
        raise InvalidConfigError("The 'CRITICAL_MIN_HZ_ALERT_THRESHOLD' needs to be below 'CRITICAL_MAX_HZ_ALERT_THRESHOLD'")
    #
    # Check whether WARNING-MIN is above CRITICAL-MIN
    if warning_min_hz_alert_threshold <= critical_min_hz_alert_threshold:
        raise InvalidConfigError("The 'WARNING_MIN_HZ_ALERT_THRESHOLD' needs to be above 'CRITICAL_MIN_HZ_ALERT_THRESHOLD'")
    #
    # Check whether WARNING-MAX is below CRTIICAL-MAX
    if warning_max_hz_alert_threshold >= critical_max_hz_alert_threshold:
        raise InvalidConfigError("The 'WARNING_MAX_HZ_ALERT_THRESHOLD' needs to be below 'CRITICAL_MAX_HZ_ALERT_THRESHOLD'")

    return Config(
        dotenv_filepath=dotenv_filepath,
        ntfy_topic_url=ntfy_topic_url,
        ntfy_auth_token=ntfy_auth_token,
        ntfy_http_requests_timeout=ntfy_http_requests_timeout,
        ntfy_http_requests_tls_verify=ntfy_http_requests_tls_verify,
        frequency_source_url=frequency_source_url,
        frequency_source_http_requests_timeout=frequency_source_http_requests_timeout,
        frequency_source_http_requests_tls_verify=frequency_source_http_requests_tls_verify,
        warning_min_hz_alert_threshold=warning_min_hz_alert_threshold,
        warning_max_hz_alert_threshold=warning_max_hz_alert_threshold,
        critical_min_hz_alert_threshold=critical_min_hz_alert_threshold,
        critical_max_hz_alert_threshold=critical_max_hz_alert_threshold
    )