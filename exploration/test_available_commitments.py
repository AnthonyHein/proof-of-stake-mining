import json
import sympy as sp
from typing import List

from commitment import *
from state import State
from state_utils import *

def main():

    states: List[State] = [
        State(),
        State(('A',)),
        State(('A', 'A')),
        State(('A', 'A', 'H', 'H')),
        State(('A', 'A', 'H', 'H', 'A')),
        State(('A', 'A', 'A')),
        State(('A', 'H', 'A', 'A')),
        State(('A', 'H', 'H', 'A', 'A', 'A')),
        State(('A', 'H', 'H', 'H', 'A', 'A')),
        State(('A', 'H', 'H', 'H', 'A', 'A', 'A')),
        State(('A', 'H', 'H', 'H', 'A', 'A', 'A', 'A')),
        State(('A', 'H', 'H', 'A', 'H', 'H', 'A', 'A')),
        State(('A', 'A', 'A', 'H', 'H', 'A', 'H', 'H', 'A', 'A')),
        State(('A', 'A', 'A', 'H', 'H', 'A', 'A', 'H', 'H', 'A', 'A')),
        State(('A', 'A', 'A', 'H', 'H', 'A', 'A', 'H', 'H', 'A', 'A', 'A', 'A', 'H',)),
        State(('A', 'H', 'H', 'H', 'A', 'H', 'A', 'A')),
        State(('A', 'A', 'A', 'H', 'H', 'H', 'H', 'A', 'H', 'H', 'A', 'A')),
        State(('A', 'A', 'A', 'H', 'H', 'H', 'H', 'A', 'H', 'H', 'A', 'A', 'A')),
        State(('A', 'A', 'A', 'H', 'H', 'H', 'H', 'H', 'A', 'H', 'H', 'A', 'A', 'A')),
        State(('A','A', 'H','H', 'H', 'A', 'A', 'A', 'H', 'H', 'H', 'H', 'H', 'A', 'H', 'H', 'A', 'A', 'A')),
    ]

    all_commitments: dict[State, List[Union[OneBoundaryCommitment, TwoBoundaryCommitment]]] = { state: get_available_commitments(state) for state in states}

    all_commitments_serializable: dict[str, List[object]] = {}

    for state, commitments in all_commitments.items():
        for commitment in commitments:
            commitment.update({
                "pr_lower_boundary": sp.latex(commitment["pr_lower_boundary"]) if "pr_lower_boundary" in commitment else "",
                "pr_upper_boundary": sp.latex(commitment["pr_upper_boundary"]) if "pr_upper_boundary" in commitment else "",
                "reward_at_boundary": sp.latex(commitment["reward_at_boundary"]) if "reward_at_boundary" in commitment else "",
                "reward_at_lower_boundary": sp.latex(commitment["reward_at_lower_boundary"]) if "reward_at_lower_boundary" in commitment else "",
                "reward_at_upper_boundary": sp.latex(commitment["reward_at_upper_boundary"]) if "reward_at_upper_boundary" in commitment else "",
            })
        all_commitments_serializable[str(state)] = commitments

    print(json.dumps(all_commitments_serializable, indent=4))

if __name__ == "__main__":
    main()