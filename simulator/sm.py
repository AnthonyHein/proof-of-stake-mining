from typing import List, Tuple, Union

from action import Action
from block import Block
from miner import Miner
from state import State
from strategy import Strategy

class SM(Strategy):

    def __init__(self) -> None:
        """
        Instantiate the SELFISH MINING strategy.
        """
        self.miner: Miner = Miner.ATTACKER

    def get_action(
        self, state: State
    ) -> Union[Tuple[Action, None],
               Tuple[Action, Tuple[Miner, List[Block], int, Block]]]:
        """"
        Publish on top of the longest chain when you have hidden a block that
        can reach a height of exactly one greater than the public longest chain.
        In all other cases, wait.
        """
        if not isinstance(state, State):
            raise TypeError("SM.get_action: `state` must be of type `State`")

        unpublished_blocks = state.unpublished_blocks[self.miner]

        if len(unpublished_blocks) != 1 and len(unpublished_blocks) == len(state.tree.longest_chain.ancestors()):
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
        Capitulate the the longest chain if there are no unpublished blocks or
        the private chain is trailing by one or more blocks.
        """
        if not isinstance(state, State):
            raise TypeError("SM.get_capitulation: `state` must be of type `State`")

        unpublished_blocks = state.unpublished_blocks[self.miner]

        if len(unpublished_blocks) == 0:
            return state.tree.longest_chain, True
        elif len(unpublished_blocks) < len(state.tree.longest_chain.ancestors()) - 1:
            return state.tree.longest_chain, True
        else:
            return None, False

    def __repr__(self) -> str:
        """
        Return the name of this strategy.
        """

        return "<SELFISH MINING STRATEGY>"