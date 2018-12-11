from adjudicator import Adjudicator
from agent import Agent
from agent_random import RandomAgent
from agent_greedy import GreedyAgent
from agent_fixed_policy import Agent as Agent_FP
import pickle
from pathlib import Path

FILE_NAME = "network.txt"
my_file = Path(FILE_NAME)
if my_file.exists():
    file = open(FILE_NAME, 'rb')
    trained_network = pickle.load(file)
else:
    trained_network = None

#trained_network = None
final_result = {}

for i in range(100):
    # agentOne = RandomAgent(1)
    # agentOne = GreedyAgent(1)
    # agentOne = Agent_FP(1)
    # agentTwo = Agent(2, trained_network)

    agentOne = Agent(1, trained_network)
    # agentTwo = Agent_FP(2)
    agentTwo = RandomAgent(2)


    adjudicator = Adjudicator()
    result = adjudicator.runGame(agentOne, agentTwo)
    print(result)
    if final_result.get(result[0], None) == None:
        final_result[result[0]] = 0
    final_result[result[0]] += 1
    
    # trained_network = agentTwo.network

    trained_network = agentOne.network

    #pickle.dump(trained_network, open(FILE_NAME, 'wb'))

print(final_result)
pickle.dump(trained_network, open(FILE_NAME, 'wb'))