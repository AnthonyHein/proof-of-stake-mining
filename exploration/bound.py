import sympy as sp
import sys
from typing import Callable, Tuple, TypedDict

from state import State

class ActionBound(TypedDict):
    action: Tuple[int, int]
    immediate_reward: sp.core.Expr
    subsequent_state: State
    lower_bound: sp.core.Expr
    upper_bound: sp.core.Expr

class ActionLowerBound(TypedDict):
    action: Tuple[int, int]
    immediate_reward: sp.core.Expr
    subsequent_state: State
    lower_bound: sp.core.Expr

class ActionUpperBound(TypedDict):
    action: Tuple[int, int]
    immediate_reward: sp.core.Expr
    subsequent_state: State
    upper_bound: sp.core.Expr

class LemmaLowerBound(TypedDict):
    lemma: str
    lower_bound: sp.core.Expr

class LemmaUpperBound(TypedDict):
    lemma: str
    upper_bound: sp.core.Expr

def bound_isinstance(x: object, cls: Callable[[], None]) -> bool:
    keys = set()

    if cls == ActionBound:
        keys = set(["action", "immediate_reward", "subsequent_state", "lower_bound", "upper_bound"])

    elif cls == ActionLowerBound:
        keys = set(["action", "immediate_reward", "subsequent_state", "lower_bound"])

    elif cls == ActionUpperBound:
        keys = set(["action", "immediate_reward", "subsequent_state", "upper_bound"])

    elif cls == LemmaLowerBound:
        keys = set(["lemma", "lower_bound"])

    elif cls == LemmaUpperBound:
        keys = set(["lemma", "upper_bound"])

    else:
        print(f"bound.bound_isinstance: object {x} and class {cls} can not be checked by this method")
        sys.exit(1)

    return isinstance(x, dict) and set(x.keys()) == keys
