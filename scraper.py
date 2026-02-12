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

def send_alert(level:str, min_or_max:str, frequency:float, threshold:float, timestamp:str, ntfy:None|NTFYHandler) -> bool:
    """
    Log and send NTFY alert if NTFY is enabled.
    """
    msg:str = f"{level.upper()}: Grid frequency {'reached' if frequency == threshold else 'is below'} {level.lower()}-{min_or_max.upper()}-threshold ({'<=' if min_or_max.lower() == 'min' else '>='} {threshold}Hz)"
    logger.info(f"[EVENT] {msg}")
    if config.enable_ntfy:
        try:
            ntfy.send_notification(
                title=f"{'REACHED' if frequency == threshold else 'BELOW'} {level.upper()} {min_or_max.upper()}-THRESHOLD",
                message=f"{msg}\n\n> Frequency={frequency}Hz\n> Timestamp={timestamp}",
                priority="urgent" if level.upper() == "CRITICAL" else "high",
                tags="rotating_light" if level.upper() == "CRITICAL" else "warning"
            )
        except NTFYError:
            logger.exception("Couldn't send alert to NTFY-instance!")
            return False
    
    return True

def check_frequency_thresholds(frequency:float, timestamp:str, ntfy:None|NTFYHandler) -> None:
    """
    Check if MIN-Hz or MAX-Hz WARNING/CRITICAL frequency thresholds have been reached.
    """
    #
    # CRITICAL
    #
    if frequency <= config.critical_min_hz_alert_threshold:
        if not send_alert(
                level="CRITICAL",
                min_or_max="MIN",
                frequency=frequency,
                threshold=config.critical_min_hz_alert_threshold,
                timestamp=timestamp,
                ntfy=ntfy
            ):
            logger.critical("Couldn't send alert!")
            quit(1)
    
    elif frequency >= config.critical_max_hz_alert_threshold:
        if not send_alert(
                level="CRITICAL",
                min_or_max="MAX",
                frequency=frequency,
                threshold=config.critical_max_hz_alert_threshold,
                timestamp=timestamp,
                ntfy=ntfy
            ):
            logger.critical("Couldn't send alert!")
            quit(1)
    
    #
    # WARNING
    #
    elif frequency <= config.warning_min_hz_alert_threshold:
        if not send_alert(
                level="WARNING",
                min_or_max="MIN",
                frequency=frequency,
                threshold=config.warning_min_hz_alert_threshold,
                timestamp=timestamp,
                ntfy=ntfy
            ):
            logger.critical("Couldn't send alert!")
            quit(1)
    
    elif frequency >= config.warning_max_hz_alert_threshold:
        if not send_alert(
                level="WARNING",
                min_or_max="MAX",
                frequency=frequency,
                threshold=config.warning_max_hz_alert_threshold,
                timestamp=timestamp,
                ntfy=ntfy
            ):
            logger.critical("Couldn't send alert!")
            quit(1)

def main() -> None:
    if args.show_alert_thresholds:
        logger.debug("Show alert thresholds and exit.")
        thresholds:str = f"""
        >------------------------------------------<
        > WARNING <
        - MIN={config.warning_min_hz_alert_threshold}Hz
        - MAX={config.warning_max_hz_alert_threshold}Hz
        
        > CRITICAL <
        - MIN={config.critical_min_hz_alert_threshold}Hz
        - MAX={config.critical_max_hz_alert_threshold}Hz
        >------------------------------------------<
        """
        print(thresholds)
        quit(0)
    
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
    parser.add_argument(
        '-s', '--show-alert-thresholds', help=f"Show CRITICAL/WARNING MIN/MAX alert thresholds and exit.",
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