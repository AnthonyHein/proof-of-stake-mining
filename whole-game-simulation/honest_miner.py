# -------------------------------------------------------------------------------
# A class for modeling an honest miner in the proof-of-stake mining game with
# external randomness proposed by Ferreira and Weinberg.
#
# @author Anthony Hein
# @version 1.0
# -------------------------------------------------------------------------------

from typing import List, Tuple

from miner import Miner
from block import Block


class HonestMiner(Miner):

    def __init__(self) -> None:
        self.block_to_publish: Block = None

    def report_miner_idx(self, miner_idx: int) -> None:
        return super().report_miner_idx(miner_idx)

    def report_mined_block(self, current_miner_idx: int, block: Block) -> None:
        if self.miner_idx == current_miner_idx:
            self.block_to_publish = block

    def report_published_set(self, blocks: List[Block], depth: int) -> None:
        pass

    def get_published_set(self) -> Tuple[List[Block], int]:
        if self.block_to_publish:
            block = self.block_to_publish
            self.block_to_publish = None
            return ([block], 0)
        else:
            return ([], 0)
