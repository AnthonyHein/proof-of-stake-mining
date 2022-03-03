import sys
from typing import List, Tuple

class State:

    def __init__(self,
                 sequence: Tuple[str, ...] = None,
                 longest_path: Tuple[int, ...] = None,
                 unpublished_blocks: Tuple[int, ...] =  None) -> None:
        """
        Initializes the state that results from mining sequence `sequence`
        with current longest path `longest_path` and unpublished blocks
        owned by the attacker `unpublished_blocks`. Note that `sequence`,
        `unpublished_blocks,` and `longest_path` fully determine the state
        of the game given the fixed strategy of the honest miner.
        """

        if sequence is None and (longest_path is not None or unpublished_blocks is not None):
            print(f"State.__init__: may not specify `longest_path` or `unpublished_blocks` without specifying `sequence`")
            sys.exit(1)

        if sequence is not None and not isinstance(sequence, Tuple):
            print(f"State.__init__: argument `sequence` to `__init__()` is not a tuple, with value {sequence}")
            sys.exit(1)
        if sequence is not None and not all(miner in ['A', 'H'] for miner in sequence):
            print(f"State.__init__: argument `sequence` to `__init__()` has an invalid miner, with value {sequence}")
            sys.exit(1)

        if sequence is None:
            sequence = ()

        if (longest_path is None and unpublished_blocks is not None) or (longest_path is not None and unpublished_blocks is None):
            print(f"State.__init__: may not specify exactly one of `longest_path` and `unpublished_blocks`")
            sys.exit(1)

        if longest_path is not None and not isinstance(longest_path, Tuple):
            print(f"State.__init__: argument `longest_path` to `__init__()` is not a tuple, with value {longest_path}")
            sys.exit(1)
        if longest_path is not None and not all(isinstance(block, int) for block in longest_path):
            print(f"State.__init__: argument `longest_path` to `__init__()` has an invalid block, with value {longest_path}")
            sys.exit(1)

        if unpublished_blocks is not None and not isinstance(unpublished_blocks, Tuple):
            print(f"State.__init__: argument `unpublished_blocks` to `__init__()` is not a tuple, with value {unpublished_blocks}")
            sys.exit(1)
        if unpublished_blocks is not None and not all(isinstance(block, int) for block in unpublished_blocks):
            print(f"State.__init__: argument `unpublished_blocks` to `__init__()` has an invalid block, with value {unpublished_blocks}")
            sys.exit(1)

        if longest_path is None:
            longest_path = tuple([0] + [i + 1 for i, v in enumerate(sequence) if v == 'H'])

        if unpublished_blocks is None:
            unpublished_blocks = tuple([i + 1 for i, v in enumerate(sequence) if v == 'A'])

        if not all(block <= len(sequence) for block in longest_path):
            print(f"State.__init__: block in `longest_path` {longest_path} has timestamp greater than sequence {sequence}")
            sys.exit(1)

        if not all(block <= len(sequence) for block in unpublished_blocks):
            print(f"State.__init__: block in `unpublished_blocks` {unpublished_blocks} has timestamp greater than sequence {sequence}")
            sys.exit(1)

        if set(unpublished_blocks).intersection(set(longest_path)) != set():
            print(f"State.__init__: intersection between `unpublished_blocks` {unpublished_blocks} and `longest_path` {longest_path} is non-empty")
            sys.exit(1)

        self.sequence = sequence
        self.longest_path = longest_path
        self.unpublished_blocks = unpublished_blocks

    def next_state_attacker(self) -> 'State':
        """"
        Get the state that follows `self` when the next miner is the attacker.
        """
        return State(
            sequence=tuple(list(self.sequence) + ['A']),
            longest_path=self.longest_path,
            unpublished_blocks=tuple(list(self.unpublished_blocks) + [len(self.sequence) + 1])
        )

    def next_state_honest_miner(self) -> 'State':
        """"
        Get the state that follows `self` when the next miner is the honest
        participant.
        """
        return State(
            sequence=tuple(list(self.sequence) + ['H']),
            longest_path=tuple(list(self.longest_path) + [len(self.sequence) + 1]),
            unpublished_blocks=self.unpublished_blocks
        )

    def next_state_from_action(self, k: int, v: int) -> 'State':
        """
        Get the state that follows action Publish(k, v), as defined
        in the paper. Since an optimal strategy is timeserving w.l.o.g., all
        actions that will ever be taken can be represented as such.
        """
        if k is None or v is None:
            print(f"State.next_state_from_action: one or more arguments are `None`")
            sys.exit(1)
        if not isinstance(k, int):
            print(f"State.next_state_from_action: argument `k` is not a valid number of blocks with value {k}")
            sys.exit(1)
        if not isinstance(v, int):
            print(f"State.next_state_from_action: argument `v` is not a valid block with value {v}")
            sys.exit(1)

        if len(list(filter(lambda x: x > v, self.unpublished_blocks))) < k:
            print(f"State.next_state_from_action: argument `k` with value {k} exceeds the number of unpublished blocks in {self.unpublished_blocks} that may be published on {v}")
            sys.exit(1)
        if v not in self.longest_path:
            print(f"State.next_state_from_action: argument `v` with value {v} is not in the longest path {self.longest_path}")
            sys.exit(1)
        if len(list(filter(lambda x: x > v, self.longest_path))) > k:
            print(f"State.next_state_from_action: argument `k` with value {k} is not large enough such that the action is timeserving for longest path {self.longest_path}")
            sys.exit(1)

        blocks = list(filter(lambda x: x > v, self.unpublished_blocks))[:k]

        return State(
            sequence=self.sequence,
            longest_path=tuple(list(filter(lambda x: x <= v, self.longest_path)) + blocks),
            unpublished_blocks=tuple(set(self.unpublished_blocks).difference(set(blocks)))
        )

    def next_state_from_capitulation(self, genesis: int) -> 'State':
        """
        Get the state that follows a miner's capitulation where they now view
        the block `genesis` as the genesis block, meaning that all blocks with
        timestamp less than this timestamp are forgotten.       
        """
        if genesis is None or not isinstance(genesis, int):
            print(f"State.next_state_from_capitulation: argument `genesis` is not a valid block with value {genesis}")
            sys.exit(1)
        if genesis not in self.longest_path:
            print(f"State.next_state_from_capitulation: argument `genesis` with value {genesis} is not in the longest path {self.longest_path}")
            sys.exit(1)

        return State(
            sequence=tuple(list(self.sequence)[genesis:]),
            longest_path=tuple([block - genesis for block in self.longest_path if block >= genesis]),
            unpublished_blocks=tuple([block - genesis for block in self.unpublished_blocks if block >= genesis]),
        )

    def get_sequence(self) -> Tuple[str, ...]:
        """
        Get the mining sequence at this state.
        """
        return self.sequence

    def get_longest_path(self) -> Tuple[int, ...]:
        """
        Get the list of blocks in the longest path at this state.
        """
        return self.longest_path

    def get_unpublished_blocks(self) -> Tuple[int, ...]:
        """
        Get the list of unpublished blocks at this state.
        """
        return self.unpublished_blocks

    def __len__(self) -> int:
        """
        Get the round at which a state occurs.
        """
        return len(self.sequence)

    def __eq__(self, other: 'State') -> bool:
        """
        Return `True` if two states are equal and false otherwise.
        """
        return self.sequence == other.sequence and \
               self.longest_path == other.longest_path and \
               self.unpublished_blocks == other.unpublished_blocks

    def __hash__(self):
        return hash((self.sequence, self.longest_path, self.unpublished_blocks))

    def __str__(self) -> str:
        """
        Return a human readable string summarizing a state.
        """

        if len(self.sequence) == 0:
            return "genesis"

        s = ""

        # Sequence ------------------------------------------------------------

        ch = None
        run = 0

        for miner in self.sequence:

            if ch is not None and ch == miner:
                run += 1
            else:
                s += f"{run if run != 1 else ''}{ch}, " if ch is not None else ""
                ch = miner
                run = 1
        
        s += f"{run if run != 1 else ''}{ch} " if ch is not None else ""

        s = f"({s.rstrip(', ')})"

        # Longest Path and Unpublished Blocks ---------------------------------

        honest_blocks = [i + 1 for i, v in enumerate(self.sequence) if v == 'H']

        if list(self.longest_path) != [0] + honest_blocks:
            s += f", Longest Path: {str(self.longest_path)}"
            s += f", Unpublished Blocks: {str(self.unpublished_blocks)}"
        
        # ---------------------------------------------------------------------

        return s

    def __repr__(self) -> str:
        """
        Return a string which can be used to reconstruct the state.
        """
        return f"State(\n\tsequence={self.sequence},\n\tlongest_path={self.longest_path},\n\tunpublished_blocks={self.unpublished_blocks},\n)"

