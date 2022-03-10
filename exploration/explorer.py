from known_states import known_states
from settings.setting import Setting
from state import State
from state_details import StateDetails
from state_utils import *
import time

class Explorer:

    def __init__(self, settings: Setting) -> None:
        """
        Initialize an object that can explore the state space under `settings`.
        """
        self.settings = settings
        self.lut: dict[State, StateDetails] = {}
        return

    def explore(self) -> None:
        """
        Explore the state space and, for each state, update `self.lut` with the
        most accurate `StateDetails` object possible. Return the number of
        states that were explored.
        """
        start = time.time()

        x = self._explore_state(State())

        print(f"Explored {x} states in {int(time.time() - start)} seconds.")
        
        self.lut = { k: v for k,v in self.lut.items() if v is not None }

        while True:
            start = time.time()
            x = self._fine_tune()
            print(f"Fine-tuned once in {int(time.time() - start)} seconds.")
            
            if x == 0:
                break

        if not self.settings["display_known_states"]:
            for known_state in known_states:
                if known_state in self.lut:
                    self.lut.pop(known_state)

        print("Done exploring.")

    def _explore_state(self, state: State) -> int:
        """
        Recursive helper function to `explore` which fills in `self.lut` for
        entry `state`. Return the number of states that were explored as a
        result of exploring `state`.
        """
        x = 0

        if state in self.lut:
            return x

        if len(state) > self.settings["exploration_depth"]:
            return x

        checkpoints = get_checkpoints(state)

        if len(checkpoints) > 1:
            return self._explore_state(state.next_state_from_capitulation(checkpoints[-1]))

        self.lut[state] = None

        if state not in known_states or self.settings["continue_from_known_states"]:
            for subsequent_state in get_subsequent_states(state):

                checkpoints = get_checkpoints(subsequent_state)

                if len(checkpoints) > 1:
                    subsequent_state = subsequent_state.next_state_from_capitulation(checkpoints[-1])

                x += self._explore_state(subsequent_state.next_state_attacker())
                x += self._explore_state(subsequent_state.next_state_honest_miner())

        if len(state) == self.settings["exploration_depth"] or self.settings["recurse"]:
            self.lut[state] = StateDetails(state, self.settings, self.lut)
            x += 1
        
        return x

    def _fine_tune(self) -> int:
        """
        Review all states and try to improve any bounds where possible. This is
        meant to be called _after_ `explore` and can be called as many times as
        necessary until the acquired knowledge reaches a steady state.
        """
        x = 0

        for state in self.lut:

            state_details = StateDetails(state, self.settings, self.lut)

            if self.lut[state] != state_details:
                self.lut[state] = state_details
                x += 1

        return x

    def get_settings(self) -> dict[str, object]:
        """
        Get the settings for this explorer object.
        """
        return self.settings

    def get_lut(self) -> dict[State, StateDetails]:
        """
        Get the lookup table `lut` which maps states to their details which
        were filled in during exploration.
        """
        return self.lut