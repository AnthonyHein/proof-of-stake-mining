import dill
import json
from typing import List

from known_states.known_state import KnownState
from known_states.known_states import known_states
from state import State

known_states: dict[State, KnownState] = known_states

if __name__ == "__main__":
    print("Do not run this file, run `test_known_states.py` instead!")