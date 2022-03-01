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

class LemmaG8(Lemma):

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
                    settings: dict[str, object],
                    conjectures: List[Conjecture]) -> Union[Tuple[str, Callable[[float], float]], None]:
        """
        Return the lower bound to the value of `state` that is achieved
        by this lemma as a string formula and function of alpha, or `None`
        if this lemma does not prove any such lower bound.
        """
        return None

    @staticmethod
    def upper_bound(state: State,
                    settings: dict[str, object],
                    conjectures: List[Conjecture]) -> Union[Tuple[str, Callable[[float], float]], None]:
        """
        Return the upper bound to the value of `state` that is achieved
        by this lemma as a string formula and function of alpha, or `None`
        if this lemma does not prove any such upper bound.
        """

        height_of_longest_chain = state.get_height_of_longest_chain()
        heights_attacker_blocks_can_reach = state.get_heights_attacker_blocks_can_reach()

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

        def upper_bounded_reward_below_longest_chain_fn(alpha) -> float:
            return sum([runs[i] * (alpha / (1 - alpha)) ** deficits[i] for i in range(len(runs))])

        upper_bounded_reward_below_longest_chain_str = ""

        if len(attacker_blocks_below_longest_chain) > 0:
            upper_bounded_reward_below_longest_chain_str = " + ".join([
                (str(runs[i]) if runs[i] > 1 or deficits[i] == 0 else "") + ("(\\tfrac{\\alpha}{1 - \\alpha})" if deficits[i] > 0 else "") + ("^{" + str(deficits[i]) + "}" if deficits[i] > 1 else "")
                for i
                in range(len(runs))
            ])

        def upper_bounded_reward_above_longest_chain_fn(alpha) -> float:
            return (len(attacker_blocks_above_longest_chain) + max(len(attacker_blocks_above_longest_chain) - 1, 0) * (alpha / (1 - 2 * alpha))) * (1 - alpha)

        upper_bounded_reward_above_longest_chain_str = ""

        if len(attacker_blocks_above_longest_chain) > 2:
            upper_bounded_reward_above_longest_chain_str = "\\big(" + str(len(attacker_blocks_above_longest_chain)) + " + " + str((len(attacker_blocks_above_longest_chain) - 1)) + "(\\tfrac{\\alpha}{1 - 2\\alpha})\\big)(1 - \\lambda)"
        elif len(attacker_blocks_above_longest_chain) == 2:
            upper_bounded_reward_above_longest_chain_str = "\\big(" + str(len(attacker_blocks_above_longest_chain)) + "+ (\\tfrac{\\alpha}{1 - 2\\alpha})\\big)(1 - \\lambda)"
        elif len(attacker_blocks_above_longest_chain) == 1:
            upper_bounded_reward_above_longest_chain_str = "1 - \\alpha"

        ub_str = ""

        if upper_bounded_reward_below_longest_chain_str == "" and upper_bounded_reward_above_longest_chain_str == "":
            ub_str = "0"
        elif upper_bounded_reward_above_longest_chain_str != "" and upper_bounded_reward_below_longest_chain_str != "":
            ub_str = upper_bounded_reward_below_longest_chain_str + " + " + upper_bounded_reward_above_longest_chain_str
        else:
            ub_str = upper_bounded_reward_below_longest_chain_str + upper_bounded_reward_above_longest_chain_str

        return (
            ub_str,
            lambda alpha: upper_bounded_reward_below_longest_chain_fn(alpha) + upper_bounded_reward_above_longest_chain_fn(alpha)
        )

    

    
