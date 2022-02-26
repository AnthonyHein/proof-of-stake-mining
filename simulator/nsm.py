from typing import List, Tuple, Union

from action import Action
from block import Block
from miner import Miner
from state import State
from strategy import Strategy

class NSM(Strategy):

    def __init__(self) -> None:
        """
        Instantiate the NOTHING-AT-STAKE SELFISH MINING strategy.
        """
        self.miner: Miner = Miner.ATTACKER

    def get_action(
        self, state: State
    ) -> Union[Tuple[Action, None],
               Tuple[Action, Tuple[Miner, List[Block], int, Block]]]:
        """"
        See the NSM strategy description at https://arxiv.org/pdf/2107.04069.pdf.
        """
        if not isinstance(state, State):
            raise TypeError("NSM.get_action: `state` must be of type `State`")

        unpublished_blocks = state.unpublished_blocks[self.miner]

        if len(unpublished_blocks) != 1 and len(unpublished_blocks) == state.tree.longest_chain.height + 1:
            return (
                Action.PUBLISH, (self.miner,
                                 unpublished_blocks,
                                 len(unpublished_blocks),
                                 state.tree.longest_chain.ancestors()[len(unpublished_blocks) - 1])
            )
        else:
            return (Action.WAIT, None)

    
    def get_capitulation(self, state: State) -> Tuple[Block, bool]:
        """
        See the NSM strategy description at https://arxiv.org/pdf/2107.04069.pdf
        """
        if not isinstance(state, State):
            raise TypeError("NSM.get_capitulation: `state` must be of type `State`")

        unpublished_blocks = state.unpublished_blocks[self.miner]

        if len(unpublished_blocks) == 0:
            return state.tree.longest_chain, True
        elif len(unpublished_blocks) <= 1 and state.tree.longest_chain.height > 2:
            return state.tree.longest_chain, True
        elif len(unpublished_blocks) <= 2 and state.tree.longest_chain.height > 2:
            return state.tree.longest_chain.ancestors()[1], False
        else:
            return None, False

    def __repr__(self) -> str:
        """
        Return the name of this strategy.
        """

        return "<SELFISH MINING STRATEGY>"