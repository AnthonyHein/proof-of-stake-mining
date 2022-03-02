import dill
import sys
from typing import Callable, List

from conjectures.conjecture import Conjecture
from known_states.known_state import KnownState
from lemmas.lemma import Lemma
from state import State

class Cell:

    def __init__(self,
                 state: State,
                 lb_lemma: str = None,
                 lb_str: str = None,
                 lb_fn: Callable[[float], float] = None,
                 ub_lemma: str = None,
                 ub_str: str = None,
                 ub_fn: Callable[[float], float] = None) -> None:
        """
        Initialize a table cell for state `state`.
        """

        if not isinstance(state, State):
            print(f"Cell.__init__: parameter `state` not a valid state with value {state}")
            sys.exit(1)
        if lb_lemma is not None and not isinstance(lb_lemma, str):
            print(f"Cell.__init__: parameter `lbd_lemma` not a valid lemma with value {lb_lemma}")
            sys.exit(1)
        if lb_str is not None and not isinstance(lb_str, str):
            print(f"Cell.__init__: parameter `lb_str` not a valid string with value {lb_str}")
            sys.exit(1)
        if lb_fn is not None and not callable(lb_fn):
            print(f"Cell.__init__: parameter `lb_fn` not a valid function with value {lb_fn}")
            sys.exit(1)
        if ub_lemma is not None and not isinstance(ub_lemma, str):
            print(f"Cell.__init__: parameter `upper_bound_lemma` not a valid lemma with value {ub_lemma}")
            sys.exit(1)
        if ub_str is not None and not isinstance(ub_str, str):
            print(f"Cell.__init__: parameter `ub_str` not a valid string with value {ub_str}")
            sys.exit(1)
        if ub_fn is not None and not callable(ub_fn):
            print(f"Cell.__init__: parameter `ub_fn` not a valid function with value {ub_fn}")
            sys.exit(1)

        self.state = state
        self.lb_lemma = lb_lemma
        self.lb_str = lb_str
        self.lb_fn = lb_fn
        self.ub_lemma = ub_lemma
        self.ub_str = ub_str
        self.ub_fn = ub_fn

    def fill(self,
             settings: dict[str, object],
             known_states: dict[State, KnownState],
             conjectures: List[Conjecture],
             lemmas: List[Lemma],
             table: List['Cell']) -> 'Cell':
        """
        Fill a table cell with all descriptive information
        about the state `state` it represents.
        """
        if self.state in known_states:
            return Cell(
                state=self.state,
                lb_lemma="Known State",
                lb_str=known_states[self.state]["value_str"],
                lb_fn=dill.loads(known_states[self.state]["value_fn"]),
                ub_lemma="Known State",
                ub_str=known_states[self.state]["value_str"],
                ub_fn=dill.loads(known_states[self.state]["value_fn"]),
            )

        return self._fill_lower_bound(settings, known_states, conjectures, lemmas, table) \
                   ._fill_upper_bound(settings, known_states, conjectures, lemmas, table)

    def _fill_lower_bound(self,
                          settings: dict[str, object],
                          known_states: dict[State, KnownState],
                          conjectures: List[Conjecture],
                          lemmas: List[Lemma],
                          table: List['Cell']) -> 'Cell':
        """
        Fill a table cell with all dsescriptive information
        about the lower bound to the state `state` it represents.
        """
        best_lb_lemma: str = "None"
        best_lb_str: str = "None"
        best_lb_fn: Callable[[float], float] = lambda x: 0

        for lemma in lemmas:

            lb = lemma.lower_bound(self.state, settings, conjectures)

            if lb is None:
                continue

            lb_str, lb_fn = lb

            # We will assume that all lower bounds are increasing in alpha.
            # This assumption is necessary to compare lower bounds.
            if lb_fn(settings["alpha-pos-lb"]) > best_lb_fn(settings["alpha-pos-lb"]) or best_lb_lemma == "None":
                best_lb_lemma = lemma.get_name()
                best_lb_str = lb_str
                best_lb_fn = lb_fn
        
        state_next_a = self.state.next_state_attacker()
        state_next_h = self.state.next_state_honest_miner()

        if len(table) > int(state_next_a) and len(table) > int(state_next_h):
            cell_next_a = table[int(state_next_a)]
            cell_next_h = table[int(state_next_h)]

            cell_wait_lb_lemma = " wait then<ul><li>if next block is A then " + cell_next_a.get_lb_lemma() + "</li><li>if next block is H then " + cell_next_h.get_lb_lemma() + "</li></ul>"
            cell_wait_lb_str = "\\alpha\\bigg(" + cell_next_a.get_lb_str() + "\\bigg) + (1 - \\alpha)\\bigg(" + cell_next_h.get_lb_str() + " - \\lambda\\bigg)"
            cell_wait_lb_fn = lambda alpha: alpha * cell_next_a.get_lb_fn()(alpha) + (1  - alpha) * (cell_next_h.get_lb_fn()(alpha) - alpha)

            if cell_wait_lb_fn(settings["alpha-pos-lb"]) > best_lb_fn(settings["alpha-pos-lb"]) or best_lb_lemma == "None":
                best_lb_lemma = cell_wait_lb_lemma
                best_lb_str = cell_wait_lb_str
                best_lb_fn = cell_wait_lb_fn

        return Cell(
            state=self.state,
            lb_lemma=best_lb_lemma,
            lb_str=best_lb_str,
            lb_fn=best_lb_fn,
            ub_lemma=self.ub_lemma,
            ub_str=self.ub_str,
            ub_fn=self.ub_fn
        )

    def _fill_upper_bound(self,
                          settings: dict[str, object],
                          known_states: dict[State, KnownState],
                          conjectures: List[Conjecture],
                          lemmas: List[Lemma],
                          table: List['Cell']) -> 'Cell':
        """
        Fill a table cell with all dsescriptive information
        about the upper bound to the state `state` it represents.
        """
        best_ub_lemma: str = "None"
        best_ub_str: str = "None"
        best_ub_fn: Callable[[float], float] = lambda x: float("inf")

        for lemma in lemmas:

            ub = lemma.upper_bound(self.state, settings, conjectures)

            if ub is None:
                continue

            ub_str, ub_fn = ub

            # We will assume that all upper bounds are increasing in alpha.
            # This assumption is necessary to compare upper bounds.
            if ub_fn(settings["alpha-pos-ub"]) < best_ub_fn(settings["alpha-pos-ub"]) or best_ub_lemma == "None":
                best_ub_lemma = lemma.get_name()
                best_ub_str = ub_str
                best_ub_fn = ub_fn

        state_next_a = self.state.next_state_attacker()
        state_next_h = self.state.next_state_honest_miner()

        if len(table) > int(state_next_a) and len(table) > int(state_next_h):
            cell_next_a = table[int(state_next_a)]
            cell_next_h = table[int(state_next_h)]

            cell_wait_ub_lemma = " wait then<ul><li>if next block is A then " + cell_next_a.get_ub_lemma() + "</li><li>if next block is H then " + cell_next_h.get_ub_lemma() + "</li></ul>"
            cell_wait_ub_str = "\\alpha\\bigg(" + cell_next_a.get_ub_str() + "\\bigg) + (1 - \\alpha)\\bigg(" + cell_next_h.get_ub_str() + " - \\lambda\\bigg)"
            cell_wait_ub_fn = lambda alpha: alpha * cell_next_a.get_ub_fn()(alpha) + (1  - alpha) * (cell_next_h.get_ub_fn()(alpha) - alpha)

            if cell_wait_ub_fn(settings["alpha-pos-ub"]) < best_ub_fn(settings["alpha-pos-ub"]) or best_ub_lemma == "None":
                best_ub_lemma = cell_wait_ub_lemma
                best_ub_str = cell_wait_ub_str
                best_ub_fn = cell_wait_ub_fn
        
        return Cell(
            state=self.state,
            lb_lemma=self.lb_lemma,
            lb_str=self.lb_str,
            lb_fn=self.lb_fn,
            ub_lemma=best_ub_lemma,
            ub_str=best_ub_str,
            ub_fn=best_ub_fn
        )

    def get_state(self) -> State:
        """
        Return the state which this cell represents.
        """
        return self.state

    def get_lb_lemma(self) -> str:
        """
        Return the lemma which provides the best lower bound
        to the state which this cell represents.
        """
        return self.lb_lemma
    
    def get_lb_str(self) -> str:
        """
        Return the string formula which is the best lower bound
        to the state which this cell represents.
        """
        return self.lb_str
    
    def get_lb_fn(self) -> str:
        """
        Return the function provides the best lower bound
        to the state which this cell represents.
        """
        return self.lb_fn
    
    def get_ub_lemma(self) -> str:
        """
        Return the lemma which provides the best upper bound
        to the state which this cell represents.
        """
        return self.ub_lemma
    
    def get_ub_str(self) -> str:
        """
        Return the string formula which is the best upper bound
        to the state which this cell represents.
        """
        return self.ub_str
    
    def get_ub_fn(self) -> str:
        """
        Return the function provides the best upper bound
        to the state which this cell represents.
        """
        return self.ub_fn