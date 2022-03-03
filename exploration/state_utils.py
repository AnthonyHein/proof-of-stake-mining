import sympy as sp
import sys
from typing import List, Tuple

from state import State

def get_attacker_blocks(state: State) -> List[int]:
    """"
    Get the list of all blocks mined by the attacker at this state.
    """
    return tuple([i + 1 for i, v in enumerate(state.get_sequence()) if v == 'A'])

def get_honest_miner_blocks(state: State) -> List[int]:
    """"
    Get the list of all blocks mined by the honest miner at this state.
    """
    return tuple([i + 1 for i, v in enumerate(state.get_sequence()) if v == 'H'])

def get_checkpoints(state: State) -> List[int]:
    """
    Get a list of all checkpoints in state `state`.
    """
    attacker_blocks = get_attacker_blocks(state)

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

    attacker_blocks_start = get_attacker_blocks(start)
    attacker_blocks_end = get_attacker_blocks(end)

    honest_miner_blocks_start = get_honest_miner_blocks(start)
    honest_miner_blocks_end = get_honest_miner_blocks(end)

    delta_attacker_blocks_in_longest_path = len(list(filter(lambda x: x in attacker_blocks_end, end.get_longest_path()))) - \
                                            len(list(filter(lambda x: x in attacker_blocks_start, start.get_longest_path())))

    delta_honest_miner_blocks_in_longest_path = len(list(filter(lambda x: x in honest_miner_blocks_end, end.get_longest_path()))) - \
                                                len(list(filter(lambda x: x in honest_miner_blocks_start, start.get_longest_path())))

    lamba = sp.symbols('lambda')

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

    attacker_blocks = get_attacker_blocks(state)
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

def main():

    def aux(n: int, state: State):

        if len(state) == n:
            print(state)
            print("get_attacker_blocks: " + str(get_attacker_blocks(state)))
            print("get_honest_miner_blocks: " + str(get_honest_miner_blocks(state)))
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