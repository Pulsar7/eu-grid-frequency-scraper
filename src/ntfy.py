import requests
import logging
#
from src.custom_exceptions import NTFYError

class NTFYHandler:
    def __init__(self, topic_url:str, auth_token:str, requests_timeout:int) -> None:
        self.logger = logging.getLogger(__class__.__name__)
        #
        self._topic_url:str = topic_url
        self._auth_token:str = auth_token
        self._requests_timeout:int = requests_timeout
    
    @property
    def topic_url(self) -> str:
        return self._topic_url
    
    @property
    def auth_token(self) -> str:
        return self._auth_token
    
    @property
    def requests_timeout(self) -> int:
        return self._requests_timeout
    
    def send_notification(self, title:str, message:str, priority:str, tags:str) -> bool:
        """
        Send HTTP-Post request to configured NTFY-topic-URL
        """
        try:
            headers:dict = {
                'Title': title,
                'Priority': priority,
                'Tags': tags,
                'Authorization': f"Bearer {self.auth_token}"
            }
            response = requests.post(
                url=self.topic_url,
                data=message,
                headers=headers,
                verify=False,
                timeout=self.requests_timeout
            )
            if response.status_code != 200:
                err_msg:str = f"Got an invalid response code ('{response.status_code}') from NTFY!"
                if response.status_code == 401:
                    err_msg += " (Looks like the authentication-token is incorrect)"
                raise NTFYError(err_msg)
            
            return True
            
        except requests.ConnectionError as _e:
            raise NTFYError("Connection Error!") from _e
        
        except requests.ConnectTimeout as _e:
            err_msg:str = f"Connection Timeout"
            if self.requests_timeout <= 3:
                err_msg += " (Your request-timeout may be too low)"
            raise NTFYError(err_msg) from _e

        except Exception as _e:
            raise NTFYError("An unexpected error occured") from _e
        
    def test_config(self) -> bool:
        """
        Test given NTFY topic-URL and authentication-token.
        """
        try:
            self.send_notification(
                title="Test notification",
                message="This is just a test notification of the eu-grid-frequency-scraper script.",
                priority="urgent",
                tags="warning"
            )
            return True
        except NTFYError:
            self.logger.exception("Test notification failed!")
            return False