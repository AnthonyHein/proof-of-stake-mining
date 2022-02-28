import json
import os
import sys
from typing import List

from cell import Cell
from conjectures import conjectures
from conjectures.conjecture import Conjecture
from known_states import known_states
from lemmas import lemmas
from lemmas.lemma import Lemma
from state import State
from visualize import save

PATH_TO_SETTINGS_DIR = "settings/"

def tabulate(settings,
             known_states: List[State],
             table: List[Cell],
             conjectures: List[Conjecture],
             lemmas: List[Lemma],
             state: State) -> List[Cell]:
    
    if state in known_states:
        return table

    if len(state) >= settings["exploration-depth"]:
    
        c = Cell(state).fill(conjectures, lemmas, settings["alpha-pos-lb"], settings["alpha-pos-ub"])

        if settings["ub-assumes-wait"]:
            c_next_a = Cell(state.next_state_attacker()).fill(conjectures, lemmas, settings["alpha-pos-lb"], settings["alpha-pos-ub"])
            c_next_h = Cell(state.next_state_honest_miner()).fill(conjectures, lemmas, settings["alpha-pos-lb"], settings["alpha-pos-ub"])
            c = Cell(
                state,
                c.get_lb_lemma(),
                c.get_lb_str(),
                c.get_lb_fn(),
                c_next_a.get_ub_lemma() + ", " + c_next_h.get_ub_lemma(),
                "\\alpha\\bigg(" + c_next_a.get_ub_str() + "\\bigg) + (1 - \\alpha)\\bigg(" + c_next_h.get_ub_str() + "\\bigg)",
                lambda alpha: alpha * c_next_a.get_ub_fn()(alpha) + (1  - alpha) * c_next_h.get_ub_fn()(alpha))

        table[int(state)] = c
        return table

    table = tabulate(settings, known_states, table, conjectures, lemmas, state.next_state_attacker())
    table = tabulate(settings, known_states, table, conjectures, lemmas, state.next_state_honest_miner())
    return table

def main():

    if len(sys.argv) != 2:
        print(f"driver.main: python3 driver.py <settings filename>")
        sys.exit(1)

    filename = PATH_TO_SETTINGS_DIR + sys.argv[1]

    if not os.path.exists(filename):
        print(f"driver.main: `{filename}` is not a valid settings file")
        sys.exit(1)

    settings = json.load(open(filename))

    table: List[Cell] = [None] * pow(2, settings["exploration-depth"])
    state = State()

    table = tabulate(
        settings=settings,
        known_states=known_states,
        table=table,
        conjectures=list(filter(lambda x: x["id"] in settings["conjectures"], conjectures)),
        lemmas=lemmas,
        state=state
    )

    save(settings, table)

if __name__ == "__main__":
    main()
