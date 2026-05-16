"""

    Custom Exceptions for this project

"""
class ConfigError(Exception):
    """
    Parent class for all Config related errors.
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)

class InvalidConfigError(ConfigError):
    """
    Raise when an invalid configuration is provided.
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)

class MissingConfigError(ConfigError):
    """
    Raise when a required configuration is not provided.
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)

class NTFYError(Exception):
    """
    Parent class for all NTFY related errors.
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)

class NTFYSendError(NTFYError):
    """
    Raise when an alert couldn't be send to a NTFY topic-URL.
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)
        
class FrequencySourceWebsiteError(Exception):
    """
    Parent class for all frequency-source-website related errors.
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)

class FrequencySourceWebsiteRequestError(FrequencySourceWebsiteError):
    """
    Raise when the HTTP-GET request at the frequency-source-website failed.
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)

class FrequencySourceWebsiteXMLParsingError(FrequencySourceWebsiteError):
    """
    Raise when parsing the XML-data from the frequency-source-website failed.
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)