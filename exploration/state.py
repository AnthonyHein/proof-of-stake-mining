from typing import List

class State:

    def __init__(self, sequence: List[str] = []) -> None:
        """
        Initializes the state that results from mining sequence `sequence`
        where the honest miner plays \textsc{Frontier} and the attacker has
        not published any blocks.
        """

        if sequence is None or not isinstance(sequence, List):
            print(f"State.__init__: argument `sequence` to `__init__()` is not a list, with value {sequence}")
        if not all(miner in ['A', 'H'] for miner in sequence):
            print(f"State.__init__: argument `sequence` to `__init__()` has an invalid miner, with value {sequence}")

        self.sequence = sequence
        self.id = sum([int(v == 'A') * pow(2, len(self.sequence) - i - 1) for i, v in enumerate(self.sequence)])

    def next_state_attacker(self) -> 'State':
        """"
        Get the state that follows `self` when the next miner is the attacker.
        """
        return State(self.sequence + ['A'])

    def next_state_honest_miner(self) -> 'State':
        """"
        Get the state that follows `self` when the next miner is the honest
        participant.
        """
        return State(self.sequence + ['H'])

    def get_attacker_blocks(self) -> List[int]:
        """"
        Get the list of all blocks mined by the attacker at this state.
        """
        return [i for i, v in enumerate(self.sequence) if v == 'A']

    def get_honest_miner_blocks(self) -> List[int]:
        """"
        Get the list of all blocks mined by the honest miner at this state.
        """
        return [i for i, v in enumerate(self.sequence) if v == 'H']

    def get_longest_path(self) -> List[int]:
        """
        Get the list of blocks in the longest chain at this state, which is
        just the list of honest miner blocks by assumption.
        """
        return self.get_honest_miner_blocks()

    def __len__(self) -> int:
        """
        Get the round at which a state occurs.
        """
        return len(self.sequence)

    def __int__(self) -> int:
        """
        Get the natural number which corresponds to this state, where the state
        is treated as a bitstring with the last miner the lowest-order bit, an
        'A' represents a '1', and an 'H' represents a '0'.
        """
        return self.id

    def __eq__(self, other: 'State') -> bool:
        """
        Return `True` if two states are equal and false otherwise.
        """
        return self.sequence == other.sequence

    def __str__(self) -> str:
        """
        Return a human readable string summarizing a state.
        """

        s = ""

        c = None
        run = 0

        for miner in self.sequence:

            if c is not None and c == miner:
                run += 1
            else:
                s += f"{run if run != 1 else ''}{c}, " if c is not None else ""
                c = miner
                run = 1
        
        s += f"{run if run != 1 else ''}{c} " if c is not None else ""

        return f"[{s.rstrip(', ')}]"

    def __repr__(self) -> str:
        """
        Return a string which can be used to reconstruct the state.
        """
        return f"State(sequence={self.sequence})"

def main():

    print(State())
    print(State().next_state_attacker().next_state_attacker())
    print(State().next_state_attacker().next_state_honest_miner())
    print(State().next_state_honest_miner().next_state_attacker())
    print(State().next_state_honest_miner().next_state_honest_miner())
    print()
    print(repr(State()))
    print(repr(State().next_state_attacker().next_state_attacker()))
    print(repr(State().next_state_attacker().next_state_honest_miner()))
    print(repr(State().next_state_honest_miner().next_state_attacker()))
    print(repr(State().next_state_honest_miner().next_state_honest_miner()))
    print()
    print(State().get_attacker_blocks())
    print(State().next_state_attacker().next_state_attacker().get_attacker_blocks())
    print(State().next_state_attacker().next_state_honest_miner().get_attacker_blocks())
    print(State().next_state_honest_miner().next_state_attacker().get_attacker_blocks())
    print(State().next_state_honest_miner().next_state_honest_miner().get_attacker_blocks())
    print()
    print(State().get_honest_miner_blocks())
    print(State().next_state_attacker().next_state_attacker().get_honest_miner_blocks())
    print(State().next_state_attacker().next_state_honest_miner().get_honest_miner_blocks())
    print(State().next_state_honest_miner().next_state_attacker().get_honest_miner_blocks())
    print(State().next_state_honest_miner().next_state_honest_miner().get_honest_miner_blocks())
    print()
    print(len(State()))
    print(len(State().next_state_attacker().next_state_attacker()))
    print(len(State().next_state_attacker().next_state_honest_miner()))
    print(len(State().next_state_honest_miner().next_state_attacker()))
    print(len(State().next_state_honest_miner().next_state_honest_miner()))
    print()
    print(int(State()))
    print(int(State().next_state_attacker().next_state_attacker()))
    print(int(State().next_state_attacker().next_state_honest_miner()))
    print(int(State().next_state_honest_miner().next_state_attacker()))
    print(int(State().next_state_honest_miner().next_state_honest_miner()))
    print()

if __name__ == "__main__":
    main()