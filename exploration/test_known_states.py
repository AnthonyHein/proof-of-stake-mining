import json

from known_states import known_states

def main():
    print(json.dumps([str(state) for state in known_states], indent = 2))

if __name__ == "__main__":
    main()