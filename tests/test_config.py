"""

    eu-grid-frequency-scraper / Unit-tests / config-tests

"""
import pytest
from src.config import load_config
#
from src.custom_exceptions import InvalidConfigError

def test_invalid_http_timeout_below_zero(monkeypatch) -> None:
    """
    Test invalid `NTFY_HTTP_REQUEST_TIMEOUT` and `API_HTTP_REQUEST_TIMEOUT`
    
    - negative `int`
    """
    monkeypatch.setenv("NETZFREQUENZ_DE_API_URL", "https://netzfrequenz.localhost")
    monkeypatch.setenv("ENABLE_NTFY", "true")
    monkeypatch.setenv("NTFY_TOPIC_URL", "https://ntfy.localhost")
    monkeypatch.setenv("NTFY_AUTH_TOKEN", "abcdefgh")
    #
    # negative integer
    monkeypatch.setenv("NTFY_HTTP_REQUEST_TIMEOUT", "-1")
    monkeypatch.setenv("API_HTTP_REQUEST_TIMEOUT", "-1")
    #
    with pytest.raises(InvalidConfigError):
        load_config()

def test_invalid_http_timeout_string_instead_of_int(monkeypatch) -> None:
    """
    Test invalid `NTFY_HTTP_REQUEST_TIMEOUT` and `API_HTTP_REQUEST_TIMEOUT`
    
    - `string` instead of `int`
    """
    monkeypatch.setenv("NETZFREQUENZ_DE_API_URL", "https://netzfrequenz.localhost")
    monkeypatch.setenv("ENABLE_NTFY", "true")
    monkeypatch.setenv("NTFY_TOPIC_URL", "https://ntfy.localhost")
    monkeypatch.setenv("NTFY_AUTH_TOKEN", "abcdefgh")
    #
    # string instead of integer
    monkeypatch.setenv("NTFY_HTTP_REQUEST_TIMEOUT", "abc")
    monkeypatch.setenv("API_HTTP_REQUEST_TIMEOUT", "abc")
    #
    with pytest.raises(InvalidConfigError):
        load_config()

def test_invalid_hz_threshold_string_instead_of_float(monkeypatch) -> None:
    """
    Test invalid `MIN_HZ_ALERT_THRESHOLD` and `MAX_HZ_ALERT_THRESHOLD`
    
    - `string` instead of `float`
    """
    monkeypatch.setenv("NETZFREQUENZ_DE_API_URL", "https://netzfrequenz.localhost")
    #
    # string instead of float
    monkeypatch.setenv("MIN_HZ_ALERT_THRESHOLD", "abc")
    monkeypatch.setenv("MAX_HZ_ALERT_THRESHOLD", "abc")
    #
    with pytest.raises(InvalidConfigError):
        load_config()

def test_invalid_hz_threshold_max_below_min(monkeypatch) -> None:
    """
    Test invalid `MIN_HZ_ALERT_THRESHOLD` and `MAX_HZ_ALERT_THRESHOLD`
    
    - `MAX_HZ_ALERT_THRESHOLD` below `MIN_HZ_ALERT_THRESHOLD`
    """
    monkeypatch.setenv("NETZFREQUENZ_DE_API_URL", "https://netzfrequenz.localhost")
    #
    # `MAX_HZ_ALERT_THRESHOLD` below `MIN_HZ_ALERT_THRESHOLD`
    monkeypatch.setenv("MIN_HZ_ALERT_THRESHOLD", "30.33")
    monkeypatch.setenv("MAX_HZ_ALERT_THRESHOLD", "30.00")
    #
    with pytest.raises(InvalidConfigError):
        load_config() 