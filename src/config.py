import os
import logging
from dotenv import load_dotenv
from dataclasses import dataclass
#
from src.utils import get_dotenv_filepath
from src.custom_exceptions import InvalidConfigError, InvalidMaxMinThresholdError

logger:logging.Logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Config:
    enable_ntfy: bool
    ntfy_topic_url: str | None
    ntfy_auth_token: str | None
    ntfy_http_request_timeout:int
    ntfy_http_request_cert_verify: bool
    warning_min_hz_alert_threshold: float
    warning_max_hz_alert_threshold: float
    critical_min_hz_alert_threshold: float
    critical_max_hz_alert_threshold: float
    api_url: str
    api_http_request_timeout: int
    api_http_request_cert_verify: bool
    

def load_config() -> Config:
    """
    Load configuration of dotenv-file into dataclass-object.
    
    Raises `InvalidConfigError` when an invalid config is given.
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
    
    ntfy_http_request_cert_verify:bool = os.getenv('NTFY_HTTP_REQUEST_CERT_VERIFY', 'false').strip().upper() == "TRUE"
    
    
    #
    # Alert
    #
    try:
        warning_min_hz_alert_threshold:float = float(os.getenv('WARNING_MIN_HZ_ALERT_THRESHOLD', "49.850"))
    except ValueError as _e:
        raise InvalidMaxMinThresholdError("Got an invalid 'WARNING_MIN_HZ_ALERT_THRESHOLD'! Must be a float.") from _e
    
    if warning_min_hz_alert_threshold <= 0:
        raise InvalidMaxMinThresholdError("'WARNING_MIN_HZ_ALERT_THRESHOLD' must not be negative!")
    
    try:
        warning_max_hz_alert_threshold:float = float(os.getenv('WARNING_MAX_HZ_ALERT_THRESHOLD', "50.150"))
    except ValueError as _e:
        raise InvalidMaxMinThresholdError("Got an invalid 'WARNING_MAX_HZ_ALERT_THRESHOLD'! Must be a float.") from _e

    if warning_min_hz_alert_threshold >= warning_max_hz_alert_threshold:
        raise InvalidMaxMinThresholdError("'WARNING_MIN_HZ_ALERT_THRESHOLD' needs to be lower than 'WARNING_MAX_HZ_ALERT_THRESHOLD'!")
    
    try:
        critical_min_hz_alert_threshold:float = float(os.getenv('CRITICAL_MIN_HZ_ALERT_THRESHOLD', "49.600"))
    except ValueError as _e:
        raise InvalidMaxMinThresholdError("Got an invalid 'CRITICAL_MIN_HZ_ALERT_THRESHOLD'! Must be a float.") from _e
    
    try:
        critical_max_hz_alert_threshold:float = float(os.getenv('CRITICAL_MAX_HZ_ALERT_THRESHOLD', "50.400"))
    except ValueError as _e:
        raise InvalidMaxMinThresholdError("Got an invalid 'CRITICAL_MAX_HZ_ALERT_THRESHOLD'! Must be a float.") from _e

    if critical_min_hz_alert_threshold >= warning_min_hz_alert_threshold:
        raise InvalidMaxMinThresholdError("'CRITICAL_MIN_HZ_ALERT_THRESHOLD' needs to be lower than 'WARNING_MIN_HZ_ALERT_THRESHOLD'")

    if critical_max_hz_alert_threshold <= warning_max_hz_alert_threshold:
        raise InvalidMaxMinThresholdError("'CRITICAL_MAX_HZ_ALERT_THRESHOLD' needs to be bigger than 'WARNING_MAX_HZ_ALERT_THRESHOLD'")

    if critical_min_hz_alert_threshold >= critical_max_hz_alert_threshold:
        raise InvalidMaxMinThresholdError("'CRITICAL_MIN_HZ_ALERT_THRESHOLD' needs to be lower than 'CRITICAL_MAX_HZ_ALERT_THRESHOLD'!")


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
    
    api_http_request_cert_verify:bool = os.getenv('API_HTTP_REQUEST_CERT_VERIFY', 'true').strip().upper() == "TRUE"
    
    return Config(
        enable_ntfy=enable_ntfy,
        ntfy_topic_url=ntfy_topic_url,
        ntfy_auth_token=ntfy_auth_token,
        ntfy_http_request_timeout=ntfy_http_request_timeout,
        ntfy_http_request_cert_verify=ntfy_http_request_cert_verify,
        warning_min_hz_alert_threshold=warning_min_hz_alert_threshold,
        warning_max_hz_alert_threshold=warning_max_hz_alert_threshold,
        critical_min_hz_alert_threshold=critical_min_hz_alert_threshold,
        critical_max_hz_alert_threshold=critical_max_hz_alert_threshold,
        api_url=api_url,
        api_http_request_timeout=api_http_request_timeout,
        api_http_request_cert_verify=api_http_request_cert_verify
    )