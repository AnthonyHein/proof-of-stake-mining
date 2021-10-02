import time
from tqdm import tqdm

from game import Game
from miner import Miner
from strategy import Strategy

# strategies
from frontier import Frontier
from sm import SM

TRIALS = 10000

EPS = 1e-8

MOMENTUM_THRESH = 2

MINERS: dict[Miner, Strategy] = {
    Miner.ATTACKER: SM(),
    Miner.HONEST: Frontier(),
}

def get_reward(alpha: float) -> float:

    game = Game(MINERS, alpha)

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

    hi = 0.5
    lo = 0.307
    mid = (hi + lo) / 2

    momentum_higher = 0
    momentum_lower = 0

    start_time = time.time()
 
    while lo + EPS <= hi: 
        mid = (hi + lo) / 2
 
        reward = get_reward(mid)

        print(f"lo: {lo: 10f} mid: {mid: 10f} hi: {hi: 10f} reward: {reward: 10f}")

        if reward - mid > EPS:
            hi = (hi + mid) / 2
            momentum_higher += 1
            momentum_lower = 0
 
        elif reward - mid < -EPS:
            lo = (mid + lo) / 2
            momentum_lower += 1
            momentum_higher = 0
 
        else:
            break

        # might have accidentally excluded the correct value
        # so if we see it constantly moving in one direction
        # then add a bit
        if momentum_higher >= MOMENTUM_THRESH:
            momentum_higher = 0
            lo = max(lo - (hi - lo), 0.307)
        
        elif momentum_lower >= MOMENTUM_THRESH:
            momentum_lower = 0
            hi = min(hi + (hi - lo), 0.5)


    print(mid)

    print("--- %s seconds ---" % (time.time() - start_time))