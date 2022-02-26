from tqdm import tqdm

from game import Game
from miner import Miner
from strategy import Strategy

# strategies
from frontier import Frontier
from sm import SM

TRIALS = 100000

ALPHA = 1/3

if __name__ == "__main__":

    miners: dict[Miner, Strategy] = {
        Miner.ATTACKER: SM(),
        Miner.HONEST: Frontier(),
    }

    game = Game(miners, ALPHA)

    rewards = []

    for i in tqdm(range(TRIALS)):

        game.reset()
        
        while not game.is_completed:
            game.simulate()

        rewards.append((game.rewards[Miner.ATTACKER], game.rewards[Miner.HONEST]))

    revenue = sum([x for x,_ in rewards]) / sum([x + y for x,y in rewards])

    print(revenue)