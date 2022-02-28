import json
import os
import sys

PATH_TO_SETTINGS_DIR = "settings/"

REQUIRED_KEYS = {
    "alpha-pos-lb": lambda x: isinstance(x, float),
    "alpha-pos-ub": lambda x: isinstance(x, float),
    "exploration-depth": lambda x: isinstance(x, int),
    "conjectures": lambda xs: isinstance(xs, list) and all([isinstance(x, int) for x in xs]),
    "ub-assumes-wait": lambda x: isinstance(x, bool) 
}

def main():

    for filename in os.listdir(PATH_TO_SETTINGS_DIR):

        print(filename)
        print()

        settings = json.load(open(PATH_TO_SETTINGS_DIR + filename))

        print(json.dumps(settings, indent = 2))

        for key in REQUIRED_KEYS:
            if key not in settings:
                print(f"test_settings.main: key `{key}` not found in settings file `{filename}`")
                sys.exit(1)
            if not REQUIRED_KEYS[key](settings[key]):
                print(f"test_settings.main: value `{settings[key]}` for key `{key}` in settings file `{filename}` is the wrong type")
                sys.exit(1)

if __name__ == "__main__":
    main()