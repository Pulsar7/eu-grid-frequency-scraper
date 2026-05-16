import logging

logger:logging.Logger = logging.getLogger(__name__)

def is_valid_frequency_source_url(url:str) -> bool:
    """
    Check whether the provided URL can be a valid frequency-source-URL for this Script or not
    """
    if not url:
        logger.error("Provied an empty URL!")
        return False

    ### TODO ###
    # Regex check?
    
    return True