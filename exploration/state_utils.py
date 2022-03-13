import sympy as sp
import sys
from typing import List, Tuple, Union

from commitment import *
from random_walk_utils import *
from state import State
from symbols import *

def get_checkpoints(state: State) -> List[int]:
    """
    Get a list of all checkpoints in state `state`.
    """
    attacker_blocks = state.get_attacker_blocks()

    checkpoints = [0]

    for block in state.get_longest_path()[1:]:
        if len(list(filter(lambda x: x in state.get_longest_path() and checkpoints[-1] < x and x <= block, attacker_blocks))) >= \
           len(list(filter(lambda x: x in state.get_unpublished_blocks() and checkpoints[-1] < x and x <= block, attacker_blocks))):
            checkpoints.append(block)
    
    return checkpoints

def get_heights_unpublished_blocks_can_reach(state: State) -> List[int]:
    """
    Get the heights that unpublished blocks owned by the attacker can reach.
    For any unpublished block owned by the attacker, this is the maximum of
    * the number blocks in the longest path less than this block
    * and, the height of the most previous attacker block plus one
    """
    heights = []

    prev_unpublished_block_height = 0

    for unpublished_block in state.get_unpublished_blocks():

        curr_unpublished_block_height = max(
            sum([block < unpublished_block for block in state.get_longest_path()]),
            prev_unpublished_block_height + 1,
        )

        prev_unpublished_block_height = curr_unpublished_block_height

        heights.append(curr_unpublished_block_height)

    return tuple(heights)

def occurs_after_state(start: State, end: State) -> bool:
    """
    Check whether `end` state occurs strictly after `start` state. This function
    only works correctly on states where the attacker has not yet published anything.
    This is because it is very difficult to know _when_ blocks in the longest path
    were added to the longest path and so it is difficult to know if a state occurs
    after another in the general case.
    """
    return len(start) != len(end) and start.get_sequence() == end.get_sequence()[:len(start)]


def get_reward_between_states(start: State, end: State) -> sp.core.add.Add:
    """
    Get the immediate reward between `start` state and `end` state, returned
    as a SymPy expression to allow for the symbol `lambda`.
    """
    if not isinstance(start, State):
        print(f"state_utils.get_reward_between_states: `start` must be of type `State`")
        sys.exit(1)
    if not isinstance(end, State):
        print(f"state_utils.get_reward_between_states: `end` must be of type `State`")
        sys.exit(1)

    attacker_blocks_start = start.get_attacker_blocks()
    attacker_blocks_end = end.get_attacker_blocks()

    honest_miner_blocks_start = start.get_honest_miner_blocks()
    honest_miner_blocks_end = end.get_honest_miner_blocks()

    delta_attacker_blocks_in_longest_path = len(list(filter(lambda x: x in attacker_blocks_end, end.get_longest_path()))) - \
                                            len(list(filter(lambda x: x in attacker_blocks_start, start.get_longest_path())))

    delta_honest_miner_blocks_in_longest_path = len(list(filter(lambda x: x in honest_miner_blocks_end, end.get_longest_path()))) - \
                                                len(list(filter(lambda x: x in honest_miner_blocks_start, start.get_longest_path())))

    return (1 - lamba) * delta_attacker_blocks_in_longest_path - lamba * delta_honest_miner_blocks_in_longest_path

def get_available_actions(state: State) -> List[Tuple[int, int]]:
    """
    Get all structured actions (i.e. timeserving, orderly, ...) available at state `state`.
    An action is just a tuple with two ints representing `k` and `v` as used in the
    definition of action Publish(k,v). Importantly, assume that `state` has no checkpoints
    except for the genesis block (otherwise we can capitulate state to get a simpler state).
    """

    if len(get_checkpoints(state)) > 1:
        print(f"state_utils.get_available_actions: `state` {state} must not have any checkpoints aside from the genesis block, capitulate state first")
        sys.exit(1)
    
    available_actions: List[Tuple[int, int]] = _get_timeserving_orderly_lcm_trimmed_actions(state)

    available_actions_do_not_establish_checkpoint, available_actions_establish_checkpoint = _split_actions_by_checkpoint_establishment(state, available_actions)

    available_actions_establish_checkpoint = _get_checkpoint_recurrent_actions(state, available_actions_establish_checkpoint)
    available_actions_establish_checkpoint = _get_nonsingleton_actions(state, available_actions_establish_checkpoint)
    available_actions_establish_checkpoint = _get_thrifty_actions(state, available_actions_establish_checkpoint)
    available_actions_establish_checkpoint = _get_patient_actions(state, available_actions_establish_checkpoint)
    available_actions_establish_checkpoint = _get_elevated_actions(state, available_actions_establish_checkpoint)

    return available_actions_do_not_establish_checkpoint + available_actions_establish_checkpoint

