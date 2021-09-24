# -------------------------------------------------------------------------------
# A class for modeling the proof-of-stake selfish mining game with external
# randomness proposed by Ferreira and Weinberg.
#
# @author Anthony Hein
# @version 1.0
# -------------------------------------------------------------------------------

from typing import List, Sequence
from random import random

from tqdm import tqdm

from block import Block
from miner import Miner

from honest_miner import HonestMiner
from nsm import NSM
from nsm_r1 import NSM_R1
from sm import SM

from sys import exit


ATTACKER = 0
HONEST = 1


class MiningGame:
    def __init__(
        self,
        miners: List[Miner],
        alpha: float,
        max_steps: int,
        verbose: bool,
        sequence: List[int] = None,
    ) -> None:

        self.miners: List[Miner] = miners

        for idx, miner in enumerate(self.miners):
            miner.report_miner_idx(idx)

        self.alpha: float = alpha

        self.max_steps: int = max_steps
        self.current_step = 1

        self.verbose = verbose

        self.sequence = sequence

        self.genesis: Block = Block(None, 0).publish(None)
        self.longest_chain: Block = self.genesis

    def step(self) -> None:

        if self.sequence:
            current_miner_idx = self.sequence[self.current_step - 1]
        else:
            current_miner_idx = ATTACKER if random() <= self.alpha else HONEST

        block = Block(current_miner_idx, self.current_step)

        if self.verbose:
            print(
                f"\nMiner {current_miner_idx} created block {self.current_step}.\n")

        for miner in self.miners:
            miner.report_mined_block(current_miner_idx, block)

        for idx in [HONEST, ATTACKER]:
            blocks, depth = self.miners[idx].get_published_set()

            if self.verbose:
                print(
                    f"Miner {idx} publishing blocks {[block.get_created_at() for block in blocks]} at depth {depth}."
                )

            parent = self.longest_chain.kth_ancestor(depth)

            for block in blocks:
                block.publish(parent)
                parent = block

            if (
                len(blocks) > 0
                and blocks[len(blocks) - 1].get_height()
                > self.longest_chain.get_height()
            ):
                self.longest_chain = blocks[len(blocks) - 1]

            self.miners[1 - idx].report_published_set(blocks, depth)

    def simulate(self) -> float:

        for _ in tqdm(range(self.max_steps)):
            self.step()
            self.current_step += 1

        longest_path = self.longest_chain.ancestors()

        if self.verbose:
            s = " -> ".join(
                [str(block.get_created_at()) for block in longest_path]
            ).rstrip(" -> ")
            print(f"\nLongest path:\n{s}\n")

        return sum(
            [1 if block.get_miner_idx() == ATTACKER else 0 for block in longest_path]
        ) / (len(longest_path) - 1)


if __name__ == "__main__":

    miners = [NSM(), HonestMiner()]
    alpha = 0.3262225  # 0.5 * (0.327727 + 0.324718)
    max_steps = 100000
    verbose = False
    sequence = None

    # sequence = [
    #     ATTACKER,
    #     HONEST,
    #     HONEST,
    #     HONEST,
    #     HONEST,
    #     HONEST,
    #     ATTACKER,
    #     ATTACKER,
    #     ATTACKER,
    #     ATTACKER,
    #     ATTACKER,
    # ]

    lst = []
    for i in range(100):
        try:
            score = MiningGame(
                [NSM(), HonestMiner()], alpha, len(
                    sequence) if sequence else max_steps, verbose, sequence
            ).simulate()
            lst.append(score)
        except AssertionError as e:
            print(e)
            exit(1)

    print(lst)
