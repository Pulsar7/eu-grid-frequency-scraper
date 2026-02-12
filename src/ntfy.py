import requests
import logging
#
from src.custom_exceptions import NTFYError

class NTFYHandler:
    def __init__(self, topic_url:str, auth_token:str, requests_timeout:int, requests_cert_verify:bool) -> None:
        self.logger:logging.Logger = logging.getLogger(__class__.__name__)
        #
        self._topic_url:str = topic_url
        self._auth_token:str = auth_token
        self._requests_timeout:int = requests_timeout
        self._requests_cert_verify:bool = requests_cert_verify
    
    @property
    def topic_url(self) -> str:
        return self._topic_url
    
    @property
    def auth_token(self) -> str:
        return self._auth_token
    
    @property
    def requests_timeout(self) -> int:
        return self._requests_timeout
    
    @property
    def requests_cert_verify(self) -> bool:
        return self._requests_cert_verify
    
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
                verify=self.requests_cert_verify,
                timeout=self.requests_timeout
            )
            response.raise_for_status()
            
            self.logger.debug(f"Sent out alert to '{self.topic_url}' with HTTP-response-code={response.status_code}")
            
            return True
        except requests.RequestException as _e:
            raise NTFYError("NTFY request-error") from _e
        
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