def _get_timeserving_orderly_lcm_trimmed_actions(state: State) -> List[Tuple[int, int]]:
    """
    Get all actions which are timserving, orderly, LCM, and trimmed. Note that the action
    Wait is just Publish(0,C), where C is the current longest chain and is always an
    available action.
    """

    attacker_blocks = state.get_attacker_blocks()
    longest_path = state.get_longest_path()
    unpublised_blocks = state.get_unpublished_blocks()

    available_actions = [(0,longest_path[-1])]   

    for height in reversed(range(len(longest_path))):

        blocks = list(filter(lambda x: x > longest_path[height], unpublised_blocks))

        if len(blocks) < len(longest_path) - height:
            continue
        
        if height + 1 < len(longest_path) and longest_path[height + 1] in attacker_blocks:
            continue

        for k in range(len(longest_path) - height, len(blocks) + 1):
            available_actions += [(k, longest_path[height])]

    return available_actions

def _split_actions_by_checkpoint_establishment(state: State,
                                               available_actions: List[Tuple[int, int]]) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Split actions in `available_actions` into one group of actions that do not establish
    a checkpoint at state `state` and another group of actions which do establish a
    checkpoint (and thus the blocks published in the action reach finality) at state 
    `state`.
    """
    available_actions_do_not_establish_checkpoint = []
    available_actions_establish_checkpoint = []

    for action in available_actions:
        subsequent_state = state.next_state_from_action(*action)
        if len(get_checkpoints(subsequent_state)) > 1:
            available_actions_establish_checkpoint.append(action)
        else:
            available_actions_do_not_establish_checkpoint.append(action)

    return available_actions_do_not_establish_checkpoint, available_actions_establish_checkpoint

def _get_checkpoint_recurrent_actions(state: State,
                                      available_actions_establish_checkpoint: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Get all actions from `available_actions_establish_checkpoint` which are checkpoint
    recurrent at the state `state`.
    """  
    available_actions_establish_checkpoint_and_checkpoint_recurrent = []

    for action in available_actions_establish_checkpoint:
        
        k, v = action

        if k == len(list(filter(lambda x: x > v, state.get_unpublished_blocks()))):
            available_actions_establish_checkpoint_and_checkpoint_recurrent.append(action)

    return available_actions_establish_checkpoint_and_checkpoint_recurrent

