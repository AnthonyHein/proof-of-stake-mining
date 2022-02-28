from typing import Callable, List, Tuple, Union

from conjectures.conjecture import Conjecture
from lemmas.lemma import Lemma
from state import State


DESCRIPTION = \
"""
The value of a state is zero if there are so many consecutive honest miner blocks that the
attacker would prefer to selfish mine over their lead rather than recover attacker blocks
even if presented the chance to do so.
"""

class NonCheckpointFinality(Lemma):

    @staticmethod
    def get_name():
        """
        Return the name of the lemma.
        """
        return "Non Checkpoint Finality"

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

        height_of_longest_chain = state.get_height_of_longest_chain()
        heights_attacker_blocks_can_reach = state.get_heights_attacker_blocks_can_reach()

        attacker_blocks_below_longest_chain = list(filter(lambda x: x <= height_of_longest_chain, heights_attacker_blocks_can_reach))
        attacker_blocks_above_longest_chain = list(filter(lambda x: x > height_of_longest_chain, heights_attacker_blocks_can_reach))

        if len(attacker_blocks_above_longest_chain) > 0:
            return None

        x = height_of_longest_chain - (attacker_blocks_below_longest_chain[-1] - 1)
        
        if x < len(attacker_blocks_below_longest_chain) - 2:
            return None

        non_consecutive_blocks = list(filter(lambda b: b - 1 not in attacker_blocks_below_longest_chain, attacker_blocks_below_longest_chain))

        for non_consecutive_block in non_consecutive_blocks:
            
            size_if_publish = sum([b >= non_consecutive_block for b in attacker_blocks_below_longest_chain])
            lead_if_not_publish = height_of_longest_chain - size_if_publish - (non_consecutive_block - 1)

            if (- size_if_publish + lead_if_not_publish * (alpha_pos_lb / (1 - 2 * alpha_pos_lb))) * (1 - alpha_pos_lb) - height_of_longest_chain * alpha_pos_lb < 0:
                return None

        return "0", lambda alpha: 0

    

    
