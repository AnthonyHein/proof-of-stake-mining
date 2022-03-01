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
                    settings: dict[str, object],
                    conjectures: List[Conjecture]) -> Union[Tuple[str, Callable[[float], float]], None]:
        """
        Return the lower bound to the value of `state` that is achieved
        by this lemma as a string formula and function of alpha, or `None`
        if this lemma does not prove any such lower bound.
        """
        pass

    @staticmethod
    def upper_bound(state: State,
                    settings: dict[str, object],
                    conjectures: List[Conjecture]) -> Union[Tuple[str, Callable[[float], float]], None]:
        """
        Return the upper bound to the value of `state` that is achieved
        by this lemma as a string formula and function of alpha, or `None`
        if this lemma does not prove any such upper bound.
        """
        pass