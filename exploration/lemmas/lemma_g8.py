from typing import Optional

from bound import LemmaLowerBound, LemmaUpperBound
from lemmas.lemma import Lemma
from settings.setting import Setting
from state import State
from state_utils import *
from symbols import *

# Provides an upper bound to any state by considering the best that can be done to include 
# currently owned blocks that reach height less than that of the longest chain at the current state
# and the best that can be done over blocks that reach height greater than that of the longest chain
# at the current state.

class LemmaG8(Lemma):

    @staticmethod
    def get_name() -> str:
        """
        Return the name of the lemma.
        """
        return "Lemma G.8"

    @staticmethod
    def lower_bound(settings: Setting, state: State) -> Optional[LemmaLowerBound]:
        """
        Return the lower bound to the value of `state` that is achieved
        by this lemma as a function of alpha, or `None` if this lemma
        does not prove any such lower bound.
        """
        return None

    @staticmethod
    def upper_bound(settings: Setting, state: State) -> Optional[LemmaUpperBound]:
        """
        Return the upper bound to the value of `state` that is achieved
        by this lemma as a function of alpha, or `None` if this lemma
        does not prove any such upper bound.
        """
        height_of_longest_chain = len(state.get_longest_path()) - 1
        heights_unpublished_blocks_can_reach = get_heights_unpublished_blocks_can_reach(state)
        heights_unpublished_blocks_above_longest_chain = list(filter(lambda x: x > height_of_longest_chain, heights_unpublished_blocks_can_reach))

        deficits, runs = get_deficits_and_runs(state)

        deficits = [max(deficit - len(heights_unpublished_blocks_above_longest_chain), 0) for deficit in deficits]

        return {
            "lemma": LemmaG8.get_name(),
            "upper_bound": sum([runs[i] * (alpha / (1 - alpha)) ** deficits[i] for i in range(len(runs))]) + (len(heights_unpublished_blocks_above_longest_chain) + max(len(heights_unpublished_blocks_above_longest_chain) - 1, 0) * (alpha / (1 - 2 * alpha))) * (1 - alpha)
        }