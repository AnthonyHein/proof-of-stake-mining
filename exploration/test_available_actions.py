import json

from known_states import known_states
from state import State
from state_utils import *

def main():

    depth = 9
    lut : dict[State, dict[State, str]] = {}

    def aux(state: State) -> None:
        if len(state) == depth:
            return

        if state in lut or len(get_checkpoints(state)) > 1:
            return

        lut[state] = {}

        available_actions = get_available_actions(state)

        for action in available_actions:
            subsequent_state = state.next_state_from_action(*action)

            lut[state][action] = str(subsequent_state)

            if state in known_states:
                continue

            aux(subsequent_state.next_state_attacker())
            aux(subsequent_state.next_state_honest_miner())

    aux(State())

    print(json.dumps({ str(state) : { str(action) : subsequent_state for action, subsequent_state in actions.items()} for state, actions in lut.items()}, indent=4))

if __name__ == "__main__":
    main()