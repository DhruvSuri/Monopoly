from adjudicator import Adjudicator
from adjudicator_fix import Adjudicator as AdjudicatorFix
from agent import Agent as RLAgent
from agent_random import RandomAgent
from agent_fixed_policy import Agent as FixedPolicyAgent
import pickle
from pathlib import Path
import numpy as np

def getOpponentRandomly(id):
    opponents = [RandomAgent(id), FixedPolicyAgent(id)]
    adjudicators = [AdjudicatorFix(), Adjudicator()]
    
    idx = np.random.randint(len(opponents))

    # print("Opponent Returned: %d" %(idx+1))
    return opponents[idx], adjudicators[idx]

def getAgentsAndAdjudicator():
    agents = [None, None]
    
    idx = np.random.randint(2)
    
    agents[idx] = RLAgent(idx+1, None)
    agents[1-idx], adjudicator = getOpponentRandomly(2-idx)

    # print("RL Agent: (%d, %d) Opponent: (%d, %d)" %(idx, idx+1, 1-idx, 2-idx))
    return agents, adjudicator, idx+1

def train(epochs):

    rlId = -1
    winCount = 0
    for i in range(epochs):
        print("Running epoch: %d" %(i))

        agents, adjudicator, rlId = getAgentsAndAdjudicator()

        result = adjudicator.runGame(agents[0], agents[1])

        if result[0] == rlId:
            winCount += 1

    print("RL Agent win count: %d in %d games" %(winCount, epochs))

    if rlId == -1:
        return None
        
    return agents[rlId-1].network

def saveTrainedNetwork(fileName, trained_network):
    pickle.dump(trained_network, open(fileName, 'wb'))

def loadTrainedNetwork(fileName):
    filePath = Path(fileName)
    if filePath.exists():
        file = open(fileName, 'rb')
        return pickle.load(file)
        
    return None

def main(epochs, fileName, doTrain, doSaveNetwork):

    if doTrain:
        trained_network = train(epochs)

        if doSaveNetwork:
            saveTrainedNetwork(fileName, trained_network)
    else:
        trained_network = loadTrainedNetwork(fileName)

if __name__ == '__main__':
    main(2000, 'network.txt', True, True)