import json
from typing import List

from state import State

known_states: List[State] = [State(item["state"]) for item in json.load(open("known_states/known_states.json"))]

if __name__ == "__main__":
    print("Do not run this file, run `test_known_states.py` instead!")