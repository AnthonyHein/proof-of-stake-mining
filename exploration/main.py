import json
import os
import sys

from explorer import Explorer

PATH_TO_SETTINGS_DIR = "settings/"

def main():

    if len(sys.argv) != 2:
        print(f"driver.main: python3 smarter_driver.py <settings filename>")
        sys.exit(1)

    filename = PATH_TO_SETTINGS_DIR + sys.argv[1]

    if not os.path.exists(filename):
        print(f"driver.main: `{filename}` is not a valid settings file")
        sys.exit(1)

    settings = json.load(open(filename))

    explorer = Explorer(settings)
    
    print(f"Explored {explorer.explore()} states in total.\n")
    
    lut = explorer.get_lut()

    for state, state_details in lut.items():
        print(state_details)
        print()
        print()

if __name__ == "__main__":
    main()
