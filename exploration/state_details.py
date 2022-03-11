import numpy as np
import sympy as sp
import sys
from typing import List, Union

from bound import *
from lemmas.lemma_g8 import LemmaG8
from known_states import known_states
from lemmas import lemmas
from settings.setting import Setting
from state import State
from state_utils import *
from symbols import *

POINTS_SAMPLED = 100

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
        if len(self.state) < settings["exploration_depth"]:

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

                next_state_a = subsequent_state.next_state_attacker()
                next_state_h = subsequent_state.next_state_honest_miner()

                if next_state_a in lut and \
                lut[next_state_a] is not None and \
                next_state_h in lut and \
                lut[next_state_h] is not None:

                    next_state_a_lower_bound = lut[next_state_a].get_best_lower_bound()
                    next_state_a_upper_bound = lut[next_state_a].get_best_upper_bound()

                    next_state_h_lower_bound = lut[next_state_h].get_best_lower_bound()
                    next_state_h_upper_bound = lut[next_state_h].get_best_upper_bound()

                    next_state_a_lower_bound_expr = (next_state_a_lower_bound["immediate_reward"] if bound_isinstance(next_state_a_lower_bound, ActionLowerBound) else sp.Integer(0)) + next_state_a_lower_bound["lower_bound"]
                    next_state_a_upper_bound_expr = (next_state_a_upper_bound["immediate_reward"] if bound_isinstance(next_state_a_upper_bound, ActionUpperBound) else sp.Integer(0)) + next_state_a_upper_bound["upper_bound"]

                    next_state_h_lower_bound_expr = (next_state_h_lower_bound["immediate_reward"] if bound_isinstance(next_state_h_lower_bound, ActionLowerBound) else sp.Integer(0)) + next_state_h_lower_bound["lower_bound"]
                    next_state_h_upper_bound_expr = (next_state_h_upper_bound["immediate_reward"] if bound_isinstance(next_state_h_upper_bound, ActionUpperBound) else sp.Integer(0)) + next_state_h_upper_bound["upper_bound"]

                    self.bounds.append({
                        "action": action,
                        "immediate_reward": immediate_reward,
                        "subsequent_state": subsequent_state,
                        "lower_bound": alpha * next_state_a_lower_bound_expr + (1 - alpha) * (next_state_h_lower_bound_expr - alpha),
                        "upper_bound": alpha * next_state_a_upper_bound_expr + (1 - alpha) * (next_state_h_upper_bound_expr - alpha),
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

        self.best_lower_bound: ActionLowerBound = {
            "action": "Capitulate",
            "immediate_reward": sp.Integer(0),
            "subsequent_state": State(),
            "lower_bound": sp.Integer(0),
        }

        if len(list(filter(lambda x: bound_isinstance(x, ActionBound), self.bounds))) == 0:
            self.best_upper_bound: LemmaUpperBound = LemmaG8.upper_bound(settings, self.state)
        else:
            self.best_upper_bound: ActionUpperBound = {
                "action": "Dummy",
                "immediate_reward": sp.Integer(0),
                "subsequent_state": State(),
                "upper_bound": sp.Integer(0),
            }

        for bound in filter(lambda x: bound_isinstance(x, ActionBound), self.bounds):

            if self._bound_less_than(settings, self.best_lower_bound, bound, lower_bound=True):
                self.best_lower_bound = {
                    "action": bound["action"],
                    "immediate_reward": bound["immediate_reward"],
                    "subsequent_state": bound["subsequent_state"],
                    "lower_bound": bound["lower_bound"],
                }

            if self._bound_less_than(settings, self.best_upper_bound, bound, lower_bound=False):
                self.best_upper_bound = {
                    "action": bound["action"],
                    "immediate_reward": bound["immediate_reward"],
                    "subsequent_state": bound["subsequent_state"],
                    "upper_bound": bound["upper_bound"],
                }

        for bound in filter(lambda x: bound_isinstance(x, LemmaLowerBound), self.bounds):

            if self._bound_less_than(settings, self.best_lower_bound, bound, lower_bound=True):
                self.best_lower_bound = bound

        for bound in filter(lambda x: bound_isinstance(x, LemmaUpperBound), self.bounds):

            if self._bound_less_than(settings, bound, self.best_upper_bound, lower_bound=False):
                self.best_upper_bound = bound

    def _bound_less_than(self,
                         settings: Setting,
                         bound_a: Union[ActionBound, ActionLowerBound, ActionUpperBound, LemmaLowerBound, LemmaUpperBound],
                         bound_b: Union[ActionBound, ActionLowerBound, ActionUpperBound, LemmaLowerBound, LemmaUpperBound],
                         lower_bound: bool) -> bool:
        """
        Compare bounds `bound_a` and `bound_b` and return `True` if and only if
        the expression for `bound_a` is less than the expression for `bound_b`
        over the interval where `lower_bound` selects either an expression for
        the lower or upper bound. This comparison is checked over the interval
        (settings["alpha_pos_lower_bound], settings["alpha_pos_upper_bound]).
        """

        # Extract expressions.
        if bound_isinstance(bound_a, ActionBound) or bound_isinstance(bound_a, ActionLowerBound) or bound_isinstance(bound_a, ActionUpperBound):
            expr_a = bound_a["immediate_reward"] + bound_a["lower_bound" if lower_bound else "upper_bound"]
        else:
            expr_a = bound_a["lower_bound" if lower_bound else "upper_bound"]

        if bound_isinstance(bound_b, ActionBound) or bound_isinstance(bound_b, ActionLowerBound) or bound_isinstance(bound_b, ActionUpperBound):
            expr_b = bound_b["immediate_reward"] + bound_b["lower_bound" if lower_bound else "upper_bound"]
        else:
            expr_b = bound_b["lower_bound" if lower_bound else "upper_bound"]

        # Comparison
        if sp.simplify(expr_a - expr_b) == 0:
            return True

        xs = np.linspace(settings["alpha_pos_lower_bound"], settings["alpha_pos_upper_bound"], POINTS_SAMPLED)

        expr_a_fn = sp.lambdify(alpha, expr_a, 'numpy')
        expr_b_fn = sp.lambdify(alpha, expr_b, 'numpy')

        lst = zip([expr_a_fn(x) for x in xs], [expr_b_fn(x) for x in xs])

        soln = sum([eval_a <= eval_b for eval_a, eval_b in lst])

        if soln == POINTS_SAMPLED:
            return True

        elif soln == 0:
            return False

        else:
            print(f"state_details._bound_less_than: two bounds are incomparable when resolving {self.state}, in particular\n{bound_a}\nand\n{bound_b}")
            return True if soln >= POINTS_SAMPLED / 2 else False
            # sys.exit(1)

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

        s += "Action/Lemma, Immediate Reward, Subsequent State, Lower Bound, Upper Bound\n"
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