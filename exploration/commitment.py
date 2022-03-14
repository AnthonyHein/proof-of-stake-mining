import sympy as sp
import sys
from typing import Callable, List, TypedDict, Union

# At the moment, the only commitments we consider are selfish mining commitments
# with at least one boundary at zero and an initial position equal to the number
# of blocks in excess of that necessary to publish in the implicit random walk.
# For example, in the familiar start (2A), there is _one_ block in excess of that
# necessary to publish in the implicit random walk. A commitment may have another
# boundary, in which case the interpretation is that the miner publishes at the
# first boundary which is hit. The assumption that these are only selfish mining
# commitments simplifies the involved data structures and calculations. Whenever
# we consider a commitment we will always assume the miner capitulates afterwards.

class OneBoundaryCommitment(TypedDict):
    committed_blocks: List[int]
    selfish_mining_blocks: List[int]
    initial_position: int
    boundary: int
    reward_at_boundary: sp.core.Expr

class TwoBoundaryCommitment(TypedDict):
    committed_blocks: List[int]
    selfish_mining_blocks: List[int]
    recovered_blocks: List[int]
    initial_position: int
    lower_boundary: int
    upper_boundary: int
    pr_lower_boundary: sp.core.Expr
    pr_upper_boundary: sp.core.Expr
    reward_at_lower_boundary: sp.core.Expr
    reward_at_upper_boundary: sp.core.Expr

def commitment_str(commitment: Union[OneBoundaryCommitment, TwoBoundaryCommitment]) -> str:
    """
    Return a string representation of a commitment.
    """
    s = ""

    s += f"committed {commitment['committed_blocks']} and will selfish mine on {commitment['selfish_mining_blocks']}"

    if commitment_isinstance(commitment, TwoBoundaryCommitment):
        s += f" unless recovers {commitment['recovered_blocks']}"

    return s

def commitment_isinstance(x: object, cls: Callable[[], None]) -> bool:
    """
    Check if object `x` is an instance of class `cls`. Where `cls` is one of
    `OneBoundaryCommitment` or `TwoBoundaryCommitment`.
    """
    keys = set()

    if cls == OneBoundaryCommitment:
        keys = set([
            "committed_blocks",
            "selfish_mining_blocks",
            "initial_position",
            "boundary",
            "reward_at_boundary",
        ])

    elif cls == TwoBoundaryCommitment:
        keys = set([
            "committed_blocks",
            "selfish_mining_blocks",
            "recovered_blocks",
            "initial_position",
            "lower_boundary",
            "upper_boundary",
            "pr_lower_boundary",
            "pr_upper_boundary",
            "reward_at_lower_boundary",
            "reward_at_upper_boundary",
        ])

    else:
        print(f"commitment.commitment_isinstance: object {x} and class {cls} can not be checked by this method")
        sys.exit(1)

    return isinstance(x, dict) and set(x.keys()) == keys
