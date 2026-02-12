"""

    eu-grid-frequency-scraper / Unit-tests / config-tests

"""
import pytest
import src.config as config 
#
from src.custom_exceptions import *

def set_default_env(monkeypatch) -> None:
    """
    Set default valid configuration.
    """
    monkeypatch.setenv("NETZFREQUENZ_DE_API_URL", "https://netzfrequenz.invalid")
    
    monkeypatch.setenv("ENABLE_NTFY", "true")
    monkeypatch.setenv("NTFY_TOPIC_URL", "https://ntfy.invalid")
    monkeypatch.setenv("NTFY_AUTH_TOKEN", "abcdefgh")
    monkeypatch.setenv("NTFY_HTTP_REQUEST_TIMEOUT", "10")
    
    monkeypatch.setenv("WARNING_MIN_HZ_ALERT_THRESHOLD", "1.5")
    monkeypatch.setenv("WARNING_MAX_HZ_ALERT_THRESHOLD", "2.0")
    
    monkeypatch.setenv("CRITICAL_MIN_HZ_ALERT_THRESHOLD", "1.0")
    monkeypatch.setenv("CRITICAL_MAX_HZ_ALERT_THRESHOLD", "2.5")

    monkeypatch.setenv("API_HTTP_REQUEST_TIMEOUT", "10")

#------------------------------------------------------------------------------------
# INTEGER below ZERO
#------------------------------------------------------------------------------------

def test_invalid_http_timeout_below_zero(monkeypatch) -> None:
    """
    Test invalid `NTFY_HTTP_REQUEST_TIMEOUT` and `API_HTTP_REQUEST_TIMEOUT`

    - negative `int`
    """
    set_default_env(monkeypatch)
    #
    # negative integer
    monkeypatch.setenv("NTFY_HTTP_REQUEST_TIMEOUT", "-1")
    monkeypatch.setenv("API_HTTP_REQUEST_TIMEOUT", "-1")
    #
    with pytest.raises(InvalidConfigError):
        config.load_config()


#------------------------------------------------------------------------------------
# STRING instead of INTEGER/FLOAT
#------------------------------------------------------------------------------------

def test_invalid_http_timeout_string_instead_of_int(monkeypatch) -> None:
    """
    Test invalid `NTFY_HTTP_REQUEST_TIMEOUT` and `API_HTTP_REQUEST_TIMEOUT`

    - `string` instead of `int`
    """
    set_default_env(monkeypatch)
    #
    # string instead of integer
    monkeypatch.setenv("NTFY_HTTP_REQUEST_TIMEOUT", "abc")
    monkeypatch.setenv("API_HTTP_REQUEST_TIMEOUT", "abc")
    #
    with pytest.raises(InvalidConfigError):
        config.load_config()

def test_invalid_warning_min_hz_threshold_string_instead_of_float(monkeypatch) -> None:
    """
    Test invalid `WARNING_MIN_HZ_ALERT_THRESHOLD`

    - `string` instead of `float`
    """
    set_default_env(monkeypatch)
    #
    # string instead of float
    monkeypatch.setenv("WARNING_MIN_HZ_ALERT_THRESHOLD", "abc")
    #
    with pytest.raises(InvalidConfigError):
        config.load_config()

def test_invalid_warning_max_hz_threshold_string_instead_of_float(monkeypatch) -> None:
    """
    Test invalid `WARNING_MAX_HZ_ALERT_THRESHOLD`

    - `string` instead of `float`
    """
    set_default_env(monkeypatch)
    #
    # string instead of float
    monkeypatch.setenv("WARNING_MAX_HZ_ALERT_THRESHOLD", "abc")
    #
    with pytest.raises(InvalidMaxMinThresholdError):
        config.load_config()

def test_invalid_critical_max_hz_threshold_string_instead_of_float(monkeypatch) -> None:
    """
    Test invalid `CRITICAL_MAX_HZ_ALERT_THRESHOLD`

    - `string` instead of `float`
    """
    set_default_env(monkeypatch)
    #
    # string instead of float
    monkeypatch.setenv("CRITICAL_MAX_HZ_ALERT_THRESHOLD", "abc")
    #
    with pytest.raises(InvalidMaxMinThresholdError):
        config.load_config()

def test_invalid_critical_min_hz_threshold_string_instead_of_float(monkeypatch) -> None:
    """
    Test invalid `CRITICAL_MIN_HZ_ALERT_THRESHOLD`

    - `string` instead of `float`
    """
    set_default_env(monkeypatch)
    #
    # string instead of float
    monkeypatch.setenv("CRITICAL_MIN_HZ_ALERT_THRESHOLD", "abc")
    #
    with pytest.raises(InvalidMaxMinThresholdError):
        config.load_config()


