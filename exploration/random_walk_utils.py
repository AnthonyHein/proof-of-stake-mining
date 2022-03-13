import sympy as sp
import sys
from typing import Tuple

from symbols import *

def get_random_walk_boundary_absorption_probabilities(initial_position: int,
                                                      lower_boundary: int,
                                                      upper_boundary: int) -> Tuple[sp.core.Expr, sp.core.Expr]:
    """
    Get the absorption probabilities of a random walk starting at `initial_position`
    with boundaries `lower_boundary` and `upper_boundary`, returned as a tuple of
    the form (lower boundary absorption pr., upper boundary absorption pr.).
    """
    if lower_boundary != 0:
        print(f"random_walk_utils.get_random_walk_boundary_absorption_probabilities: not implemented to handle lower boundary {lower_boundary}")
        sys.exit(1)

    pr_lower_boundary = (((1 - alpha) / alpha) ** upper_boundary - ((1 - alpha) / alpha) ** initial_position) / (((1 - alpha) / alpha) ** upper_boundary - 1)
    pr_upper_boundary = (((1 - alpha) / alpha) ** initial_position - 1) / (((1 - alpha) / alpha) ** upper_boundary - 1)

    return (pr_lower_boundary, pr_upper_boundary)

def get_random_walk_two_boundary_conditional_hitting_times(initial_position: int,
                                                           lower_boundary: int,
                                                           upper_boundary: int) -> Tuple[sp.core.Expr, sp.core.Expr]:
    """
    Get the conditional expected hitting times of a random walk starting at
    `initial_position` with boundaries `lower_boundary` and `upper_boundary`,
    returned as a tuple of the form (conditional expected hitting time given
    the walk hits the lower boundary, conditional expected hitting time given
    the walk hits the upper boundary).
    """
    if lower_boundary != 0:
        print(f"random_walk_utils.get_random_walk_two_boundary_conditional_hitting_times: not implemented to handle lower boundary {lower_boundary}")
        sys.exit(1)

    hitting_time_lower_boundary = (2 * alpha - 1) ** (-1) / (((1 - alpha) / alpha ) ** initial_position - ((1 - alpha) / alpha ) ** upper_boundary) * (initial_position * (((1 - alpha) / alpha ) ** initial_position + ((1 - alpha) / alpha ) ** upper_boundary) + 2 * upper_boundary * (((1 - alpha) / alpha ) ** (initial_position + upper_boundary) - ((1 - alpha) / alpha ) ** upper_boundary) / (1 - ((1 - alpha) / alpha) ** upper_boundary))
    hitting_time_upper_boundary = (2 * alpha - 1) ** (-1) / (1  -((1 - alpha) / alpha ) ** initial_position) * ((upper_boundary - initial_position) * (((1 - alpha) / alpha ) ** initial_position + 1) + 2 * upper_boundary * (((1 - alpha) / alpha ) ** initial_position - ((1 - alpha) / alpha ) ** upper_boundary) / (((1 - alpha) / alpha) ** upper_boundary - 1))

    return (hitting_time_lower_boundary, hitting_time_upper_boundary)

def get_random_walk_two_boundary_conditional_increments(initial_position: int,
                                                        lower_boundary: int,
                                                        upper_boundary: int) -> Tuple[sp.core.Expr, sp.core.Expr]:
    """
    Get the conditional expected increments for a random walk starting at
    `initial_position` with boundaries `lower_boundary` and `upper_boundary`,
    returned as a tuple of the form (conditional expected increments given
    the walk hits the lower boundary, conditional expected increments given
    the walk hits the upper boundary).
    """
    if lower_boundary != 0:
        print(f"random_walk_utils.get_random_walk_two_boundary_conditional_increments: not implemented to handle lower boundary {lower_boundary}")
        sys.exit(1)

    hitting_time_lower_boundary, hitting_time_upper_boundary = get_random_walk_two_boundary_conditional_hitting_times(initial_position, lower_boundary, upper_boundary)

    increments_lower_boundary = (hitting_time_lower_boundary - initial_position) / 2
    increments_upper_boundary = (hitting_time_upper_boundary + upper_boundary - initial_position) / 2

    return (increments_lower_boundary, increments_upper_boundary)

def get_random_walk_one_boundary_increments(initial_position: int,
                                            lower_boundary: int) -> sp.core.Expr:
    """
    Get the expected incremeents for a random walk starting at `initial_position`
    with boundary `lower_boundary` returned as an expression.
    """
    if lower_boundary != 0:
        print(f"random_walk_utils.get_random_walk_one_boundary_increments: not implemented to handle lower boundary {lower_boundary}")
        sys.exit(1)

    return initial_position * (alpha / (1 - 2 * alpha))