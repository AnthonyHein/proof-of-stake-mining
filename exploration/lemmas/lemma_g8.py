from typing import Optional

from sympy import symbols

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
        height_of_longest_chain = len(state.get_longest_path())
        heights_attacker_blocks_can_reach = get_heights_unpublished_blocks_can_reach(state)

        attacker_blocks_below_longest_chain = list(filter(lambda x: x <= height_of_longest_chain, heights_attacker_blocks_can_reach))
        attacker_blocks_above_longest_chain = list(filter(lambda x: x > height_of_longest_chain, heights_attacker_blocks_can_reach))

        deficits = []
        runs = []

        curr_deficit = 1
        curr_run = 0

        for i in range(height_of_longest_chain, 0, -1):
            if i in attacker_blocks_below_longest_chain:
                curr_run += 1

            else:
                if curr_run > 0:
                    deficits.append(max(curr_deficit - len(attacker_blocks_above_longest_chain), 0))
                    runs.append(curr_run)
                curr_run = 0
                curr_deficit += 1

        if curr_run > 0:
            deficits.append(max(curr_deficit - len(attacker_blocks_above_longest_chain), 0))
            runs.append(curr_run)

        return {
            "lemma": LemmaG8.get_name(),
            "upper_bound": sum([runs[i] * (alpha / (1 - alpha)) ** deficits[i] for i in range(len(runs))]) + (len(attacker_blocks_above_longest_chain) + max(len(attacker_blocks_above_longest_chain) - 1, 0) * (alpha / (1 - 2 * alpha))) * (1 - alpha)
        }