from typing import List

from block import Block
from tree import Tree

class State:

    def __init__(self) -> None:
        """
        Maintains the state of the mining game.
        """

        self.tree: Tree = Tree()
        self.unpublished_blocks: List[Block] = []
        self.rounds_mined_on: List[int] = []