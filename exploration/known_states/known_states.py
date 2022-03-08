import sympy as sp

from known_states.known_state import KnownState
from state import State
from symbols import *

known_states: dict[State, KnownState] = {

    State(("H",)): {
        "lower_bound": sp.Integer(0),
        "upper_bound": sp.Integer(0),
    },

    State(("A", "A",) ): {
        "lower_bound": (2 + (alpha / (1 - 2 * alpha))) * (1 - alpha),
        "upper_bound": (2 + (alpha / (1 - 2 * alpha))) * (1 - alpha),
    },

    State(("A", "H", "A",)): {
        "lower_bound": 2 - alpha,
        "upper_bound": 2 - alpha,
    },

    State(("A", "H", "H", "A", "A",)): {
        "lower_bound": 3 - alpha,
        "upper_bound": 3 - alpha,
    },

    State(("A", "H", "H", "A", "H", "A",)): {
        "lower_bound": 2 - alpha,
        "upper_bound": 2 - alpha,
    },

    State(("A", "H", "H", "H", "A","A",)): {
        "lower_bound": alpha * (4 - alpha) + (1 - alpha) * (2 - 2 * alpha),
        "upper_bound": alpha * (4 - alpha) + (1 - alpha) * (2 - 2 * alpha),
    },

    State(("A", "H", "H", "H", "A", "H", "A",)): {
        "lower_bound": 2 - alpha,
        "upper_bound": 2 - alpha,
    },

    State(("A", "H", "H", "H", "H", "A","A",)): {
        "lower_bound": (alpha ** 2 / (1 - alpha + alpha ** 2)) * (4 * alpha) + (alpha ** 2 / (1 - alpha + alpha ** 2)) * ((3 + (2 / (1 - alpha + alpha ** 2)) + 2) / 2) * (1 - alpha) + ((1 - alpha) / (1 - alpha + alpha ** 2)) * ( (2 + ( ((1 + alpha - alpha ** 2) / (1 - alpha + alpha ** 2)) - 1 / 2)) * (1 - alpha)),
        "upper_bound": (alpha ** 2 / (1 - alpha + alpha ** 2)) * (4 * alpha) + (alpha ** 2 / (1 - alpha + alpha ** 2)) * ((3 + (2 / (1 - alpha + alpha ** 2)) + 2) / 2) * (1 - alpha) + ((1 - alpha) / (1 - alpha + alpha ** 2)) * ( (2 + ( ((1 + alpha - alpha ** 2) / (1 - alpha + alpha ** 2)) - 1 / 2)) * (1 - alpha)),
    },

    State(("A", "H", "H", "H", "H", "A", "H", "A",)): {
        "lower_bound": 2 - alpha,
        "upper_bound": 2 - alpha,
    },

    State(("A", "H", "H", "H", "H", "H",)): {
        "lower_bound": sp.Integer(0),
        "upper_bound": sp.Integer(0),
    }

}