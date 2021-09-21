# -------------------------------------------------------------------------------
# A class for modeling a selfish miner in the proof-of-stake mining game with
# external randomness proposed by Ferreira and Weinberg.
#
# @author Anthony Hein
# @version 1.0
# -------------------------------------------------------------------------------

from typing import List, Tuple
from enum import Enum

from miner import Miner
from block import Block


class NSM_R1(Miner):

    class State(Enum):
        B0_0 = 1
        B1_0 = 2
        B2_0 = 3
        B1_1 = 4

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.will_publish = False
        self.blocks_hidden = []
        self.blocks_ahead = 0

        self.orphan = None
        self.orphan_depth = 0

        self.current_state = self.State.B0_0
        self.next_state = None

    def report_miner_idx(self, miner_idx: int) -> None:
        return super().report_miner_idx(miner_idx)

    def report_mined_block(self, current_miner_idx: int, block: Block) -> None:

        if self.miner_idx == current_miner_idx:

            self.blocks_ahead += 1
            self.blocks_hidden.append(block)

            if self.current_state == self.State.B0_0:
                self.next_state = self.State.B1_0

            elif self.current_state == self.State.B1_0 or self.current_state == self.State.B2_0:
                if self.orphan and self.blocks_ahead >= self.orphan_depth:
                    self.next_state = self.State.B0_0
                    self.will_publish = True
                    self.blocks_hidden = [self.orphan] + self.blocks_hidden
                else:
                    self.next_state = self.State.B2_0

            elif self.current_state == self.State.B1_1:
                self.next_state = self.State.B0_0
                self.will_publish = True

            else:
                assert False, "Unkown state."

        else:
            self.blocks_ahead = max(self.blocks_ahead - 1, 0)
            self.orphan_depth += 1

            if self.current_state == self.State.B0_0:
                self.next_state = self.State.B0_0

            elif self.current_state == self.State.B1_0:
                self.next_state = self.State.B1_1

            elif self.current_state == self.State.B2_0:
                if self.blocks_ahead == 1:
                    self.next_state = self.State.B0_0
                    self.will_publish = True

                else:
                    self.next_state = self.State.B2_0

            elif self.current_state == self.State.B1_1:
                self.next_state = self.State.B0_0

                self.orphan = self.blocks_hidden[0]
                self.orphan_depth = 2

                self.blocks_hidden = []

            else:
                assert False, "Unkown state."

        self.current_state = self.next_state

    def report_published_set(self, blocks: List[Block], depth: int) -> None:
        pass

    def get_published_set(self) -> Tuple[List[Block], int]:
        if self.will_publish:
            blocks = self.blocks_hidden
            self.reset()
            return (blocks, len(blocks) - 1)

        else:
            return ([], 0)
