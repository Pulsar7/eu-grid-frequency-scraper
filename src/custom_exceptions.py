class ConfigError(Exception):
    """
    Parent exception for Config related errors.
    """
    pass

class InvalidConfigError(ConfigError):
    """
    Raise when given Config is invalid.
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)

class InvalidMaxMinThresholdError(InvalidConfigError):
    """
    Raise when given max/min-warning/critical Hz alert-treshold is given.
    """
    def __init__(self, *args):
        super().__init__(*args)
        
class APIError(Exception):
    """
    Raise when scraping data from the API failed. 
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)
        
class NTFYError(Exception):
    """
    Raise when using NTFY failed.
    """
    def __init__(self, *args) -> None:
        super().__init__(*args)