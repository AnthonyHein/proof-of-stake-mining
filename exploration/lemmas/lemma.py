from typing import Callable, List, Tuple, Union

from conjectures.conjecture import Conjecture
from state import State

class Lemma:

    @staticmethod
    def get_name() -> str:
        """
        Return the name of the lemma.
        """
        pass

    @staticmethod
    def get_description() -> str:
        """
        Return a description of the lemma.
        """
        pass

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
        pass

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
        pass