import json
import os
import sys

from conjectures import conjectures
from lemmas import lemmas
from state import State

PATH_TO_SETTINGS_DIR = "settings/"

ALPHA_POS_LB = 0.3080
ALPHA_POS_UB = 0.3277

def main():

    if len(sys.argv) != 2:
        print(f"driver.main: python3 driver.py <settings filename>")
        sys.exit(1)

    filename = PATH_TO_SETTINGS_DIR + sys.argv[1]

    if not os.path.exists(filename):
        print(f"driver.main: `{filename}` is not a valid settings file")
        sys.exit(1)

    settings = json.load(open(filename))
    cjctrs = list(filter(lambda x: x["id"] in settings["conjectures"], conjectures))

    state = State(('A', 'H', 'H', 'A', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H',))

    for lemma in lemmas:

        print(lemma.get_name())
        print(lemma.get_description())
        print()
        

        lb = lemma.lower_bound(state, cjctrs, settings["alpha-pos-lb"], settings["alpha-pos-ub"])
        ub = lemma.upper_bound(state, cjctrs, settings["alpha-pos-lb"], settings["alpha-pos-ub"])

        if lb is not None:
            print(f"Lower bound to state {state}:")
            print(lb[0])
            print(lb[1](settings["alpha-pos-lb"]))

        if ub is not None:
            print(f"Upper bound to state {state}:")
            print(ub[0])
            print(ub[1](settings["alpha-pos-lb"]))

        print()

if __name__ == "__main__":
    main()