def main():

    def aux(n: int, state: State):

        if len(state) == n:
            print("str: " + str(state))
            print("repr:\n" + repr(state))
            print("next_state_attacker: " + str(state.next_state_attacker()))
            print("next_state_honest_miner: " + str(state.next_state_honest_miner()))
            print("get_sequence: " + str(state.get_sequence()))
            print("get_longest_path: " + str(state.get_longest_path()))
            print("get_unpublished_blocks: " + str(state.get_unpublished_blocks()))
            print()
            return

        aux(n, state.next_state_attacker())
        aux(n, state.next_state_honest_miner())

    aux(3, State())

    state = State().next_state_honest_miner().next_state_honest_miner().next_state_attacker().next_state_attacker().next_state_from_action(2,1)
    print(state)
    print()

    state = State().next_state_attacker().next_state_attacker().next_state_honest_miner().next_state_from_action(2,0)
    print(state)
    print()

    state = State(sequence=('A', 'H', 'H', 'A', 'H', 'H', 'A')).next_state_from_action(1, 6)
    print(state)
    print()

    state = State().next_state_honest_miner().next_state_honest_miner().next_state_attacker().next_state_attacker().next_state_from_capitulation(2)
    print(state)
    print()

    state = State().next_state_attacker().next_state_attacker().next_state_honest_miner().next_state_from_capitulation(3)
    print(state)
    print()

    state = State(sequence=('A', 'H', 'H', 'A', 'H', 'H', 'A')).next_state_from_capitulation(5)
    print(state)
    print()

if __name__ == "__main__":
    main()