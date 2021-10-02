from typing import List, Tuple, Union
from sys import stderr

from action import Action
from block import Block
from miner import Miner
from state import State
from strategy import Strategy

class REM1(Strategy):

    def __init__(self) -> None:
        """
        Instantiate the REMEMBER 1 SELFISH MINING strategy.
        """
        self.miner: Miner = Miner.ATTACKER
        self.just_published: bool = False

    def _get_failed_rounds(self, state: State) -> List[Block]:
        """
        TODO: Will have to writeup more formal description.
        """

        if not isinstance(state, State):
            raise TypeError("REM1._get_failures: `state` must be of type `State`")

        # this code assumes that `rounds_mined_on` will always be in increasing order
        rounds_mined_on = state.rounds_mined_on[self.miner]

        round_no = max(state.rounds_mined_on[Miner.ATTACKER] + state.rounds_mined_on[Miner.HONEST])

        failed_rounds = []
        selfish_mining_tail = False

        for i in range(1, len(rounds_mined_on)):
            if rounds_mined_on[i] - rounds_mined_on[i-1] == 1:
                selfish_mining_tail = True
                break
            if rounds_mined_on[i] - rounds_mined_on[i-1] > 2:
                failed_rounds.append(rounds_mined_on[i-1])

        if not selfish_mining_tail and len(rounds_mined_on) > 0 and round_no - rounds_mined_on[-1] >= 2:
            failed_rounds.append(rounds_mined_on[-1])

        return failed_rounds

    def get_action(
        self, state: State
    ) -> Union[Tuple[Action, None],
               Tuple[Action, Tuple[Miner, List[Block], int, Block]]]:
        """"
        TODO: Will have to writeup more formal description.
        """
        if not isinstance(state, State):
            raise TypeError("REM1.get_action: `state` must be of type `State`")

        # this code assumes that `rounds_mined_on` will always be in increasing order

        self.just_published = False

        unpublished_blocks = state.unpublished_blocks[self.miner]
        rounds_mined_on = state.rounds_mined_on[self.miner]
        
        failed_rounds = self._get_failed_rounds(state)

        if len(failed_rounds) > 0 and len(unpublished_blocks) > 1:
            # get all attacker blocks not including the most recent failed round
            non_failed_blocks = [
                block
                for block
                in unpublished_blocks
                if block.created_at not in failed_rounds
            ]

            # get the longest chain had we capitulated after most recent failure (including genesis)
            lc_after_recent_failure = [
                block
                for block
                in state.tree.longest_chain.ancestors()
                if block.created_at >= rounds_mined_on[1] - 1
            ]
        else:
            non_failed_blocks = []
            lc_after_recent_failure = []

        if len(unpublished_blocks) != 1 and len(unpublished_blocks) == state.tree.longest_chain.height + 1:
            self.just_published = True
            return (
                Action.PUBLISH, (self.miner,
                                 unpublished_blocks,
                                 len(unpublished_blocks),
                                 state.tree.longest_chain.ancestors()[len(unpublished_blocks) - 1])
            )

        elif len(failed_rounds) > 0 and len(non_failed_blocks) > 1 and len(non_failed_blocks) == len(lc_after_recent_failure):
            self.just_published = True
            return (
                Action.PUBLISH, (self.miner,
                                 non_failed_blocks,
                                 len(non_failed_blocks),
                                 lc_after_recent_failure[len(non_failed_blocks) - 1])
            )

        else:
            return (Action.WAIT, None)

    
    def get_capitulation(self, state: State) -> Tuple[Block, bool]:
        """
        TODO: Will have to writeup more formal description.
        """
        if not isinstance(state, State):
            raise TypeError("REM1.get_capitulation: `state` must be of type `State`")

        # this code assumes that `rounds_mined_on` will always be in increasing order

        unpublished_blocks = state.unpublished_blocks[self.miner]
        rounds_mined_on = state.rounds_mined_on[self.miner]

        failed_rounds = self._get_failed_rounds(state)

        # capitulate if we just published or have no unpublished blocks
        if self.just_published or len(unpublished_blocks) == 0:
            return state.tree.longest_chain, True
        
        # capitulate if we have two blocks that failed selfish mining
        elif len(failed_rounds) >= 2:

            # relabel rounds_mined_on[1] to be |1|
            return [
                block
                for block
                in state.tree.longest_chain.ancestors()
                if block.created_at == rounds_mined_on[1] - 1
            ][0], False

        else:
            return None, False

    def __repr__(self) -> str:
        """
        Return the name of this strategy.
        """

        return "<SELFISH MINING STRATEGY>"