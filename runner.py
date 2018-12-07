from adjudicator import Adjudicator
from agent import Agent
from agent_random import RandomAgent
import pickle
from pathlib import Path

FILE_NAME = "network.txt"
my_file = Path(FILE_NAME)
if my_file.exists():
    file = open(FILE_NAME, 'rb')
    trained_network = pickle.load(file)
else:
    trained_network = None

final_result = {}

for i in range(1000):
    agentOne = Agent(0, trained_network)
    agentTwo = Agent(1, trained_network)
    adjudicator = Adjudicator()
    result = adjudicator.runGame(agentOne, agentTwo)
    print(result)
    if final_result.get(result[0], None) == None:
        final_result[result[0]] = 0
    final_result[result[0]] += 1
    trained_network = agentTwo.network
pickle.dump(trained_network, open(FILE_NAME, 'wb'))
pickle.dump(trained_network, open(FILE_NAME, 'wb'))