def _get_nonsingleton_actions(state: State,
                              available_actions_establish_checkpoint: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Get all actions from `available_actions_establish_checkpoint` which are nonsingleton
    at the state `state`.
    """    
    available_actions_establish_checkpoint_and_nonsingleton = []

    for action in available_actions_establish_checkpoint:
        
        k, v = action

        if k > 1:
            available_actions_establish_checkpoint_and_nonsingleton.append(action)

    return available_actions_establish_checkpoint_and_nonsingleton

def _get_thrifty_actions(state: State,
                         available_actions_establish_checkpoint: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Get all actions from `available_actions_establish_checkpoint` which are thrifty
    at the state `state`. This function is actually impletemented such that it
    assumes all actions in `available_actions_establish_checkpoint` have already
    been checked to ensure they are checkpoint recurrent.
    """
    if len(available_actions_establish_checkpoint) == 0:
        return []
    else:
        return [sorted(available_actions_establish_checkpoint, key=lambda x: x[0], reverse=True)[0]]
    

def _get_patient_actions(state: State,
                         available_actions_establish_checkpoint: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Get all actions from `available_actions_establish_checkpoint` which are patient
    at the state `state`.
    """
    available_actions_establish_checkpoint_and_patient = []

    for action in available_actions_establish_checkpoint:
        subsequent_state = state.next_state_from_action(*action)
        if len(subsequent_state.get_longest_path()) - len(state.get_longest_path()) == 1:
            available_actions_establish_checkpoint_and_patient.append(action)

    return available_actions_establish_checkpoint_and_patient

def _get_elevated_actions(state: State,
                          available_actions_establish_checkpoint: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Get all actions from `available_actions_establish_checkpoint` which are elevated
    at the state `state`. This function is actually impletemented such that it
    assumes all actions in `available_actions_establish_checkpoint` have already
    been checked to they are timeserving, orderly, LCM, trimmed and checkpoint recurrent.
    Furthermore, it assumes that the blocks in `state.get_unpublished_blocks()` are
    sorted in increasing order of timestamps.
    """
    available_actions_establish_checkpoint_and_elevated = []

    for action in available_actions_establish_checkpoint:
        
        k, v = action

        if state.get_unpublished_blocks()[-k] == v + 1:
            available_actions_establish_checkpoint_and_elevated.append(action)

    return available_actions_establish_checkpoint_and_elevated

def get_subsequent_states(state: State) -> List[State]:
    """
    Get all states which may follow a state, where these states are those reached
    by valid actions as defined above.
    """
    return [state.next_state_from_action(*action) for action in get_available_actions(state)]

def get_deficits_and_runs(state: State) -> Tuple[List[int], List[int]]:
    """
    Get the list of deficits and runs for state `state`. This comment should be
    updated when there is a better way of explaining what deficits and runs are,
    but for the moment they are just as defined by this code. Returned as the
    tuple (deficits, runs).
    """
    height_of_longest_chain = len(state.get_longest_path()) - 1
    heights_unpublished_blocks_can_reach = get_heights_unpublished_blocks_can_reach(state)

    heights_unpublished_blocks_below_longest_chain = list(filter(lambda x: x <= height_of_longest_chain, heights_unpublished_blocks_can_reach))
    heights_unpublished_blocks_above_longest_chain = list(filter(lambda x: x > height_of_longest_chain, heights_unpublished_blocks_can_reach))

    deficits = []
    runs = []

    curr_deficit = 1
    curr_run = 0

    for i in range(height_of_longest_chain, 0, -1):
        if i in heights_unpublished_blocks_below_longest_chain:
            curr_run += 1

        else:
            if curr_run > 0:
                deficits.append(curr_deficit)
                runs.append(curr_run)
            curr_run = 0
            curr_deficit += 1

    if curr_run > 0:
        deficits.append(curr_deficit)
        runs.append(curr_run)

    return (deficits, runs)

def get_available_commitments(state: State) -> List[Union[OneBoundaryCommitment, TwoBoundaryCommitment]]:
    """
    Get all commitments available at state `state`. The class of commitments we
    consider is outlined in `commitment.py`.
    """
    commitments: List[Union[OneBoundaryCommitment, TwoBoundaryCommitment]] = []

    height_of_longest_chain: int = len(state.get_longest_path()) - 1
    unpublished_blocks: List[int] = list(state.get_unpublished_blocks())
    heights_unpublished_blocks_can_reach: List[int] = get_heights_unpublished_blocks_can_reach(state)

    heights_unpublished_blocks_below_longest_chain: List[int] = list(filter(lambda x: x <= height_of_longest_chain, heights_unpublished_blocks_can_reach))
    heights_unpublished_blocks_above_longest_chain: List[int] = list(filter(lambda x: x > height_of_longest_chain, heights_unpublished_blocks_can_reach))

    if len(heights_unpublished_blocks_above_longest_chain) < 2:
        return commitments

    unpublished_blocks_below_longest_chain: List[int] = list(unpublished_blocks)[:-len(heights_unpublished_blocks_above_longest_chain)]
    unpublished_blocks_above_longest_chain: List[int] = list(unpublished_blocks)[-len(heights_unpublished_blocks_above_longest_chain):]

    committed_blocks: List[int] = list(unpublished_blocks_above_longest_chain)
    selfish_mining_blocks: List[int] = list(unpublished_blocks_above_longest_chain)
    initial_position: int = len(unpublished_blocks_above_longest_chain) - 1

    # Calculate all deficits.
    deficits, runs = get_deficits_and_runs(state)

    remaining_unpublished_blocks_below_longest_chain  = unpublished_blocks_below_longest_chain
    remaining_heights_unpublished_blocks_below_longest_chain = heights_unpublished_blocks_below_longest_chain

    # See if there are some blocks which are promised to be published in any commitment scheme.
    if len(deficits) > 0 and deficits[0] == 1:
        committed_blocks = remaining_unpublished_blocks_below_longest_chain[-runs[0]:] + committed_blocks
        remaining_unpublished_blocks_below_longest_chain = remaining_unpublished_blocks_below_longest_chain[:-runs[0]]
        remaining_heights_unpublished_blocks_below_longest_chain = remaining_heights_unpublished_blocks_below_longest_chain[:-runs[0]]
        deficits = deficits[1:]
        runs = runs[1:]

    og_committed_blocks = committed_blocks.copy()
    og_selfish_mining_blocks = selfish_mining_blocks.copy()

    # First feasible set of committed blocks.
    commitments += _get_available_commitments_fixed_committed_blocks(
        state,
        og_committed_blocks,
        og_selfish_mining_blocks,
        committed_blocks,
        selfish_mining_blocks,
        initial_position,
        deficits,
        runs,
        remaining_unpublished_blocks_below_longest_chain,
        remaining_heights_unpublished_blocks_below_longest_chain,
    )

    # Find all other feasible sets of committed blocks.
    for i in range(len(deficits)):
        if len(og_committed_blocks) - deficits[i] >= 1:
            committed_blocks = remaining_unpublished_blocks_below_longest_chain[-runs[i]:] + committed_blocks
            selfish_mining_blocks = og_selfish_mining_blocks[-(len(og_selfish_mining_blocks) - deficits[i] + 1):]
            remaining_unpublished_blocks_below_longest_chain = remaining_unpublished_blocks_below_longest_chain[:-runs[i]]
            remaining_heights_unpublished_blocks_below_longest_chain = remaining_heights_unpublished_blocks_below_longest_chain[:-runs[i]]
            commitments += _get_available_commitments_fixed_committed_blocks(
                state,
                og_committed_blocks,
                og_selfish_mining_blocks,
                committed_blocks,
                selfish_mining_blocks,
                len(selfish_mining_blocks) - 1,
                deficits[i+1:],
                runs[i+1:],
                remaining_unpublished_blocks_below_longest_chain,
                remaining_heights_unpublished_blocks_below_longest_chain,
            )
        else:
            break

    return commitments

def _get_available_commitments_fixed_committed_blocks(state: State,
                                                      og_committed_blocks : List[int],
                                                      og_selfish_mining_blocks : List[int],
                                                      committed_blocks: List[int],
                                                      selfish_mining_blocks: List[int],
                                                      initial_position: int,
                                                      deficits: List[int],
                                                      runs: List[int],
                                                      remaining_unpublished_blocks_below_longest_chain: List[int],
                                                      remaining_heights_unpublished_blocks_below_longest_chain: List[int]) -> List[Union[OneBoundaryCommitment, TwoBoundaryCommitment]]:
    """
    Get all commitments available at state `state` when the parameters of the
    commitment are fixed as the parameters to this function.
    """
    commitments: List[Union[OneBoundaryCommitment, TwoBoundaryCommitment]] = [{
        "committed_blocks": committed_blocks.copy(),
        "selfish_mining_blocks": selfish_mining_blocks.copy(),
        "initial_position": initial_position,
        "boundary": 0,
        "reward_at_boundary": (len(committed_blocks) + get_random_walk_one_boundary_increments(initial_position, 0)) * (1 - alpha) + (len(committed_blocks) - len(selfish_mining_blocks)) * alpha,
    }]

    recovered_blocks = []

    for i in range(len(deficits)):

        recovered_blocks = remaining_unpublished_blocks_below_longest_chain[-runs[i]:] + recovered_blocks
        remaining_unpublished_blocks_below_longest_chain = remaining_unpublished_blocks_below_longest_chain[:-runs[i]]

        if len(og_selfish_mining_blocks) - deficits[i] >= 0:
            continue

        else:
            absorption_probabilities = get_random_walk_boundary_absorption_probabilities(initial_position, 0, initial_position + deficits[i] - len(og_selfish_mining_blocks))
            increments = get_random_walk_two_boundary_conditional_increments(initial_position, 0, initial_position + deficits[i] - len(og_selfish_mining_blocks))

            commitments.append({
                "committed_blocks": committed_blocks.copy(),
                "selfish_mining_blocks": selfish_mining_blocks.copy(),
                "recovered_blocks": recovered_blocks.copy(),
                "initial_position": initial_position,
                "lower_boundary": 0,
                "upper_boundary": initial_position + deficits[i] - len(og_selfish_mining_blocks),
                "pr_lower_boundary": absorption_probabilities[0],
                "pr_upper_boundary": absorption_probabilities[1],
                "reward_at_lower_boundary": (len(committed_blocks) + increments[0]) * (1 - alpha) + (len(committed_blocks) - len(selfish_mining_blocks)) * alpha,
                "reward_at_upper_boundary": (len(recovered_blocks) + len(committed_blocks) + increments[1]) * (1 - alpha) + (len(recovered_blocks) + (deficits[i] - 1) + len(og_committed_blocks) - len(selfish_mining_blocks)) * alpha,
            })

    return commitments

def main():

    def aux(n: int, state: State):

        if len(state) == n:
            print(state)
            print("get_attacker_blocks: " + str(state.get_attacker_blocks()))
            print("get_honest_miner_blocks: " + str(state.get_honest_miner_blocks()))
            print("get_heights_unpublished_blocks_can_reach: " + str(get_heights_unpublished_blocks_can_reach(state)))
            print()
            return

        aux(n, state.next_state_attacker())
        aux(n, state.next_state_honest_miner())

    aux(3, State())

    start = State().next_state_honest_miner().next_state_honest_miner().next_state_attacker().next_state_attacker()
    end = start.next_state_from_action(2,2)
    sp.pprint(get_reward_between_states(start, end))
    print()

    start = State().next_state_attacker().next_state_attacker().next_state_honest_miner()
    end = start.next_state_from_action(2,0)
    sp.pprint(get_reward_between_states(start, end))
    print()

    start = State(sequence=('A', 'H', 'H', 'A', 'H', 'H', 'A'))
    end = start.next_state_from_action(1, 6)
    sp.pprint(get_reward_between_states(start, end))
    print()

    print(get_checkpoints(State(sequence=('H','A','H','H','A','H','A')).next_state_from_action(2,4)))
    print()

if __name__ == "__main__":
    main()

# Because this has proven more difficult than anticipated, this is what I think
# the outout should be:

{
    "genesis": [],
    "(A)": [],
    "(2A)": [
        {
            "committed_blocks": [
                1,
                2
            ],
            "selfish_mining_blocks": [
                1,
                2
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 2\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(2A, 2H)": [],
    "(2A, 2H, A)": [],
    "(3A)": [
        {
            "committed_blocks": [
                1,
                2,
                3
            ],
            "selfish_mining_blocks": [
                1,
                2,
                3
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, H, 2A)": [
        {
            "committed_blocks": [
                1,
                3,
                4
            ],
            "selfish_mining_blocks": [
                3,
                4
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, 2H, 3A)": [
        {
            "committed_blocks": [
                4,
                5,
                6
            ],
            "selfish_mining_blocks": [
                4,
                5,
                6
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                1,
                4,
                5,
                6
            ],
            "selfish_mining_blocks": [
                5,
                6
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 4\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, 3H, 2A)": [
        {
            "committed_blocks": [
                5,
                6
            ],
            "selfish_mining_blocks": [
                5,
                6
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 2\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                5,
                6
            ],
            "selfish_mining_blocks": [
                5,
                6
            ],
            "recovered_blocks": [
                1
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{3}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "3 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{7}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ],
    "(A, 3H, 3A)": [
        {
            "committed_blocks": [
                5,
                6,
                7
            ],
            "selfish_mining_blocks": [
                5,
                6,
                7
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, 3H, 4A)": [
        {
            "committed_blocks": [
                5,
                6,
                7,
                8
            ],
            "selfish_mining_blocks": [
                5,
                6,
                7,
                8
            ],
            "initial_position": 3,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{3 \\alpha}{1 - 2 \\alpha} + 4\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                1,
                5,
                6,
                7,
                8
            ],
            "selfish_mining_blocks": [
                7,
                8
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "3 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 5\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, 2H, A, 2H, 2A)": [
        {
            "committed_blocks": [
                7,
                8
            ],
            "selfish_mining_blocks": [
                7,
                8
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 2\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                7,
                8
            ],
            "selfish_mining_blocks": [
                7,
                8
            ],
            "recovered_blocks": [
                1,
                4
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{3}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "4 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{9}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ],
    "(3A, 2H, A, 2H, 2A)": [
        {
            "committed_blocks": [
                1,
                2,
                3,
                6,
                9,
                10
            ],
            "selfish_mining_blocks": [
                9,
                10
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "4 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 6\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(3A, 2H, 2A, 2H, 2A)": [
        {
            "committed_blocks": [
                1,
                2,
                3,
                6,
                7,
                10,
                11
            ],
            "selfish_mining_blocks": [
                7,
                10,
                11
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "4 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 7\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(3A, 2H, 2A, 2H, 4A, H)": [
        {
            "committed_blocks": [
                1,
                2,
                3,
                6,
                7,
                10,
                11,
                12,
                13
            ],
            "selfish_mining_blocks": [
                10,
                11,
                12,
                13
            ],
            "initial_position": 3,
            "boundary": 0,
            "reward_at_boundary": "5 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{3 \\alpha}{1 - 2 \\alpha} + 9\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(A, 3H, A, H, 2A)": [
        {
            "committed_blocks": [
                5,
                7,
                8
            ],
            "selfish_mining_blocks": [
                7,
                8
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                5,
                7,
                8
            ],
            "selfish_mining_blocks": [
                7,
                8
            ],
            "recovered_blocks": [
                1
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "\\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{5}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "4 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{9}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ],
    "(3A, 4H, A, 2H, 2A)": [
        {
            "committed_blocks": [
                11,
                12
            ],
            "selfish_mining_blocks": [
                11,
                12
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 2\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                11,
                12
            ],
            "selfish_mining_blocks": [
                11,
                12
            ],
            "recovered_blocks": [
                1,
                2,
                3,
                8
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{3}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "6 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{13}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ],
    "(3A, 4H, A, 2H, 3A)": [
        {
            "committed_blocks": [
                11,
                12,
                13
            ],
            "selfish_mining_blocks": [
                11,
                12,
                13
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                8,
                11,
                12,
                13
            ],
            "selfish_mining_blocks": [
                12,
                13
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 4\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        }
    ],
    "(3A, 5H, A, 2H, 3A)": [
        {
            "committed_blocks": [
                12,
                13,
                14
            ],
            "selfish_mining_blocks": [
                12,
                13,
                14
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                12,
                13,
                14
            ],
            "selfish_mining_blocks": [
                12,
                13,
                14
            ],
            "recovered_blocks": [
                1,
                2,
                3,
                9
            ],
            "initial_position": 2,
            "lower_boundary": 0,
            "upper_boundary": 3,
            "pr_lower_boundary": "\\frac{- \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(2 + \\frac{\\frac{- \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}} + \\frac{6 \\left(1 - \\alpha\\right)^{5}}{\\alpha^{5}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{2 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{2 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}\\right)}\\right)",
            "reward_at_upper_boundary": "7 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{15}{2} + \\frac{1 + \\frac{\\frac{6 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        },
        {
            "committed_blocks": [
                9,
                12,
                13,
                14
            ],
            "selfish_mining_blocks": [
                13,
                14
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 4\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                9,
                12,
                13,
                14
            ],
            "selfish_mining_blocks": [
                13,
                14
            ],
            "recovered_blocks": [
                1,
                2,
                3
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{7}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "7 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{15}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ],
    "(2A, 3H, 3A, 5H, A, 2H, 3A)": [
        {
            "committed_blocks": [
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                17,
                18,
                19
            ],
            "initial_position": 2,
            "boundary": 0,
            "reward_at_boundary": "\\left(1 - \\alpha\\right) \\left(\\frac{2 \\alpha}{1 - 2 \\alpha} + 3\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                17,
                18,
                19
            ],
            "recovered_blocks": [
                6,
                7,
                8,
                14
            ],
            "initial_position": 2,
            "lower_boundary": 0,
            "upper_boundary": 3,
            "pr_lower_boundary": "\\frac{- \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(2 + \\frac{\\frac{- \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}} + \\frac{6 \\left(1 - \\alpha\\right)^{5}}{\\alpha^{5}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{2 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{2 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}\\right)}\\right)",
            "reward_at_upper_boundary": "7 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{15}{2} + \\frac{1 + \\frac{\\frac{6 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        },
        {
            "committed_blocks": [
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                17,
                18,
                19
            ],
            "recovered_blocks": [
                1,
                2,
                6,
                7,
                8,
                14
            ],
            "initial_position": 2,
            "lower_boundary": 0,
            "upper_boundary": 4,
            "pr_lower_boundary": "\\frac{- \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}",
            "reward_at_lower_boundary": "\\left(1 - \\alpha\\right) \\left(2 + \\frac{\\frac{- \\frac{8 \\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}} + \\frac{8 \\left(1 - \\alpha\\right)^{6}}{\\alpha^{6}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}} + \\frac{2 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{2 \\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}\\right)}\\right)",
            "reward_at_upper_boundary": "10 \\alpha + \\left(1 - \\alpha\\right) \\left(10 + \\frac{2 + \\frac{\\frac{8 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} - \\frac{8 \\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}} + \\frac{2 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        },
        {
            "committed_blocks": [
                14,
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                18,
                19
            ],
            "initial_position": 1,
            "boundary": 0,
            "reward_at_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{\\alpha}{1 - 2 \\alpha} + 4\\right)",
            "pr_lower_boundary": "",
            "pr_upper_boundary": "",
            "reward_at_lower_boundary": "",
            "reward_at_upper_boundary": ""
        },
        {
            "committed_blocks": [
                14,
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                18,
                19
            ],
            "recovered_blocks": [
                6,
                7,
                8
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 2,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}",
            "reward_at_lower_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{7}{2} + \\frac{\\frac{- \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}} + \\frac{4 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}\\right)}\\right)",
            "reward_at_upper_boundary": "7 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{15}{2} + \\frac{1 + \\frac{\\frac{4 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{4 \\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{2}}{\\alpha^{2}}} + \\frac{1 - \\alpha}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        },
        {
            "committed_blocks": [
                14,
                17,
                18,
                19
            ],
            "selfish_mining_blocks": [
                18,
                19
            ],
            "recovered_blocks": [
                1,
                2,
                6,
                7,
                8
            ],
            "initial_position": 1,
            "lower_boundary": 0,
            "upper_boundary": 3,
            "pr_lower_boundary": "\\frac{- \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "pr_upper_boundary": "\\frac{-1 + \\frac{1 - \\alpha}{\\alpha}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}",
            "reward_at_lower_boundary": "2 \\alpha + \\left(1 - \\alpha\\right) \\left(\\frac{7}{2} + \\frac{\\frac{- \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}} + \\frac{6 \\left(1 - \\alpha\\right)^{4}}{\\alpha^{4}}}{1 - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{1 - \\alpha}{\\alpha} + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{2 \\left(2 \\alpha - 1\\right) \\left(\\frac{1 - \\alpha}{\\alpha} - \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}\\right)}\\right)",
            "reward_at_upper_boundary": "10 \\alpha + \\left(1 - \\alpha\\right) \\left(10 + \\frac{2 + \\frac{\\frac{6 \\left(1 - \\alpha\\right)}{\\alpha} - \\frac{6 \\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}}{-1 + \\frac{\\left(1 - \\alpha\\right)^{3}}{\\alpha^{3}}} + \\frac{2 \\left(1 - \\alpha\\right)}{\\alpha}}{2 \\left(1 - \\frac{1 - \\alpha}{\\alpha}\\right) \\left(2 \\alpha - 1\\right)}\\right)",
            "reward_at_boundary": ""
        }
    ]
}
