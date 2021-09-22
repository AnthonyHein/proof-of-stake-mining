from typing import List

from block import Block
from block_utils import *
from miner import Miner
from tree import Tree

class State:

    def __init__(self) -> None:
        """
        Maintains the state of the mining game.
        """

        self.tree: Tree = Tree()
        self.unpublished_blocks: dict[Miner, List[Block]] = {
            Miner.ATTACKER: [],
            Miner.HONEST: [],
        }
        self.rounds_mined_on: dict[Miner, List[int]] = {
            Miner.ATTACKER: [],
            Miner.HONEST: [],
        }

    def capitulate(self, genesis: Block) -> 'State':
        """
        Modify the state so that the block `genesis` is effectively the genesis
        block from all strategies point of view.
        """

        if not isinstance(genesis, Block):
            raise TypeError("State.capitulate: `genesis` must be of type `Block`")
        if genesis not in self.tree.blocks:
            raise ValueError("State.capiulate: `genesis` must be an existing block in the tree")

        genesis_prev_height = genesis.height
        genesis_prev_created_at = genesis.created_at

        self.tree = self.tree.capitulate(genesis)

        self.unpublished_blocks = {
            Miner.ATTACKER: [
                relabel_block(block, genesis_prev_height, genesis_prev_created_at, False)
                for block
                in self.unpublished_blocks[Miner.ATTACKER]
                if block.created_at > genesis_prev_created_at
            ],
            Miner.HONEST: [
                relabel_block(block, genesis_prev_height, genesis_prev_created_at, False)
                for block
                in self.unpublished_blocks[Miner.HONEST]
                if block.created_at > genesis_prev_created_at
            ],
        }
        
        self.rounds_mined_on = {
            Miner.ATTACKER: [
                created_at - genesis_prev_created_at
                for created_at
                in self.rounds_mined_on[Miner.ATTACKER]
                if created_at >= genesis_prev_created_at
            ],
            Miner.HONEST: [
                created_at - genesis_prev_created_at
                for created_at
                in self.rounds_mined_on[Miner.HONEST]
                if created_at >= genesis_prev_created_at
            ],
        }

if __name__ == "__main__":

    state = State()

    # TODO