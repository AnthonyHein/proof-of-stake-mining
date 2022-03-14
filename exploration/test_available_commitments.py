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
                "commitment_str": commitment_str(commitment),
            })
        all_commitments_serializable[str(state)] = commitments

    print(json.dumps(all_commitments_serializable, indent=4))

if __name__ == "__main__":
    main()

# Because this has proven more difficult than anticipated, this is what I think
# the outout should be:

{
    "genesis": [],
    "(A)": [],
    "(2A)": [
        {
            "committed_blocks": [
                1,
                2
            ],
            "selfish_mining_blocks": [
                1,
                2
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 2\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(2A, 2H)": [],
    "(2A, 2H, A)": [],
    "(3A)": [
        {
            "committed_blocks": [
                1,
                2,
                3
            ],
            "selfish_mining_blocks": [
                1,
                2,
                3
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, H, 2A)": [
        {
            "committed_blocks": [
                1,
                3,
                4
            ],
            "selfish_mining_blocks": [
                3,
                4
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, 2H, 3A)": [
        {
            "committed_blocks": [
                4,
                5,
                6
            ],
            "selfish_mining_blocks": [
                4,
                5,
                6
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                1,
                4,
                5,
                6
            ],
            "selfish_mining_blocks": [
                5,
                6
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 4\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, 3H, 2A)": [
        {
            "committed_blocks": [
                5,
                6
            ],
            "selfish_mining_blocks": [
                5,
                6
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 2\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                5,
                6
            ],
            "selfish_mining_blocks": [
                5,
                6
            ],
            "recovered_blocks": [
                1
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{3}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "3 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{7}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ],
    "(A, 3H, 3A)": [
        {
            "committed_blocks": [
                5,
                6,
                7
            ],
            "selfish_mining_blocks": [
                5,
                6,
                7
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, 3H, 4A)": [
        {
            "committed_blocks": [
                5,
                6,
                7,
                8
            ],
            "selfish_mining_blocks": [
                5,
                6,
                7,
                8
            ],
            "initial_position": 3,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{3 \\alpha}{1 - 2 \\alpha} + 4\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                1,
                5,
                6,
                7,
                8
            ],
            "selfish_mining_blocks": [
                7,
                8
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "3 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 5\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, 2H, A, 2H, 2A)": [
        {
            "committed_blocks": [
                7,
                8
            ],
            "selfish_mining_blocks": [
                7,
                8
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 2\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                7,
                8
            ],
            "selfish_mining_blocks": [
                7,
                8
            ],
            "recovered_blocks": [
                1,
                4
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{3}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "4 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{9}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ],
    "(3A, 2H, A, 2H, 2A)": [
        {
            "committed_blocks": [
                1,
                2,
                3,
                6,
                9,
                10
            ],
            "selfish_mining_blocks": [
                9,
                10
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "4 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 6\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(3A, 2H, 2A, 2H, 2A)": [
        {
            "committed_blocks": [
                1,
                2,
                3,
                6,
                7,
                10,
                11
            ],
            "selfish_mining_blocks": [
                7,
                10,
                11
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "4 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 7\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(3A, 2H, 2A, 2H, 4A, H)": [
        {
            "committed_blocks": [
                1,
                2,
                3,
                6,
                7,
                10,
                11,
                12,
                13
            ],
            "selfish_mining_blocks": [
                10,
                11,
                12,
                13
            ],
            "initial_position": 3,
            "boundary": 0,
            "reward_at_boundary": "5 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{3 \\alpha}{1 - 2 \\alpha} + 9\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, 3H, A, H, 2A)": [
        {
            "committed_blocks": [
                5,
                7,
                8
            ],
            "selfish_mining_blocks": [
                7,
                8
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                5,
                7,
                8
            ],
            "selfish_mining_blocks": [
                7,
                8
            ],
            "recovered_blocks": [
                1
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "\\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{5}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "4 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{9}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ],
    "(3A, 4H, A, 2H, 2A)": [
        {
            "committed_blocks": [
                11,
                12
            ],
            "selfish_mining_blocks": [
                11,
                12
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 2\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                11,
                12
            ],
            "selfish_mining_blocks": [
                11,
                12
            ],
            "recovered_blocks": [
                1,
                2,
                3,
                8
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{3}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "6 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{13}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ],
    "(3A, 4H, A, 2H, 3A)": [
        {
            "committed_blocks": [
                11,
                12,
                13
            ],
            "selfish_mining_blocks": [
                11,
                12,
                13
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                8,
                11,
                12,
                13
            ],
            "selfish_mining_blocks": [
                12,
                13
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 4\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(3A, 5H, A, 2H, 3A)": [
        {
            "committed_blocks": [
                12,
                13,
                14
            ],
            "selfish_mining_blocks": [
                12,
                13,
                14
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                12,
                13,
                14
            ],
            "selfish_mining_blocks": [
                12,
                13,
                14
            ],
            "recovered_blocks": [
                1,
                2,
                3,
                9
            ],
            "initial_position": 2,
            "lower_boundary": 0,
            "upper_boundary": 3,
            "pr_lower_boundary": "\\frac{- \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(2 + \\frac{\\frac{- \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}} + \\frac{6 \\left(1 - \\alpha\\right)^{5}}{\\alpha^{5}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{2 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{2 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}\\right)}\\right)",
            "reward_at_upper_boundary": "7 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{15}{2} + \\frac{1 + \\frac{\\frac{6 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        },
        {
            "committed_blocks": [
                9,
                12,
                13,
                14
            ],
            "selfish_mining_blocks": [
                13,
                14
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 4\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                9,
                12,
                13,
                14
            ],
            "selfish_mining_blocks": [
                13,
                14
            ],
            "recovered_blocks": [
                1,
                2,
                3
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{7}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "7 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{15}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ],
    "(2A, 3H, 3A, 5H, A, 2H, 3A)": [
        {
            "committed_blocks": [
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                17,
                18,
                19
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                17,
                18,
                19
            ],
            "recovered_blocks": [
                6,
                7,
                8,
                14
            ],
            "initial_position": 2,
            "lower_boundary": 0,
            "upper_boundary": 3,
            "pr_lower_boundary": "\\frac{- \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(2 + \\frac{\\frac{- \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}} + \\frac{6 \\left(1 - \\alpha\\right)^{5}}{\\alpha^{5}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{2 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{2 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}\\right)}\\right)",
            "reward_at_upper_boundary": "7 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{15}{2} + \\frac{1 + \\frac{\\frac{6 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        },
        {
            "committed_blocks": [
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                17,
                18,
                19
            ],
            "recovered_blocks": [
                1,
                2,
                6,
                7,
                8,
                14
            ],
            "initial_position": 2,
            "lower_boundary": 0,
            "upper_boundary": 4,
            "pr_lower_boundary": "\\frac{- \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(2 + \\frac{\\frac{- \\frac{8 \\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}} + \\frac{8 \\left(1 - \\alpha\\right)^{6}}{\\alpha^{6}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}} + \\frac{2 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{2 \\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}\\right)}\\right)",
            "reward_at_upper_boundary": "10 \\alpha + \\left(1 - \\alpha\\right) \\left(10 + \\frac{2 + \\frac{\\frac{8 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{8 \\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}} + \\frac{2 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        },
        {
            "committed_blocks": [
                14,
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                18,
                19
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 4\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                14,
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                18,
                19
            ],
            "recovered_blocks": [
                6,
                7,
                8
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{7}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "7 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{15}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        },
        {
            "committed_blocks": [
                14,
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                18,
                19
            ],
            "recovered_blocks": [
                1,
                2,
                6,
                7,
                8
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 3,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "reward_at_lower_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{7}{2} + \\frac{\\frac{- \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}} + \\frac{6 \\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}\\right)}\\right)",
            "reward_at_upper_boundary": "10 \\alpha + \\left(1 - \\alpha\\right) \\left(10 + \\frac{2 + \\frac{\\frac{6 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{2 \\left(1 - \\alpha\\right)}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ]
}
