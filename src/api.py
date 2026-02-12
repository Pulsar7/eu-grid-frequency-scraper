import logging
import requests
import xml.etree.ElementTree as ET
#
from src.custom_exceptions import APIError

class APIHandler:
    def __init__(self, api_url:str, requests_timeout:int, requests_cert_verify:bool) -> None:
        self.logger:logging.Logger = logging.getLogger(__class__.__name__)
        #
        self._api_url:str = api_url
        self._requests_timeout:int = requests_timeout
        self._requests_cert_verify:bool = requests_cert_verify
        
    @property
    def api_url(self) -> str:
        return self._api_url
    
    @property
    def requests_timeout(self) -> int:
        return self._requests_timeout
    
    @property
    def requests_cert_verify(self) -> bool:
        return self._requests_cert_verify
    
    def get_api_data(self) -> tuple[float, str]:
        """
        Get data from Netzfrequenz-XML-API.
        
        Expected XML-data from the API:
        ```
        <r>
            <f>50.043</f>
            <z>2026-02-11T15:05:08+00:00</z>
        </r>
        
        Raises `APIError` if failed.
        """
        # Get data
        try:
            response = requests.get(
                url=self.api_url, 
                verify=self.requests_cert_verify,
                timeout=self.requests_timeout
            )
            response.raise_for_status()
            
            self.logger.debug(f"Got response.status_code={response.status_code} from '{self.api_url}', "
                              f"{len(response.content)} bytes")
        
        except requests.RequestException as _e:
            raise APIError("API request-error") from _e
        
        # Parse XML-data
        try:
            api_data = ET.fromstring(response.content)
        except ET.ParseError as _e:
            raise APIError("Couldn't parse API XML-data") from _e
        frequency:str|None = api_data.findtext('f')
        timestamp:str|None = api_data.findtext('z')
        if frequency is None or timestamp is None:
            self.logger.debug(f"Received XML-data: {response.content}")
            raise APIError("API XML-data doesn't contain expected keys")

        self.logger.debug(f"Received data from API: {api_data}, "
                            f"parsed frequency={frequency} and timestamp={timestamp} from XML-API data")

        try:
            frequency:float = float(frequency)
        except ValueError as _e:
            raise APIError("Invalid frequency value") from _e
        
        return (frequency, timestamp)
        
        