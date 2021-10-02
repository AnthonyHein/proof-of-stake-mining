from typing import List, Tuple, Union

from action import Action
from block import Block
from miner import Miner
from state import State


class Strategy:

    def __init__(self) -> None:
        """
        The constructor must set an instance variable `miner` of type `Miner`.
        """
        pass

    def get_action(
        self, state: State
    ) -> Union[Tuple[Action, None],
               Tuple[Action, Tuple[Miner, List[Block], dict[Block, Block]]],
               Tuple[Action, Tuple[Miner, List[Block], Block]],
               Tuple[Action, Tuple[Miner, List[Block], int, Block]]]:
        """"
        Get the action that this strategy will take given the state `state`.
        This returns a tuple of an `Action` and a tuple with all the arguments
        necessary for this action.
        """
        pass

    def get_capitulation(self, state: State) -> Tuple[Block, bool]:
        """
        Get the capitulation that this strategy will perform given the state 
        `state`. A capitulation is described by the block that this strategy
        will now view as the genesis block and a boolean flag whether this
        capitulation implies the game is over. Capitulations return `None,
        False` if a capitulation does not occur on this turn.
        """
        pass
