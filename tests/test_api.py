"""

    eu-grid-frequency-scraper / Unit-tests / api-tests

"""
import pytest
#
from src.api import APIHandler
from src.custom_exceptions import *

def get_apihandler_obj(api_url:str) -> APIHandler:
    return APIHandler(
        api_url=api_url,
        requests_timeout=10,
        requests_cert_verify=True
    )

def test_invalid_netzfrequenz_api_url() -> None:
    """
    Test invalid netzfrequenz API-URL.
    """
    api_handler:APIHandler = get_apihandler_obj(api_url="https://www.netzfrequenzmessung.invalid")
    #
    with pytest.raises(APIRequestError):
        api_handler.get_api_data()