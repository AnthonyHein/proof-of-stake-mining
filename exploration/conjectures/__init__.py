import json
from typing import List

from conjectures.conjecture import Conjecture

conjectures: List[Conjecture] = json.load(open("conjectures/conjectures.json"))

def main():
    print(json.dumps(conjectures, indent = 2))

if __name__ == "__main__":
    main()