from typing import Callable, List, Tuple, Union

from conjectures.conjecture import Conjecture
from lemmas.lemma import Lemma
from state import State


DESCRIPTION = \
"""
Provides an upper bound to any state by considering the best that can be done to include 
currently owned blocks that reach height less than that of the longest chain at the current state
and the best that can be done over blocks that reach height greater than that of the longest chain
at the current state.
"""

class Lemma_G8(Lemma):

    @staticmethod
    def get_name():
        """
        Return the name of the lemma.
        """
        return "Lemma G.8"

    @staticmethod
    def get_description():
        """
        Return a description of the lemma.
        """
        return DESCRIPTION

    @staticmethod
    def lower_bound(state: State,
                    conjectures: List[Conjecture],
                    alpha_pos_lb: float,
                    alpha_pos_ub: float) -> Union[Tuple[str, Callable[[float], float]], None]:
        """
        Return the lower bound to the value of `state` that is achieved
        by this lemma as a string formula and function of alpha, or `None`
        if this lemma does not prove any such lower bound.
        """
        return None

    @staticmethod
    def upper_bound(state: State,
                    conjectures: List[Conjecture],
                    alpha_pos_lb: float,
                    alpha_pos_ub: float) -> Union[Tuple[str, Callable[[float], float]], None]:
        """
        Return the upper bound to the value of `state` that is achieved
        by this lemma as a string formula and function of alpha, or `None`
        if this lemma does not prove any such upper bound.
        """
        def fn(alpha):
            return (2 + (alpha / (1 - 2 * alpha))) * (1 - alpha)

        return "(2 + (alpha / (1 - 2 * alpha))) * (1 - alpha)", fn

    

    
