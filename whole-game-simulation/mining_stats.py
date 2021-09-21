from mining_game import MiningGame

from honest_miner import HonestMiner
from nsm import NSM
from nsm_r1 import NSM_R1
from sm import SM

if __name__ == "__main__":

    alpha = 0.4
    max_steps = 10000000
    verbose = False

    miners = [
        "NSM",
        "NSM_R1",
        "SM"
    ]

    scores = [
        MiningGame([NSM(), HonestMiner()], alpha, max_steps, verbose).simulate(),
        MiningGame([NSM_R1(), HonestMiner()], alpha, max_steps, verbose).simulate(),
        MiningGame([SM(), HonestMiner()], alpha, max_steps, verbose).simulate(),
    ]

    for idx, score in enumerate(scores):
        print(miners[idx] + ":\t\t" + str(score))