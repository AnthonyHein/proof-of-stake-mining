import csv
from datetime import datetime
import dill
import json
import os
import sys
from typing import List

from cell import Cell
from conjectures import conjectures
from conjectures.conjecture import Conjecture
from lemmas import lemmas
from lemmas.lemma import Lemma
from state import State

PATH_TO_SETTINGS_DIR = "settings/"
PATH_TO_RESULTS_DIR = "results/"

ALPHA_POS_LB = 0.3080
ALPHA_POS_UB = 0.3277

def tabulate(settings,
             table: List[Cell],
             conjectures: List[Conjecture],
             lemmas: List[Lemma],
             state: State) -> List[Cell]:

    if len(state) >= settings["exploration-depth"]:
        table[int(state)] = Cell(state).fill(conjectures, lemmas, ALPHA_POS_LB, ALPHA_POS_UB)
        return table

    table = tabulate(settings, table, conjectures, lemmas, state.next_state_attacker())
    table = tabulate(settings, table, conjectures, lemmas, state.next_state_honest_miner())
    return table

def save(settings, table: List[Cell]) -> None:

    f = open(PATH_TO_RESULTS_DIR + datetime.now().strftime("%m-%d-%Y--%H-%M-%S") + ".csv", "w")
    f.write(f"alpha_pos_lb,{ALPHA_POS_LB},,,,,,\n")
    f.write(f"settings['exploration-depth'],{settings['exploration-depth']},,,,,,\n")
    f.write(f"settings['conjectures'],{settings['conjectures']},,,,,,\n")
    f.write(f"id,state,lb_lemma,lb_str,lb_fn,ub_lemma,ub_str,ub_fn\n")

    for cell in table:
        f.write(
            str(int(cell.get_state())) + "," +
            str(cell.get_state()) + "," +
            str(cell.get_lb_lemma()) + "," +
            str(cell.get_lb_str()) + "," +
            str(dill.dumps(cell.get_lb_fn())) + "," +
            str(cell.get_ub_lemma()) + "," +
            str(cell.get_ub_str()) + "," +
            str(dill.dumps(cell.get_ub_fn())) + "\n"
        )

    f.close()

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
        table=table,
        conjectures=filter(lambda x: x["id"] in settings["conjectures"], conjectures),
        lemmas=lemmas,
        state=state
    )

    save(settings, table)

if __name__ == "__main__":
    main()
