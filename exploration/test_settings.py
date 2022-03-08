import json
import os
import sys

from settings.setting import *

PATH_TO_SETTINGS_DIR = "settings/"

def main():

    for filename in list(filter(lambda x: x.endswith(".json"), os.listdir(PATH_TO_SETTINGS_DIR))):

        print(filename)
        print()

        settings = json.load(open(PATH_TO_SETTINGS_DIR + filename))

        print(json.dumps(settings, indent = 2))

        if not setting_isinstance(settings, Setting):
            print(f"test_settings.main: invalid settings file {filename}")
            sys.exit(1)

if __name__ == "__main__":
    main()