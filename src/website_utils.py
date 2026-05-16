import logging
import requests
import xml.etree.ElementTree as ET
#
from src.exceptions import *

logger:logging.Logger = logging.getLogger(__name__)

def get_xml_data(url:str, http_requests_timeout:str, requests_tls_verify:bool) -> bytes:
    """
    Get XML-data from Frequency-Source-Website and return content as bytes.
    
    Raises `FrequencySourceWebsiteRequestError` when an error occured.
    """
    logger.debug(f"HTTP-GET '{url}'...")
    try:
        response = requests.get(
            url=url,
            verify=requests_tls_verify,
            timeout=http_requests_timeout
        )
        response.raise_for_status()
    except requests.RequestException as _e:
        raise FrequencySourceWebsiteRequestError(f"Couldn't get XML-Data from Frequency-Source-Website '{url}'") from _e
    
    content = response.content
    logger.debug(f"Got {len(content)} Bytes as response-content")
    
    if len(content) == 0:
        raise FrequencySourceWebsiteRequestError(f"Received content from '{url}' is empty!")
    
    return content

def parse_xml_data(content:bytes) -> tuple[float, str]:
    """
    Parse XML-data from Frequency-Source-Website and return tuple of frequency and timestamp.
    
    Expected XML-data from the API:
    ```
    <r>
        <f>50.043</f>
        <z>2026-02-11T15:05:08+00:00</z>
    </r>
    ```
    
    Raises `FrequencySourceWebsiteXMLParsingError` when an error occured. 
    """
    try:
        xml_data = ET.fromstring(content)
    except ET.ParseError as _e:
        raise FrequencySourceWebsiteXMLParsingError("Couldn't parse XML-data") from _e
    #
    # Parse frequency- and timestamp-string
    frequency_string:str|None = xml_data.findtext('f')
    if not frequency_string:
        logger.debug(f"Parsed XML-data:\n{xml_data}\n")
        raise FrequencySourceWebsiteXMLParsingError(f"Couldn't parse frequency from XML-data!")
    try:
        frequency:float = float(frequency_string)
    except (ValueError, TypeError) as _e:
        logger.debug(f"Parsed XML-data:\n{xml_data}\n")
        raise FrequencySourceWebsiteXMLParsingError(f"Parsed frequency-string from XML-data is not valid: frequency_string='{frequency_string}'") from _e
    
    timestamp:str|None = xml_data.findtext('z')
    if not timestamp:
        logger.debug(f"Parsed XML-data:\n{xml_data}\n")
        raise FrequencySourceWebsiteXMLParsingError(f"Couldn't parse timestamp from XML-data!")
    
    return (frequency, timestamp)

def get_frequency_and_timestamp(url:str, http_requests_timeout:str, requests_tls_verify:bool) -> tuple[float, str]:
    """
    Calls helper functions and doesn't catch their exceptions!
    """
    return parse_xml_data(
        content=get_xml_data(url=url, http_requests_timeout=http_requests_timeout, 
                             requests_tls_verify=requests_tls_verify)
    )