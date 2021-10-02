from game import Game
from miner import Miner
from strategy import Strategy

# strategies
from frontier import Frontier
from sm import SM

if __name__ == "__main__":

    miners: dict[Miner, Strategy] = {
        Miner.ATTACKER: SM(),
        Miner.HONEST: Frontier(),
    }

    alpha = None

    game = Game(miners, alpha, stream=True)

    rewards = []

    while (input("Another round? y/[n] ") == "y"):
        game.reset()

        while not game.is_completed:
            print(game.simulate_step())
        
        rewards.append((game.rewards[Miner.ATTACKER], game.rewards[Miner.HONEST]))
        print((game.rewards[Miner.ATTACKER], game.rewards[Miner.HONEST]))

    revenue = sum([x for x,_ in rewards]) / sum([x + y for x,y in rewards])
    print(revenue)