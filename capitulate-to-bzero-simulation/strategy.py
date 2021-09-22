from typing import List, Tuple

from block import Block
from miner import Miner

class Strategy:

    def __init__(self) -> None:
        
        self.miner = 

    def report_miner_idx(self, miner_idx: int) -> None:
        self.miner_idx: int = miner_idx

    def report_mined_block(self, current_miner_idx: int, block: Block) -> None:
        pass

    def report_published_set(self, blocks: List[Block], depth: int) -> None:
        pass

    def get_published_set(self) -> Tuple[List[Block], int]:
        pass
