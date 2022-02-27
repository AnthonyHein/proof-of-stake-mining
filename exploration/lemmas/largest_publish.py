from typing import Callable, List, Tuple, Union

from conjectures.conjecture import Conjecture
from lemmas.lemma import Lemma
from state import State


DESCRIPTION = \
"""
Provides a lower bound to any state by considering the action which publishes or selfish
mines on the largest number of blocks the attacker currently owns then capitulates. This
lower bound will never jump a "deficit" using blocks in excess of the longest chain.
"""

class LargestPublish(Lemma):

    @staticmethod
    def get_name():
        """
        Return the name of the lemma.
        """
        return "Largest Publish"

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

        curr_run = 0

        for i in range(height_of_longest_chain, 0, -1):
            if i in attacker_blocks_below_longest_chain:
                curr_run += 1
                continue
            else:
                break

        def fn(alpha) -> float:
            return curr_run + (len(attacker_blocks_above_longest_chain) + max(len(attacker_blocks_above_longest_chain) - 1, 0) * (alpha / (1 - 2 * alpha))) * (1 - alpha)

        lb_str = ""

        if len(attacker_blocks_above_longest_chain) > 2:
            lb_str = (str(curr_run) + " + " if curr_run > 0 else "") + "\\big(" + str(len(attacker_blocks_above_longest_chain)) + " + " + str((len(attacker_blocks_above_longest_chain) - 1)) + "(\\tfrac{\\alpha}{1 - 2\\alpha})\\big)(1 - \\lambda)"
        elif len(attacker_blocks_above_longest_chain) == 2:
            lb_str = (str(curr_run) + " + " if curr_run > 0 else "") + "\\big(" + str(len(attacker_blocks_above_longest_chain)) + "+ (\\tfrac{\\alpha}{1 - 2\\alpha})\\big)(1 - \\lambda)"
        elif len(attacker_blocks_above_longest_chain) == 1:
            lb_str = (str(curr_run) + " + " if curr_run > 0 else "") + "1 - \\alpha"

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