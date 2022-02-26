from enum import Enum, auto

class Action(Enum):
    WAIT = auto()
    PUBLISH_SET = auto()
    PUBLISH_PATH = auto()
    PUBLISH = auto()