#------------------------------------------------------------------------------------
# Invalid CRITICAL-HZ-THRESHOLDs
#------------------------------------------------------------------------------------

def test_invalid_critical_hz_threshold_max_below_min(monkeypatch) -> None:
    """
        `CRITICAL_MAX_HZ_ALERT_THRESHOLD` below `CRITICAL_MIN_HZ_ALERT_THRESHOLD`
    """
    set_default_env(monkeypatch)
    #
    monkeypatch.setenv("CRITICAL_MIN_HZ_ALERT_THRESHOLD", "30.33")
    monkeypatch.setenv("CRITICAL_MAX_HZ_ALERT_THRESHOLD", "30.00")
    #
    with pytest.raises(InvalidMaxMinThresholdError):
        config.load_config()
        
def test_invalid_critical_hz_threshold_max_equals_min(monkeypatch) -> None:
    """
        `CRITICAL_MAX_HZ_ALERT_THRESHOLD` equals `CRITICAL_MIN_HZ_ALERT_THRESHOLD`
    """
    set_default_env(monkeypatch)
    #
    monkeypatch.setenv("CRITICAL_MIN_HZ_ALERT_THRESHOLD", "30.33")
    monkeypatch.setenv("CRITICAL_MAX_HZ_ALERT_THRESHOLD", "30.33")
    #
    with pytest.raises(InvalidMaxMinThresholdError):
        config.load_config()


#------------------------------------------------------------------------------------
# Invalid WARNING-Hz-THRESHOLDs
#------------------------------------------------------------------------------------

def test_invalid_warning_hz_threshold_max_below_min(monkeypatch) -> None:
    """
        `WARNING_MAX_HZ_ALERT_THRESHOLD` below `WARNING_MIN_HZ_ALERT_THRESHOLD`
    """
    set_default_env(monkeypatch)
    #
    monkeypatch.setenv("WARNING_MIN_HZ_ALERT_THRESHOLD", "30.33")
    monkeypatch.setenv("WARNING_MAX_HZ_ALERT_THRESHOLD", "30.00")
    #
    with pytest.raises(InvalidMaxMinThresholdError):
        config.load_config()

def test_invalid_warning_hz_threshold_max_equals_min(monkeypatch) -> None:
    """
        `WARNING_MAX_HZ_ALERT_THRESHOLD` equals `WARNING_MIN_HZ_ALERT_THRESHOLD`
    """
    set_default_env(monkeypatch)
    #
    monkeypatch.setenv("WARNING_MIN_HZ_ALERT_THRESHOLD", "30.33")
    monkeypatch.setenv("WARNING_MAX_HZ_ALERT_THRESHOLD", "30.33")
    #
    with pytest.raises(InvalidMaxMinThresholdError):
        config.load_config()

def test_invalid_hz_threshold_min_warning_equals_min_critical(monkeypatch) -> None:
    """
        `CRITICAL_MIN_HZ_ALERT_THRESHOLD` equals `WARNING_MIN_HZ_ALERT_THRESHOLD`
    """
    set_default_env(monkeypatch)
    #
    monkeypatch.setenv("CRITICAL_MIN_HZ_ALERT_THRESHOLD", "")
    monkeypatch.setenv("WARNING_MIN_HZ_ALERT_THRESHOLD", "")
    #
    with pytest.raises(InvalidMaxMinThresholdError):
        config.load_config()
        
def test_invalid_hz_threshold_min_warning_below_min_critical(monkeypatch) -> None:
    """
        `WARNING_MIN_HZ_ALERT_THRESHOLD` below `CRITICAL_MIN_HZ_ALERT_THRESHOLD`
    """
    set_default_env(monkeypatch)
    #
    monkeypatch.setenv("CRITICAL_MIN_HZ_ALERT_THRESHOLD", "1.5")
    monkeypatch.setenv("WARNING_MIN_HZ_ALERT_THRESHOLD", "1.0")
    #
    with pytest.raises(InvalidMaxMinThresholdError):
        config.load_config()

def test_invalid_hz_threshold_max_warning_above_max_critical(monkeypatch) -> None:
    """
        `WARNING_MAX_HZ_ALERT_THRESHOLD` above `CRITICAL_MAX_HZ_ALERT_THRESHOLD`
    """
    set_default_env(monkeypatch)
    #
    monkeypatch.setenv("WARNING_MAX_HZ_ALERT_THRESHOLD", "2.5")
    monkeypatch.setenv("CRITICAL_MAX_HZ_ALERT_THRESHOLD", "2.0")
    #
    with pytest.raises(InvalidMaxMinThresholdError):
        config.load_config()