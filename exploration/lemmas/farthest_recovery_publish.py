from typing import Callable, List, Tuple, Union

from conjectures.conjecture import Conjecture
from lemmas.lemma import Lemma
from state import State


DESCRIPTION = \
"""
Provides a lower bound to any state by considering the action which publishes such
that it recovers the farthest block possible and selfish mines on any excess.
"""

class FarthestRecoveryPublish(Lemma):

    @staticmethod
    def get_name():
        """
        Return the name of the lemma.
        """
        return "Farthest Recovery Publish"

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
        height_of_longest_chain = state.get_height_of_longest_chain()
        heights_attacker_blocks_can_reach = state.get_heights_attacker_blocks_can_reach()

        attacker_blocks_below_longest_chain = list(filter(lambda x: x <= height_of_longest_chain, heights_attacker_blocks_can_reach))
        attacker_blocks_above_longest_chain = list(filter(lambda x: x > height_of_longest_chain, heights_attacker_blocks_can_reach))

        if len(attacker_blocks_above_longest_chain) == 0:
            return ("0", lambda x: 0)

        deficits = []
        runs = []

        curr_deficit = 1
        curr_run = 0

        for i in range(height_of_longest_chain, 0, -1):
            if i in attacker_blocks_below_longest_chain:
                curr_run += 1
                continue

            else:
                if curr_run > 0:
                    deficits.append(curr_deficit)
                    runs.append(curr_run)
                curr_run = 0
                curr_deficit += 1

        if curr_run > 0:
            deficits.append(max(curr_deficit - len(attacker_blocks_above_longest_chain), 0))
            runs.append(curr_run)

        recovered_blocks = sum([runs[i] if deficits[i] <= len(attacker_blocks_above_longest_chain) else 0 for i in range(len(deficits))])
        recovered_deficit = max([deficit - 1 if deficit <= len(attacker_blocks_above_longest_chain) else 0 for deficit in deficits])
        excess_blocks = len(attacker_blocks_above_longest_chain) - recovered_deficit

        def fn(alpha) -> float:
            return recovered_blocks + recovered_deficit + (excess_blocks + max(excess_blocks - 1, 0) * (alpha / (1 - 2 * alpha))) * (1 - alpha)

        lb_str = ""

        if excess_blocks > 2:
            lb_str = (str(recovered_blocks + recovered_deficit) + " + " if recovered_blocks > 0 else "") + "\\big(" + str(excess_blocks) + " + " + str(excess_blocks - 1) + "(\\tfrac{\\alpha}{1 - 2\\alpha})\\big)(1 - \\lambda)"
        elif excess_blocks == 2:
            lb_str = (str(recovered_blocks + recovered_deficit) + " + " if recovered_blocks > 0 else "") + "\\big(" + str(excess_blocks) + "+ (\\tfrac{\\alpha}{1 - 2\\alpha})\\big)(1 - \\lambda)"
        elif excess_blocks == 1:
            lb_str = (str(recovered_blocks + recovered_deficit) + " + " if recovered_blocks > 0 else "") + "1 - \\alpha"

        return (lb_str, fn)

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
        return None