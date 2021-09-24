from random import random

from block import Block
from miner import Miner
from state import State
from state_utils import *
from strategy import Strategy

class Game:

    def __init__(self, miners: dict[Miner, Strategy], alpha: float) -> None:
        """
        Setup an instance of the mining game with strategies defined by `miners`
        and `alpha` representing the portion of the network controlled by the
        attacker.
        """
        if not isinstance(miners, dict):
            raise TypeError("Game.__init__: `miners` must be of type `dict[Miner, Strategy]`")
        if not all(isinstance(k, Miner) and isinstance(v, Strategy) for k, v in miners.items()):
            raise TypeError("Game.__init__: `miners` must be of type `dict[Miner, Strategy]`")
        if Miner.ATTACKER not in miners:
            raise ValueError("Game.__init__: `Miner.ATTACKER` must be a key in `miners`")
        if Miner.HONEST not in miners:
            raise ValueError("Game.__init__: `Miner.HONEST` must be a key in `miners`")

        self.miners: dict[Miner, Strategy] = miners
        self.alpha: float = alpha

        self.rewards: dict[Miner, int] = {
            Miner.ATTACKER: 0,
            Miner.HONEST: 0,
        }

        # note that state already starts with a genesis block
        self.state: State = State()

        # represents the next timestep at any given time
        self.timestep: int = 1

        # used for debugging, may want to move a half step at a time,
        # where a full step is always Miner.HONEST then Miner.ATTACKER
        self.at_half: bool = False

        # flag whether this game is completed
        self.is_completed: bool = False
        
    def _mine_block(self) -> Block:
        """
        Randomly select which miner will mine the next block, create this block,
        and return it. Also, increment the timestep of the game.
        """
        if self.at_half:
            raise RuntimeError("Game._mine_block: cannot mine blocks at half-steps")

        miner = Miner.ATTACKER if (random() <= self.alpha) else Miner.HONEST            
        return Block(miner, self.timestep)

    def _simulate_honest_half_step(self) -> 'Game':
        """
        Simulate a half-step when it is the honest miner's half of this timestep.
        """
        if self.at_half:
            raise RuntimeError("Game._simulate_honest_half_step: simulating the wrong miner's half-step")

        new_block = self._mine_block()
        self.state = self.state.mine_block(new_block)
        action = self.miners[Miner.HONEST].get_action(self.state)
        self.state = self.state.take_action(action)

        self.rewards = {
            Miner.ATTACKER: miner_k_reward(Miner.ATTACKER, State(), self.state),
            Miner.HONEST: miner_k_reward(Miner.HONEST, State(), self.state),
        }

        self.at_half = not self.at_half

        return self

    def _simulate_attacker_half_step(self) -> 'Game':
        """
        Simulate a half-step when it is the attacking miner's half of this timestep.
        """
        if not self.at_half:
            raise RuntimeError("Game._simulate_attacker_half_step: simulating the wrong miner's half-step")

        action = self.miners[Miner.ATTACKER].get_action(self.state)
        self.state = self.state.take_action(action)

        self.rewards = {
            Miner.ATTACKER: miner_k_reward(Miner.ATTACKER, State(), self.state),
            Miner.HONEST: miner_k_reward(Miner.HONEST, State(), self.state),
        }

        capitulation, is_completed = self.miners[Miner.ATTACKER].get_capitulation(self.state)

        # only capitulate if this is not a capitulation which ends the game (bc we want to observe final state)
        if not is_completed:
            self.state = self.state.capitulate(capitulation)

        # capitulation of a `Game` object only entails setting `self.timestep` correctly
        all_blocks = self.state.rounds_mined_on[Miner.ATTACKER] + self.state.rounds_mined_on[Miner.HONEST]
        self.timestep = max(all_blocks) if len(all_blocks) > 0 else 0

        self.at_half = not self.at_half
        self.timestep += 1

        self.is_completed = is_completed

        return self
        

    def simulate_half_step(self) -> 'Game':
        """
        Simulate a half-step from the current position of this mining game and
        return the result.
        """
        return self._simulate_attacker_half_step() if self.at_half else self._simulate_honest_half_step()

    def simulate_step(self) -> 'Game':
        """
        Simulate a full step from the current position of this mining game and return the result.
        """
        _ = self.simulate_half_step()
        return self.simulate_half_step()

    def simulate(self) -> 'Game':
        """
        Simulate the game until its completion and return the resulting game.
        """
        while not self.is_completed:
            self.simulate_step()
        
        return self
    
    def reset(self) -> 'Game':
        """
        Reset this game object to the state $B_{0,0}$ and return the result.
        """
        self.state = State()
        self.rewards = {
            Miner.ATTACKER: 0,
            Miner.HONEST: 0,
        }
        self.timestep = 1
        self.at_half = False
        self.is_completed = False

    def __repr__(self) -> str:
        """
        Return a string representing the current game.
        """

        s = "\n"
        s += "+----------------------------------------------------------+\n"
        s += "| MINING GAME START                                        |\n"
        s += "|                                                          |\n"
        s += "|                                                          |\n"
        s +=f"| Completed: {str(self.is_completed): <46}|\n"
        s +=f"| Timestep: {str(self.timestep): <47}|\n"
        s +=f"| At half: {str(self.at_half): <48}|\n"
        s += "|                                                          |\n"
        s += "| Miners:                                                  |\n"
        s += "|                                                          |\n"
        s +=f"| Attacker: {str(self.miners[Miner.ATTACKER]): <47}|\n"
        s +=f"| Honest: {str(self.miners[Miner.HONEST]): <49}|\n"
        s += "|                                                          |\n"
        s +=f"| alpha: {str(self.alpha): <50}|\n"
        s += "|                                                          |\n"
        s +=f"| Rewards:                                                 |\n"
        s += "|                                                          |\n"
        s +=f"| Attacker: {str(self.rewards[Miner.ATTACKER]): <47}|\n"
        s +=f"| Honest: {str(self.rewards[Miner.HONEST]): <49}|\n"
        s += "|                                                          |\n"
        s += str(self.state)
        s += "|                                                          |\n"
        s += "|                                                          |\n"
        s += "| MINING GAME END                                          |\n"
        s += "+----------------------------------------------------------+\n"

        return s