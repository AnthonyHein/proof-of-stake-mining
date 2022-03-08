import sympy as sp
from typing import TypedDict

class KnownState(TypedDict):
    lower_bound: sp.core.Expr
    upper_bound: sp.core.Expr