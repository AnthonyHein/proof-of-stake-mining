import sys
from typing import Callable, List, TypedDict

class Setting(TypedDict):
    alpha_pos_lower_bound: float
    alpha_pos_upper_bound: float
    exploration_depth: int
    continue_from_known_states: bool
    display_known_states: bool
    recurse: bool
    save_as: str

def setting_isinstance(x: object, cls: Callable[[], None]) -> bool:
    keys = set()

    if cls == Setting:
        keys = set(["alpha_pos_lower_bound", "alpha_pos_upper_bound", "conjectures", "continue_from_known_states", "display_known_states", "exploration_depth", "recurse", "visualization"])

    else:
        print(f"setting.setting_isinstance: class {cls} can not be checked by this method")
        sys.exit(1)

    return isinstance(x, dict) and set(x.keys()) == keys