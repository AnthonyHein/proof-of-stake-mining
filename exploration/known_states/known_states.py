import dill

from known_states.known_state import KnownState
from state import State

known_states: dict[State, KnownState] = {

    State(("H",)): {
        "value_str": "0",
        "value_fn": dill.dumps(lambda alpha: 0),
    },

    State(("A", "A",) ): {
        "value_str": "\\big( 2 + (\\tfrac{\\alpha}{1 - 2\\alpha}) \\big)(1 - \\lambda)",
        "value_fn": dill.dumps(lambda alpha: (2 + (alpha / (1 - 2 * alpha))) * (1 - alpha)),
    },

    State(("A", "H", "A",)): {
        "value_str": "2 - \\alpha",
        "value_fn": dill.dumps(lambda alpha: 2 - alpha),
    },

    State(("A", "H", "H", "A","A",)): {
        "value_str": "3 - \\alpha",
        "value_fn": dill.dumps(lambda alpha: 3 - alpha),
    },

    State(("A", "H", "H", "A", "H", "A",)): {
        "value_str": "2 - \\alpha",
        "value_fn": dill.dumps(lambda alpha: 2 - alpha),
    },

    State(("A", "H", "H", "H", "A","A",)): {
        "value_str": "\\alpha( 4 - \\alpha) + (1 - \\alpha)(2 - 2\\alpha)",
        "value_fn": dill.dumps(lambda alpha: alpha * (4 - alpha) + (1 - alpha) * (2 - 2 * alpha)),
    },

    State(("A", "H", "H", "H", "A", "H", "A",)): {
        "value_str": "2 - \\alpha",
        "value_fn": dill.dumps(lambda alpha: 2 - alpha),
    },

    State(("A", "H", "H", "H", "H", "A","A",)): {
        "value_str": "\\tfrac{\\alpha^2}{1 - \\alpha + \\alpha^2}\\bigg(3 + (\\tfrac{2}{1 - \\alpha + \\alpha^2} + 2)/2 \\bigg)(1-\\alpha) + \\tfrac{1- \\alpha}{1 - \\alpha + \\alpha^2}\\bigg( \\big( 2 + (\\tfrac{1 + \\alpha - \\alpha^2}{1 - \\alpha + \\alpha^2} - 1)/2 \\big)(1 - \\alpha) - 4\\alpha \\bigg) - 4\\alpha",
        "value_fn": dill.dumps(lambda alpha: (alpha ** 2) / (1 - alpha + alpha ** 2) * (3 + (2 / (1 - alpha + alpha ** 2) + 2)/2 ) * (1- alpha) + (1- alpha) / (1 - alpha + alpha ** 2) * ( ( 2 + ( (1 + alpha - alpha ** 2) / (1 - alpha + alpha ** 2) - 1)/2 ) * (1 - alpha) - 4 * alpha ) - 4 * alpha),
    },

    State(("A", "H", "H", "H", "H", "A", "H", "A",)): {
        "value_str": "2 - \\alpha",
        "value_fn": dill.dumps(lambda alpha: 2 - alpha),
    },

    State(("A", "H", "H", "H", "H", "H",)): {
        "value_str": "0",
        "value_fn": dill.dumps(lambda alpha: 0),
    }

}