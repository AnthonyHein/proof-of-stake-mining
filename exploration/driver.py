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
        table[int(state)] = Cell(state).fill(conjectures, lemmas, settings["alpha-pos-lb"], settings["alpha-pos-ub"])
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
