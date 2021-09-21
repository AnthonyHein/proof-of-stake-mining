# -------------------------------------------------------------------------------
# A class for modeling a miner in the proof-of-stake mining game with
# external randomness proposed by Ferreira and Weinberg.
#
# @author Anthony Hein
# @version 1.0
# -------------------------------------------------------------------------------

from typing import List, Tuple

from block import Block


class Miner:
    def report_miner_idx(self, miner_idx: int) -> None:
        self.miner_idx: int = miner_idx

    def report_mined_block(self, current_miner_idx: int, block: Block) -> None:
        pass

    def report_published_set(self, blocks: List[Block], depth: int) -> None:
        pass

    def get_published_set(self) -> Tuple[List[Block], int]:
        pass
