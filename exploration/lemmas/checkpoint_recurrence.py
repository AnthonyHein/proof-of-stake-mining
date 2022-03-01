from typing import Callable, List, Tuple, Union

from conjectures.conjecture import Conjecture
from lemmas.lemma import Lemma
from state import State


DESCRIPTION = \
"""
If a checkpoint exists in the longest chain of a state, then the value of the state
can be upper bounded by value of the blocks owned that can reach height greater
than the checkpoint.
"""

class CheckpointRecurrence(Lemma):

    @staticmethod
    def get_name():
        """
        Return the name of the lemma.
        """
        return "Checkpoint Recurrence"

    @staticmethod
    def get_description():
        """
        Return a description of the lemma.
        """
        return DESCRIPTION

    @staticmethod
    def lower_bound(state: State,
                    settings: dict[str, object],
                    conjectures: List[Conjecture]) -> Union[Tuple[str, Callable[[float], float]], None]:
        """
        Return the lower bound to the value of `state` that is achieved
        by this lemma as a string formula and function of alpha, or `None`
        if this lemma does not prove any such lower bound.
        """
        return None

    @staticmethod
    def upper_bound(state: State,
                    settings: dict[str, object],
                    conjectures: List[Conjecture]) -> Union[Tuple[str, Callable[[float], float]], None]:
        """
        Return the upper bound to the value of `state` that is achieved
        by this lemma as a string formula and function of alpha, or `None`
        if this lemma does not prove any such upper bound.
        """

        # XXX: Need to add more logic here.

        if len(state.get_attacker_blocks()) == 0:
            return "0", lambda alpha: 0
        else:
            return None