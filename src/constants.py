from enum import Enum
from pathlib import Path
from dataclasses import dataclass

class AlertType(Enum):
    WARNING_ALERT=0
    CRITICAL_ALERT=1
    NO_ALERT=2

@dataclass(frozen=True)
class Alert:
    alert_type:AlertType
    alert_title:str
    alert_msg:str

#
# Default CLI-arguments
#
DEFAULT_LOGGING_LEVEL:str = "debug"
DEFAULT_DOTENV_FILEPATH:Path = Path("./.env")