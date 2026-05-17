"""

    EU-Grid frequency scraper Script

"""
import os
import time
import logging
import argparse
from dataclasses import fields
from pathlib import Path, PosixPath
#
from src.exceptions import *
import src.constants as consts
import src.ntfy_utils as ntfy_utils
import src.website_utils as website_utils
from src.constants import Alert, AlertType
from src.config import configure_logging, load_config, Config

def show_config(config:Config) -> None:
    """
    Printout configuration from Config-dataclass-object.
    """
    l:int = 100
    print(f"<{''.join(['-' for _ in range(0,l)])}>")
    for field in fields(config):
        attr = getattr(config, field.name)
        if type(attr) == PosixPath:
            attr = attr.resolve()
        print(f" {field.name}: {attr}")
    print(f"<{''.join(['-' for _ in range(0,l)])}>")

def get_alert(config:Config, frequency:float, timestamp:str) -> Alert:
    """
    
    """
    #
    # Determine whether to send an alert message or not
    alert_title:str = ""
    alert_msg:str = ""
    alert_type:AlertType = AlertType.NO_ALERT
    if frequency >= config.warning_max_hz_alert_threshold:
        logger.info(f"Reached MAX-Hz WARNING-threshold of {config.warning_max_hz_alert_threshold}Hz. Frequency={frequency}Hz ; Timestamp={timestamp}")
        alert_title = "WARNING MAX-Hz threshold reached"
        alert_msg = f"Warning MAX-Hz threshold of {config.warning_max_hz_alert_threshold}Hz reached."
        alert_type = AlertType.WARNING_ALERT

    elif frequency <= config.warning_min_hz_alert_threshold:
        logger.info(f"Reached MIN-Hz WARNING-threshold of {config.warning_min_hz_alert_threshold}Hz. Frequency={frequency}Hz ; Timestamp={timestamp}")
        alert_title = "WARNING MIN-Hz threshold reached"
        alert_msg = f"Warning MIN-Hz threshold of {config.warning_min_hz_alert_threshold}Hz reached."
        alert_type = AlertType.WARNING_ALERT

    elif frequency >= config.critical_max_hz_alert_threshold:
        logger.info(f"Reached MAX-Hz CRITICAL-threshold of {config.critical_max_hz_alert_threshold}Hz. Frequency={frequency}Hz ; Timestamp={timestamp}")
        alert_title = "WARNING MAX-Hz threshold reached"
        alert_msg = f"Critical MAX-Hz threshold of {config.critical_max_hz_alert_threshold}Hz reached."
        alert_type = AlertType.CRITICAL_ALERT

    elif frequency <= config.critical_min_hz_alert_threshold:
        logger.info(f"Reached MIN-Hz CRITICAL-threshold of {config.critical_min_hz_alert_threshold}Hz. Frequency={frequency}Hz ; Timestamp={timestamp}")
        alert_title = "WARNING MIN-Hz threshold reached"
        alert_msg = f"Critical MIN-Hz threshold of {config.critical_min_hz_alert_threshold}Hz reached."
        alert_type = AlertType.CRITICAL_ALERT

    if alert_type is not AlertType.NO_ALERT:
        alert_msg += f"\n> Frequency={frequency}Hz\n > Timestamp={timestamp}\n\n Data-Source-API-URL={config.data_source_api_url}"

    return Alert(alert_type, alert_title, alert_msg)

def send_ntfy_alert(config:Config, alert:Alert) -> None:
    """
    
    """
    ntfy_utils.send_alert(
        topic_url=config.ntfy_topic_url,
        auth_token=config.ntfy_auth_token,
        http_requests_timeout=config.ntfy_http_requests_timeout,
        requests_tls_verify=config.ntfy_http_requests_tls_verify,
        title=alert.alert_title,
        message=alert.alert_msg,
        priority="urgent",
        tags="rotating_light" if alert.alert_type == AlertType.CRITICAL_ALERT else "warning"
    )
    
def main() -> None:
    _start:float = time.time()
    logger.debug(f"Started '{filename}'")
    #
    # Get CLI-arguments
    parser = argparse.ArgumentParser(filename)
    parser.add_argument(
        '-l', '--loglevel', help=f"Set the logging-level (Default='{consts.DEFAULT_LOGGING_LEVEL}')",
        default=consts.DEFAULT_LOGGING_LEVEL, type=str
    )
    parser.add_argument(
        '-d', '--dotenv-filepath', help=f"Set the dotenv-filepath (Default='{consts.DEFAULT_DOTENV_FILEPATH.resolve()}')",
        default=consts.DEFAULT_DOTENV_FILEPATH.resolve(), type=str
    )
    parser.add_argument(
        '-s', '--show-config', help="Show configuration and exit.", action="store_true"
    )
    args = parser.parse_args()
    #
    # Configure logging-module
    configure_logging(log_level=args.loglevel)
    #
    # Load dotenv configuration
    config:Config
    try:
        config = load_config(dotenv_filepath=Path(args.dotenv_filepath))
    except ConfigError:
        logger.exception("Couldn't load configuration! Abort.")
        quit(1)
    #
    # Handle CLI-arguments
    if args.show_config:
        show_config(config)
        quit(0)
    #
    # Get frequency and timestamp
    try:
        (frequency, timestamp) = website_utils.get_frequency_and_timestamp(
            url=config.data_source_api_url,
            http_requests_timeout=config.data_source_api_http_requests_timeout,
            requests_tls_verify=config.data_source_api_http_requests_tls_verify
        )
    except FrequencySourceWebsiteError:
        logger.exception("Couldn't get frequency and timestamp from data-source-API!")
        quit(1)
    #
    # Handle alert (if any)
    alert:Alert = get_alert(config=config, frequency=frequency, timestamp=timestamp)
    if alert.alert_type is not AlertType.NO_ALERT:
        try:
            send_ntfy_alert(config=config, alert=alert)
        except NTFYSendError:
            logger.exception(f"Couldn't send {'CRITICAL' if alert.alert_type == AlertType.CRITICAL_ALERT else 'WARNING'}-Alert")
            quit(1)
    else:
        logger.info(f"No threshold reached; No Alert required; Frequency={frequency}; Timestamp={timestamp}")

    logger.debug(f"Runtime={time.time()-_start} seconds")

if __name__ == '__main__':
    filename:str = os.path.basename(__file__)
    logger:logging.Logger = logging.getLogger(__name__)
    main()