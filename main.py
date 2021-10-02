import csv
import numpy as np
from tqdm import tqdm

from game import Game
from miner import Miner
from strategy import Strategy

# strategies
from frontier import Frontier
from sm import SM
from nsm import NSM

TRIALS = 10000

LO = 0.30
HI = 0.40
STEP = 0.005

def get_reward(miners, alpha: float) -> float:

    game = Game(miners, alpha)

    attacker_reward = 0
    honest_reward = 0

    for i in range(TRIALS):
        game.reset()
        
        while not game.is_completed:
            game.simulate()

        attacker_reward += game.rewards[Miner.ATTACKER]
        honest_reward += game.rewards[Miner.HONEST]

    return attacker_reward / (attacker_reward + honest_reward)

if __name__ == "__main__":

    strat = input("Select a strategy (SM / NSM): ")

    if strat == "SM":
        outfile = "results/sm.csv"
        attacker = SM()

    elif strat == "NSM":
        outfile = "results/nsm.csv"
        attacker = NSM()

    else:
        print(f"error: could not recognize strategy {strat}")
        exit()

    miners: dict[Miner, Strategy] = {
        Miner.ATTACKER: attacker,
        Miner.HONEST: Frontier(),
    }

    alphas = np.arange(LO, HI, STEP)

    datapoints = []

    for alpha in tqdm(alphas):
        datapoints.append((alpha, get_reward(miners, alpha)))

    with open(outfile, 'w') as f:
        csv.writer(f, delimiter=' ').writerows(datapoints)