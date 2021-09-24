from functools import partial
from typing import Callable

import sympy as sp

from miner import Miner
from state import State

# FIXME: sympy is way to slow for our purposes... need to ditch this

def miner_k_reward(miner: Miner, start: State, end: State) -> int:
    """
    Given a `start` state and an `end` state, calculate the integer-valued reward of
    miner `miner` as the difference between the number of blocks created by miner
    `miner` in the longest path at state `end` and state `start`.
    """

    if not isinstance(miner, Miner):
        raise TypeError("state_utils.miner_k_reward: `miner` must be of type `Miner`")
    if not isinstance(start, State):
        raise TypeError("state_utils.miner_k_reward: `start` must be of type `State`")
    if not isinstance(start, State):
        raise TypeError("state_utils.miner_k_reward: `end` must be of type `State`")
    
    longest_chain_blocks_start = 0

    for block in start.tree.longest_chain.ancestors():
        if block.miner == miner:
            longest_chain_blocks_start += 1

    longest_chain_blocks_end = 0

    for block in end.tree.longest_chain.ancestors():
        if block.miner == miner:
            longest_chain_blocks_start += 1

    return longest_chain_blocks_end - longest_chain_blocks_start

def mining_game_reward_fixed_rev(start: State, end: State, rev: float) -> float:
    """
    Given a `start` state and an `end` state, calculate the real-valued mining
    game reward as the weighted sum of miner `Miner.ATTACKER` reward and miner
    `Miner.HONEST` reward with weights (1 - `rev`) and (-`rev`) respectively.
    """

    if not isinstance(start, State):
        raise TypeError("state_utils.mining_game_reward: `start` must be of type `State`")
    if not isinstance(start, State):
        raise TypeError("state_utils.mining_game_reward: `end` must be of type `State`")
    if not isinstance(rev, float):
        raise TypeError("state_utils.mining_game_reward: `rev` must be of type `float`")

    return (1 - rev) * miner_k_reward(Miner.ATTACKER, start, end) - \
           rev * miner_k_reward(Miner.HONEST, start, end)


def mining_game_reward_expr(start: State, end: State) -> sp.core.add.Add:
    """
    Given a `start` state and an `end` state, calculate the real-valued mining
    game reward as the weighted sum of miner `Miner.ATTACKER` reward and miner
    `Miner.HONEST` reward with weights (1 - rev) and (-rev) respectively where
    `rev` is a symbolic symbol in SymPy. This allows for evaluating `rev` when
    the run finally capitulates.
    """

    if not isinstance(start, State):
        raise TypeError("state_utils.mining_game_reward_expr: `start` must be of type `State`")
    if not isinstance(start, State):
        raise TypeError("state_utils.mining_game_reward_expr: `end` must be of type `State`")

    rev = sp.symbols('rev')
    return (1 - rev) * miner_k_reward(Miner.ATTACKER, start, end) - \
           rev * miner_k_reward(Miner.HONEST, start, end)

def mining_game_reward_val(start: State, end: State) -> float:
    """
    Given a `start` state and an `end` state, calculate the real-valued mining
    game reward as value of `rev` that makes the following equation true:
        (1 - rev)(Miner.ATTACKER reward) + (- rev)(Miner.HONEST reward) = 0
    """

    
    if not isinstance(start, State):
        raise TypeError("state_utils.mining_game_reward_val: `start` must be of type `State`")
    if not isinstance(start, State):
        raise TypeError("state_utils.mining_game_reward_val: `end` must be of type `State`")

    rev = sp.symbols('rev')
    sol = sp.solve(mining_game_reward_expr(start, end), rev)

    if sol != None and len(sol) > 0:
        return sol[0].evalf()
    else:
        return 0