import sympy as sp
from typing import Optional

from bound import LemmaLowerBound, LemmaUpperBound
from lemmas.lemma import Lemma
from settings.setting import Setting
from state import State
from state_utils import *

# The value of a state is zero if there are so many consecutive honest miner blocks that the
# attacker would prefer to selfish mine over their lead rather than recover attacker blocks
# even if presented the chance to do so.

class NonCheckpointFinality(Lemma):

    @staticmethod
    def get_name() -> str:
        """
        Return the name of the lemma.
        """
        return "Non Checkpoint Finality"

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
        if state.get_attacker_blocks() != state.get_unpublished_blocks():
            return None

        height_of_longest_chain = len(state.get_longest_path()) - 1
        heights_unpublished_blocks_can_reach = get_heights_unpublished_blocks_can_reach(state)

        if len(heights_unpublished_blocks_can_reach) == 0 or \
           max(heights_unpublished_blocks_can_reach) >= height_of_longest_chain:
            return None

        x = height_of_longest_chain - (heights_unpublished_blocks_can_reach[-1] - 1)
        
        if x < len(heights_unpublished_blocks_can_reach) - 2:
            return None

        non_consecutive_block_heights = list(filter(lambda h: h - 1 not in heights_unpublished_blocks_can_reach, heights_unpublished_blocks_can_reach))

        for non_consecutive_block_height in non_consecutive_block_heights:
            
            size_if_publish = sum([b >= non_consecutive_block_height for b in heights_unpublished_blocks_can_reach])
            lead_if_not_publish = height_of_longest_chain - size_if_publish - (non_consecutive_block_height - 1)

            if (- size_if_publish + lead_if_not_publish * (settings["alpha_pos_lower_bound"] / (1 - 2 * settings["alpha_pos_lower_bound"]))) * (1 - settings["alpha_pos_lower_bound"]) - height_of_longest_chain * settings["alpha_pos_lower_bound"] < 0:
                return None

        return {
            "lemma": NonCheckpointFinality.get_name(),
            "upper_bound": sp.Integer(0),
        }

    

    
