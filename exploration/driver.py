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
             conjectures: List[Conjecture],
             lemmas: List[Lemma],
             table: List[Cell],
             state: State) -> List[Cell]:

    if len(state) > settings["exploration-depth"]:
        return table

    if state not in known_states or settings["continue-from-known-states"]:
        table = tabulate(settings, known_states, conjectures, lemmas, table, state.next_state_attacker())
        table = tabulate(settings, known_states, conjectures, lemmas, table, state.next_state_honest_miner())
    
    cell = Cell(state).fill(settings, known_states, conjectures, lemmas, table)

    if len(state) == settings["exploration-depth"] or settings["recurse"]:
        table[int(state)] = cell

    return table

def main():

    if len(sys.argv) != 2:
        print(f"driver.main: python3 smarter_driver.py <settings filename>")
        sys.exit(1)

    filename = PATH_TO_SETTINGS_DIR + sys.argv[1]

    if not os.path.exists(filename):
        print(f"driver.main: `{filename}` is not a valid settings file")
        sys.exit(1)

    settings = json.load(open(filename))

    table: List[Cell] = [None] * (pow(2, settings["exploration-depth"] + 1) - 1)
    state = State(
        sequence=(),
        capacity=settings["exploration-depth"],
    )

    table = tabulate(
        settings=settings,
        known_states=known_states,
        conjectures=conjectures,
        lemmas=lemmas,
        table=table,
        state=state,
    )

    save(settings, table)

if __name__ == "__main__":
    main()
