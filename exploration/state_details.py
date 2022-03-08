import sympy as sp
import sys
from typing import List, Union

from bound import *
from known_states import known_states
from lemmas import lemmas
from settings.setting import Setting
from state import State
from state_utils import *
from symbols import *

class StateDetails:

    def __init__(self,
                 state: State,
                 settings: Setting,
                 lut: dict[State, 'StateDetails']) -> None:
        """
        Initialize an object that will store a detailed view of `state`.
        """
        self.state: State = state
        self.bounds: List[Union[ActionBound, LemmaLowerBound, LemmaUpperBound]] = []
        self.best_lower_bound: Union[ActionLowerBound, LemmaLowerBound] = None
        self.best_upper_bound: Union[ActionUpperBound, LemmaUpperBound] = None

        self._fill(settings, lut)
        return

    def _fill(self, settings: Setting, lut: dict[State, 'StateDetails']) -> None:
        """
        Helper function for `__init__` that fills in the state details using `settings` and `lut`.
        """
        # Known States
        if self.state in known_states:
            best_lower_bound = {
                "lemma": "Known State",
                "lower_bound": known_states[self.state]["lower_bound"],
            }
            best_upper_bound = {
                "lemma": "Known State",
                "upper_bound": known_states[self.state]["upper_bound"],
            }
            self.bounds = [best_lower_bound, best_upper_bound]
            self.best_lower_bound = best_lower_bound
            self.best_upper_bound = best_upper_bound
            return

        # Action Bounds
        for action in get_available_actions(self.state):
            subsequent_state = self.state.next_state_from_action(*action)
            immediate_reward = get_reward_between_states(self.state, subsequent_state)

            checkpoints = get_checkpoints(subsequent_state)

            if len(checkpoints) > 1:
                subsequent_state = subsequent_state.next_state_from_capitulation(checkpoints[-1])

            if subsequent_state == State():
                self.bounds.append({
                    "action": action,
                    "immediate_reward": immediate_reward,
                    "subsequent_state": subsequent_state,
                    "lower_bound": sp.Integer(0),
                    "upper_bound": sp.Integer(0),
                })
                continue

            if subsequent_state.next_state_attacker() in lut and \
               lut[subsequent_state.next_state_attacker()] is not None and \
               subsequent_state.next_state_honest_miner() in lut and \
               lut[subsequent_state.next_state_honest_miner()] is not None:
                self.bounds.append({
                    "action": action,
                    "immediate_reward": immediate_reward,
                    "subsequent_state": subsequent_state,
                    "lower_bound": alpha * lut[subsequent_state.next_state_attacker()].get_best_lower_bound()["lower_bound"] + (1 - alpha) * lut[subsequent_state.next_state_honest_miner()].get_best_lower_bound()["lower_bound"],
                    "upper_bound": alpha * lut[subsequent_state.next_state_attacker()].get_best_upper_bound()["upper_bound"] + (1 - alpha) * lut[subsequent_state.next_state_honest_miner()].get_best_upper_bound()["upper_bound"],
                })

        # Lemma Lower Bounds:
        for lemma in lemmas:

            lower_bound = lemma.lower_bound(settings, self.state)

            if lower_bound is not None:
                self.bounds.append(lower_bound)

        # Lemma Upper Bounds
        for lemma in lemmas:

            upper_bound = lemma.upper_bound(settings, self.state)

            if upper_bound is not None:
                self.bounds.append(upper_bound)

        domain = sp.Interval(settings["alpha_pos_lower_bound"],settings["alpha_pos_upper_bound"]).intersect(sp.S.Reals)

        # Best Lower Bound
        self.best_lower_bound = {
            "action": "Unknown",
            "immediate_reward": sp.Integer(0),
            "subsequent_state": "Unknown",
            "lower_bound": sp.Integer(0),
        }

        for bound in self.bounds:

            if bound_isinstance(bound, LemmaUpperBound):
                continue

            a = (self.best_lower_bound["immediate_reward"] if bound_isinstance(self.best_lower_bound, ActionLowerBound) else sp.Integer(0)) + self.best_lower_bound["lower_bound"]
            b = (bound["immediate_reward"] if bound_isinstance(bound, ActionBound) else sp.Integer(0)) + bound["lower_bound"]

            soln = sp.solveset(a < b, alpha, domain)

            if soln == domain:
                if bound_isinstance(bound, ActionBound):
                    self.best_lower_bound = {
                        "action": bound["action"],
                        "immediate_reward": bound["immediate_reward"],
                        "subsequent_state": bound["subsequent_state"],
                        "lower_bound": bound["lower_bound"],
                    }
                else:
                    self.best_lower_bound = bound

            elif soln == sp.S.EmptySet:
                continue

            else:
                print(f"state_details._fill: two bounds are incomparable when resolving {self.state}, in particular\n{self.best_lower_bound}\nand\n{bound}")
                sys.exit(1)

        # Best Upper Bound
        self.best_upper_bound = {
            "action": "Unknown",
            "immediate_reward": sp.Integer(0),
            "subsequent_state": "Unknown",
            "upper_bound": sp.Integer(0),
        }

        for bound in self.bounds:

            if bound_isinstance(bound, LemmaLowerBound):
                continue

            a = (self.best_upper_bound["immediate_reward"] if bound_isinstance(self.best_upper_bound, ActionLowerBound) else sp.Integer(0)) + self.best_upper_bound["upper_bound"]
            b = (bound["immediate_reward"] if bound_isinstance(bound, ActionBound) else sp.Integer(0)) + bound["upper_bound"]

            soln = sp.solveset(a < b, alpha, domain)

            if soln == domain:
                if bound_isinstance(bound, ActionBound):
                    self.best_upper_bound = {
                        "action": bound["action"],
                        "immediate_reward": bound["immediate_reward"],
                        "subsequent_state": bound["subsequent_state"],
                        "upper_bound": bound["upper_bound"],
                    }
                else:
                    self.best_upper_bound = bound

            elif soln == sp.S.EmptySet:
                continue

            else:
                print(f"state_details._fill: two bounds are incomparable when resolving {self.state}, in particular\n{self.best_upper_bound}\nand\n{bound}")
                sys.exit(1)

    def get_state(self) -> State:
        """
        Return the `state`.
        """
        return self.state

    def get_bounds(self) -> List[Union[ActionBound, LemmaUpperBound]]:
        """
        Return the `bounds` for this state.
        """
        return self.bounds
    
    def get_best_lower_bound(self) -> ActionLowerBound:
        """
        Return the `best_lower_bound` for this state.
        """
        return self.best_lower_bound

    def get_best_upper_bound(self) -> Union[ActionUpperBound, LemmaUpperBound]:
        """
        Return the `best_upper_bound_str` for this state.
        """
        return self.best_upper_bound

    def __eq__(self, other: 'StateDetails') -> bool:
        """
        Return `True` if two state details are equal and false otherwise.
        """
        return self.state == other.state and \
               self.bounds == other.bounds and \
               self.best_lower_bound == other.best_lower_bound and \
               self.best_upper_bound == other.best_upper_bound

    def __str__(self) -> str:
        """
        Return a human readable string summarizing the state details.
        """

        s = ""

        s += "State: " + str(self.state) + "\n"

        s += "\n"

        s += "Action/Lemma, Subsequent State, Immediate Reward, Lower Bound, Upper Bound\n"
        for bound in self.bounds:

            if bound_isinstance(bound, ActionBound):
                s += str(bound["action"]) + ", "
                s += sp.latex(bound["immediate_reward"]) + ", "
                s += str(bound["subsequent_state"]) + ", "
                s += sp.latex(bound["lower_bound"]) + ", "
                s += sp.latex(bound["upper_bound"])

            elif bound_isinstance(bound, LemmaLowerBound):
                s += str(bound["lemma"]) + ",,,"
                s += sp.latex(bound["lower_bound"]) + ","

            elif bound_isinstance(bound, LemmaUpperBound):
                s += str(bound["lemma"]) + ",,,,"
                s += sp.latex(bound["upper_bound"])

            else:
                print(f"state_details.__str__: bound {bound} is not one of `ActionBound`, `LemmaLowerBound`, or `LemmaUpperBound`")
                sys.exit(1)

            s += "\n"
        
        s += "\n"

        s += "Best Lower Bound:\n"
        if bound_isinstance(self.best_lower_bound, ActionLowerBound):
            s += str(self.best_lower_bound["action"]) + ", "
            s += sp.latex(self.best_lower_bound["immediate_reward"]) + ", "
            s += str(self.best_lower_bound["subsequent_state"]) + ", "
            s += sp.latex(self.best_lower_bound["lower_bound"])
        elif bound_isinstance(self.best_lower_bound, LemmaLowerBound):
            s += str(self.best_lower_bound["lemma"]) + ", "
            s += sp.latex(self.best_lower_bound["lower_bound"])
        else:
            print(f"state_details.__str__: bound {self.best_lower_bound} is not one of `ActionLowerBound` or `LemmaLowerBound`")
            sys.exit(1)

        s += "\n\n"

        s += "Best Upper Bound:\n"
        if bound_isinstance(self.best_upper_bound, ActionUpperBound):
            s += str(self.best_upper_bound["action"]) + ", "
            s += sp.latex(self.best_upper_bound["immediate_reward"]) + ", "
            s += str(self.best_upper_bound["subsequent_state"]) + ", "
            s += sp.latex(self.best_upper_bound["upper_bound"])
        elif bound_isinstance(self.best_upper_bound, LemmaUpperBound):
            s += str(self.best_upper_bound["lemma"]) + ", "
            s += sp.latex(self.best_upper_bound["upper_bound"])
        else:
            print(f"state_details.__str__: bound {self.best_upper_bound} is not one of `ActionUpperBound` or `LemmaUpperBound`")
            sys.exit(1)

        return s

    def __repr__(self) -> str:
        """
        Return a representation of the state details.
        """
        return str(self)