from conjectures import conjectures
from lemmas import lemmas
from state import State

ALPHA_POS_LB = 0.3080
ALPHA_POS_UB = 0.3277

def main():

    state = State(['A', 'A', 'H'])

    for lemma in lemmas:

        print(lemma.get_name())
        print(lemma.get_description())
        print()
        

        lb = lemma.lower_bound(state, conjectures, ALPHA_POS_LB, ALPHA_POS_UB)
        ub = lemma.upper_bound(state, conjectures, ALPHA_POS_LB, ALPHA_POS_UB)

        if lb is not None:
            print(f"Lower bound to state {state}:")
            print(lb[0](alpha=1/3))
            print(lb[1])

        if ub is not None:
            print(f"Upper bound to state {state}:")
            print(ub[0](alpha=1/3))
            print(ub[1])

        print()

if __name__ == "__main__":
    main()