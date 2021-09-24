import csv
import numpy as np
from tqdm import tqdm

from game import Game
from miner import Miner
from strategy import Strategy

# strategies
from frontier import Frontier
from sm import SM

TRIALS = 100000

LO = 0.33
HI = 0.45
STEP = 0.005

if __name__ == "__main__":

    miners: dict[Miner, Strategy] = {
        Miner.ATTACKER: SM(),
        Miner.HONEST: Frontier(),
    }

    alphas = np.arange(LO, HI, STEP)

    datapoints = []

    for alpha in tqdm(alphas):
        game = Game(miners, alpha)
        rewards = []

        for i in tqdm(range(TRIALS)):
            game.reset()
            
            while not game.is_completed:
                game.simulate()

            rewards.append((game.rewards[Miner.ATTACKER], game.rewards[Miner.HONEST]))

        revenue = sum([x for x,_ in rewards]) / sum([x + y for x,y in rewards])
        datapoints.append((alpha, revenue))

    with open('out.csv', 'w') as f:
        csv.writer(f, delimiter=' ').writerows(datapoints)