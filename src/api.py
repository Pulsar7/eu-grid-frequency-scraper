import logging
import requests
import xml.etree.ElementTree as ET
#
from src.custom_exceptions import APIError

class APIHandler:
    def __init__(self, api_url:str, requests_timeout:int) -> None:
        self.logger:logging.Logger = logging.getLogger(__class__.__name__)
        #
        self._api_url:str = api_url
        self._requests_timeout:int = requests_timeout
        
    @property
    def api_url(self) -> str:
        return self._api_url
    
    @property
    def requests_timeout(self) -> int:
        return self._requests_timeout
    
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
        try:
            response = requests.get(url=self._api_url, verify=True,
                                    timeout=self.requests_timeout)
            if response.status_code != 200:
                err_msg:str = f"Got an invalid response code ('{response.status_code}') from API!"
                # TODO: Limit exceeded warn-message
                raise APIError(err_msg)
            
            self.logger.debug(f"Got response.status_code={response.status_code} from '{self._api_url}'")
            self.logger.debug(f"Got {len(response.content)} Bytes of data from API")
            
            try:
                api_data = ET.fromstring(response.content)
                frequency = api_data.find('f').text
                timestamp = api_data.find('z').text
                self.logger.debug(f"Received data from API: {api_data}")
                self.logger.debug(f"Got frequency={frequency} and timestamp={timestamp} from XML-API data")
            except Exception as _e:
                raise APIError("Couldn't parse API-XML-data") from _e
            
            try:
                frequency:float = float(frequency)
            except ValueError as _e:
                raise APIError("Got invalid frequency!") from _e
            
            return (frequency, timestamp)
            
        except requests.ConnectionError as _e:
            raise APIError("API Connection Error!") from _e
        
        except requests.ConnectTimeout as _e:
            err_msg:str = f"API Connection Timeout"
            if self.requests_timeout <= 3:
                err_msg += " (Your request-timeout may be too low)"
            raise APIError(err_msg) from _e

        except Exception as _e:
            raise APIError("An unexpected error occured") from _e
