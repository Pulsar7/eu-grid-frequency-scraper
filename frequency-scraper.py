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
            url=config.frequency_source_url,
            http_requests_timeout=config.frequency_source_http_requests_timeout,
            requests_tls_verify=config.frequency_source_http_requests_tls_verify
        )
    except FrequencySourceWebsiteError:
        logger.exception("Couldn't get frequency and timestamp from Frequency-Website")
        quit(1)
    #
    # Determine whether to send an alert message or not
    if frequency >= config.warning_max_hz_alert_threshold:
        logger.info(f"Reached MAX-Hz WARNING-threshold of {config.warning_max_hz_alert_threshold}Hz. Frequency={frequency}Hz ; Timestamp={timestamp}")
        #
        # Send out WARNING alert
        try:
            ntfy_utils.send_alert(
                topic_url=config.ntfy_topic_url,
                auth_token=config.ntfy_auth_token,
                http_requests_timeout=config.ntfy_http_requests_timeout,
                requests_tls_verify=config.ntfy_http_requests_tls_verify,
                title="WARNING MAX-Hz threshold reached",
                message=f"Warning MAX-Hz threshold of {config.warning_max_hz_alert_threshold}Hz reached.\n > {frequency}Hz\n > Timestamp={timestamp}",
                priority="urgent",
                tags="warning"
            )
        except NTFYSendError:
            logger.exception("Couldn't send WARNING-MAX-Alert")
            quit(1)
    elif frequency <= config.warning_min_hz_alert_threshold:
        logger.info(f"Reached MIN-Hz WARNING-threshold of {config.warning_min_hz_alert_threshold}Hz. Frequency={frequency}Hz ; Timestamp={timestamp}")
        #
        # Send out WARNING alert
        try:
            ntfy_utils.send_alert(
                topic_url=config.ntfy_topic_url,
                auth_token=config.ntfy_auth_token,
                http_requests_timeout=config.ntfy_http_requests_timeout,
                requests_tls_verify=config.ntfy_http_requests_tls_verify,
                title="WARNING MIN-Hz threshold reached",
                message=f"Warning MIN-Hz threshold of {config.warning_min_hz_alert_threshold}Hz reached.\n > {frequency}Hz\n > Timestamp={timestamp}",
                priority="urgent",
                tags="warning"
            )
        except NTFYSendError:
            logger.exception("Couldn't send WARNING-MIN-Alert")
            quit(1)
    elif frequency >= config.critical_max_hz_alert_threshold:
        logger.info(f"Reached MAX-Hz CRITICAL-threshold of {config.critical_max_hz_alert_threshold}Hz. Frequency={frequency}Hz ; Timestamp={timestamp}")
        #
        # Send out CRITICAL alert
        try:
            ntfy_utils.send_alert(
                topic_url=config.ntfy_topic_url,
                auth_token=config.ntfy_auth_token,
                http_requests_timeout=config.ntfy_http_requests_timeout,
                requests_tls_verify=config.ntfy_http_requests_tls_verify,
                title="CRITICAL MAX-Hz threshold reached",
                message=f"Warning MAX-Hz threshold of {config.critical_max_hz_alert_threshold}Hz reached.\n > {frequency}Hz\n > Timestamp={timestamp}",
                priority="urgent",
                tags="red-light"
            )
        except NTFYSendError:
            logger.exception("Couldn't send CRITICAL-MAX-Alert")
            quit(1)
    elif frequency <= config.critical_min_hz_alert_threshold:
        logger.info(f"Reached MIN-Hz CRITICAL-threshold of {config.critical_min_hz_alert_threshold}Hz. Frequency={frequency}Hz ; Timestamp={timestamp}")
        #
        # Send out CRITICAL alert
        try:
            ntfy_utils.send_alert(
                topic_url=config.ntfy_topic_url,
                auth_token=config.ntfy_auth_token,
                http_requests_timeout=config.ntfy_http_requests_timeout,
                requests_tls_verify=config.ntfy_http_requests_tls_verify,
                title="CRITICAL MIN-Hz threshold reached",
                message=f"Warning MIN-Hz threshold of {config.critical_min_hz_alert_threshold}Hz reached.\n > {frequency}Hz\n > Timestamp={timestamp}",
                priority="urgent",
                tags="red-light"
            )
        except NTFYSendError:
            logger.exception("Couldn't send CRITICAL-MIN-Alert")
            quit(1)
    else:
        logger.info(f"No threshold reached; frequency={frequency}Hz ; timestamp={timestamp}")

    logger.debug(f"Runtime={time.time()-_start} seconds")

if __name__ == '__main__':
    filename:str = os.path.basename(__file__)
    logger:logging.Logger = logging.getLogger(__name__)
    main()