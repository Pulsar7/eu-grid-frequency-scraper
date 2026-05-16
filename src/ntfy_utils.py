import logging
import requests
#
from src.exceptions import *

logger:logging.Logger = logging.getLogger(__name__)

def send_alert(topic_url:str, auth_token:str, http_requests_timeout:str, requests_tls_verify:bool, title:str, 
               message:str, priority:str, tags:str) -> None:
    """
    Sends alert-message to provided topic-URL, using HTTP-Post-request.
    
    Raises `NTFYSendError` when sending the alert-message failed.
    """
    logger.debug(f"Sending alert to NTFY-Topic-URL '{topic_url}'...")
    headers:dict = {
        'Title': title,
        'Priority': priority,
        'Tags': tags,
        'Authorization': f"Bearer {auth_token}"
    }
    try:
        response = requests.post(
            url=topic_url,
            data=message,
            headers=headers,
            verify=requests_tls_verify,
            timeout=http_requests_timeout
        )
        response.raise_for_status()
    except requests.RequestException as _e:
        raise NTFYSendError("Couldn't send alert to NTFY-topic-URL!") from _e

    logger.info(f"Successfully sent alert to NTFY-Topic-URL '{topic_url}'")