"""

    EU Grid frequency scraper and notifier.

    # Script-Version: 1.0
    # Python-Version: 3.10.12

"""
import os
import time
import logging
import argparse
#
import src.utils as utils
from src.api import APIHandler
from src.ntfy import NTFYHandler
from src.custom_exceptions import *
from src.config import load_config, Config
from src.logger_config import configure_logger

def check_frequency_thresholds(frequency:float, timestamp:str, ntfy:None|NTFYHandler) -> None:
    """
    Check and send alert if MIN-Hz or MAX-Hz frequency threshold has been reached and NTFY is enabled.
    """
    if frequency <= config.min_hz_alert_threshold:
        logger.info(f"[EVENT] Grid frequency is below MIN-threshold (< {config.min_hz_alert_threshold}Hz)")
        if config.enable_ntfy:
            ntfy.send_notification(
                title="FREQUENCY BELOW THRESHOLD",
                message=f"Grid frequency is below MIN-threshold (< {config.min_hz_alert_threshold}Hz)\n\n> Frequency={frequency}\n> Timestamp={timestamp}",
                priority="urgent", # max
                tags="warning"
            )
    
    elif frequency >= config.max_hz_alert_threshold:
        logger.info(f"[EVENT] Grid frequency is above MAX-threshold (< {config.max_hz_alert_threshold}Hz)")
        if config.enable_ntfy:
            ntfy.send_notification(
                title="FREQUENCY ABOVE THRESHOLD",
                message=f"Grid frequency is above MAX-threshold (> {config.max_hz_alert_threshold}Hz)\n\n> Frequency={frequency}\n> Timestamp={timestamp}",
                priority="urgent", # max
                tags="warning"
            )

def main() -> None:
    ntfy = None
    if config.enable_ntfy:
        ntfy = NTFYHandler(
            topic_url=config.ntfy_topic_url,
            auth_token=config.ntfy_auth_token,
            requests_timeout=config.ntfy_http_request_timeout,
            requests_cert_verify=config.ntfy_http_request_cert_verify
        )
        logger.debug(f"Using NTFY '{ntfy.topic_url}' for notifications")
    else:
        logger.warning("NTFY is disabled.")
    
    if args.test_ntfy and config.enable_ntfy:
        logger.info("Test NTFY-configuration and exit.")
        if not ntfy.test_config():
            logger.critical("Your current NTFY-configuration failed.")
            quit(1)
        else:
            logger.info("Your current NTFY-configuration seems fine.")
            quit(0)
    elif args.test_ntfy and not config.enable_ntfy:
        logger.critical("Cannot test NTFY-configuration, when NTFY is disabled!")
        quit(1)
        
    apihandler = APIHandler(
        api_url=config.api_url,
        requests_timeout=config.api_http_request_timeout,
        requests_cert_verify=config.api_http_request_cert_verify
    )
    
    try:
        (frequency, timestamp) = apihandler.get_api_data()
    except APIError:
        logger.exception("Couldn't get frequency and timestamp from API!")
        quit(1)
    
    logger.info(f"Frequency={frequency} | Timestamp={timestamp}")

    check_frequency_thresholds(frequency, timestamp, ntfy)
    
    logger.debug(f"Runtime={time.time()-_start} seconds")

if __name__ == '__main__':
    _start:float = time.time()
    
    filename:str = os.path.basename(__file__)
    parser = argparse.ArgumentParser(filename)
    DEFAULT_LOGLEVEL:str = "DEBUG"
    parser.add_argument(
        '-l', '--loglevel', help=f"Log level (Default={DEFAULT_LOGLEVEL})",
        default=DEFAULT_LOGLEVEL
    )
    parser.add_argument(
        '-t', '--test-ntfy', help=f"Test NTFY-configuration by sending a test-notification.",
        action="store_true"
    )
    args:list = parser.parse_args()
    
    configure_logger(args.loglevel.upper())
    logger:logging.Logger = logging.getLogger(__name__)
    
    try:
        logger.debug(f"Using dotenv-filepath '{utils.get_dotenv_filepath().absolute()}'")
        config:Config = load_config()
    except ConfigError:
        logger.exception("Got invalid configuration.")
        quit(1)
    
    main()