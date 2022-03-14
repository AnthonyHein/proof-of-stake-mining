from known_states import known_states
from state import State
from state_utils import *

def main():

    depth = 10
    lut : dict[State, dict[State, str]] = {}

    def aux(state: State) -> None:
        if len(state) > depth:
            return

        print(state, pretty_state_str(state), "<br />")

        if state in lut or len(get_checkpoints(state)) > 1:
            return

        available_actions = get_available_actions(state)

        for action in available_actions:
            subsequent_state = state.next_state_from_action(*action)

            if state in known_states:
                continue

            aux(subsequent_state.next_state_attacker())
            aux(subsequent_state.next_state_honest_miner())

    aux(State())

if __name__ == "__main__":
    main()