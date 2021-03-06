from typing import Optional

from bound import LemmaLowerBound, LemmaUpperBound
from settings.setting import Setting
from state import State

# NOTE: Lemmas should _only_ be applied to states where all checkpoints have
# already been processed.

class Lemma:

    @staticmethod
    def get_name() -> str:
        """
        Return the name of the lemma.
        """
        pass

    @staticmethod
    def lower_bound(settings: Setting, state: State) -> Optional[LemmaLowerBound]:
        """
        Return the lower bound to the value of `state` that is achieved
        by this lemma as a function of alpha, or `None` if this lemma
        does not prove any such lower bound.
        """
        pass

    @staticmethod
    def upper_bound(settings: Setting, state: State) -> Optional[LemmaUpperBound]:
        """
        Return the upper bound to the value of `state` that is achieved
        by this lemma as a function of alpha, or `None` if this lemma
        does not prove any such upper bound.
        """
        pass