import json
import os
import sympy as sp
import sys
from typing import Optional

from bound import *
from lemmas import lemmas
from state import State

PATH_TO_SETTINGS_DIR = "settings/"

def main():

    if len(sys.argv) != 2:
        print(f"test_lemmas.main: python3 driver.py <settings filename>")
        sys.exit(1)

    filename = PATH_TO_SETTINGS_DIR + sys.argv[1]

    if not os.path.exists(filename):
        print(f"test_lemmas.main: `{filename}` is not a valid settings file")
        sys.exit(1)

    settings = json.load(open(filename))

    state = State(('A', 'H', 'H', 'A', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H',))

    for lemma in lemmas:

        print(lemma.get_name())
        print()

        lower_bound: Optional[LemmaLowerBound] = lemma.lower_bound(settings, state)
        upper_bound: Optional[LemmaUpperBound] = lemma.upper_bound(settings, state)

        if lower_bound is not None:
            if not bound_isinstance(lower_bound, LemmaLowerBound):
                print(f"test_lemmas.main: lower_bound {lower_bound} is not of type `LemmaLowerBound`")
                sys.exit(1)

            print(f"Lower bound to state {state}:\n")
            print(sp.latex(lower_bound['lower_bound']))

        if upper_bound is not None:
            if not bound_isinstance(upper_bound, LemmaUpperBound):
                print(f"test_lemmas.main: upper_bound {upper_bound} is not of type `LemmaUpperBound`")
                sys.exit(1)

            print(f"Upper bound to state {state}:\n")
            print(sp.latex(upper_bound['upper_bound']))

        print()

if __name__ == "__main__":
    main()