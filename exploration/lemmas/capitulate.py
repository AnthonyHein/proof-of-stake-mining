import sympy as sp
from typing import Optional

from bound import LemmaLowerBound, LemmaUpperBound
from lemmas.lemma import Lemma
from settings.setting import Setting
from state import State

# Provides a lower bound to any state by simply capitulating to $B_0$.

class Capitulate(Lemma):

    @staticmethod
    def get_name() -> str:
        """
        Return the name of the lemma.
        """
        return "Capitulate"

    @staticmethod
    def lower_bound(settings: Setting, state: State) -> Optional[LemmaLowerBound]:
        """
        Return the lower bound to the value of `state` that is achieved
        by this lemma as a function of alpha, or `None` if this lemma
        does not prove any such lower bound.
        """
        return {
            "lemma": Capitulate.get_name(),
            "lower_bound": sp.Integer(0),
        }

    @staticmethod
    def upper_bound(settings: Setting, state: State) -> Optional[LemmaUpperBound]:
        """
        Return the upper bound to the value of `state` that is achieved
        by this lemma as a function of alpha, or `None` if this lemma
        does not prove any such upper bound.
        """
        return None