from typing import List, Tuple, Union

from action import Action
from block import Block
from miner import Miner
from state import State
from strategy import Strategy

class Frontier(Strategy):

    def __init__(self) -> None:
        """
        Instantiate the FRONTIER mining strategy.
        """
        self.miner: Miner = Miner.HONEST

    def get_action(
        self, state: State
    ) -> Union[Tuple[Action, None],
               Tuple[Action, Tuple[Miner, List[Block], int, Block]]]:
        """"
        Publish all unpublished blocks on top of the longest chain, or wait if
        no such blocks exist.
        """
        if not isinstance(state, State):
            raise TypeError("Frontier.get_action: `state` must be of type `State`")

        unpublished_blocks = state.unpublished_blocks[self.miner]

        if len(unpublished_blocks) > 0:
            return (
                Action.PUBLISH, (self.miner,
                                 unpublished_blocks,
                                 len(unpublished_blocks),
                                 state.tree.longest_chain)
            )
        else:
            return (Action.WAIT, None)

    def get_capitulation(self, state: State) -> Tuple[Block, bool]:
        """
        Always capitulate to the current longest chain.
        """
        if not isinstance(state, State):
            raise TypeError("Frontier.get_capitulation: `state` must be of type `State`")

        return state.tree.longest_chain, True

    def __repr__(self) -> str:
        """
        Return the name of this strategy.
        """

        return "<FRONTIER STRATEGY>"