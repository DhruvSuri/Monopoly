# Monopoly


## Adjudicator Details

Implementation of the classic Monopoly game and its Machine Learning based playing agent

Note: This project is under active development from scratch.

### Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

This is a console based game. Currently, it only supports bot vs bot but it's extensible.

#### Prerequisites

What things you need to install the software and how to install them

* python3
* numpy

### Playing game
To start playing the game download the code and run "rungame.py"
```
chmod +x rungame.py
./rungame.py
```

1. Game.py is the main file where core adjudicator code lies.
2. Board and card configurations are in BoardConfig.json, ChanceCards.json and CommunityCards.json
3. Code is written in form of handlers. Each board cell has an handler based on it's type. Similarly, for cards.


### Test cases

#### Running
For running automated tests run "TestCases.py"
```
chmod +x TestCases.py
./TestCases.py
```
Tests to be run are in "tests" list

#### Adding new test case
* Follow the existing test cases format to add new test case. 
* For running the test case just add it in "tests" list

### Acknowledgments
* Referred Team-007 code for ChanceCards and CommunityChestCards config


## Agent Details

File Details

agent.py
1. This is our RL-agent file. We have used Q-learning as a way of doing Reinforcement Learning
    a. Implemented Q-Learning to learn the states
    b. Incorporated the usage of EligibilityTraces, which helps in keeping the history and also helps us increasing the number of state-transitions, which helps us in training the agent faster. 
    c. The usage of Eligibility Traces, helps us determine, which particular set of states have led to a particular good or bad state
    d. This also helps us use the properties of Monte Carlo method within Reinforcement Learning 
    e. We have calculated the reward based on the current state of the game. The same state will give different rewards to each player. This depends on the player’s relative position in the game. This is calculated in ‘calculateReward’     

agent_fixed_policy.py
1. This is our Fixed Policy agent file. We have used heuristics here to play the game.
	a. Stalling technique to come out of jail when significant number of iterations passed.
	b. Added very little randomization to model different types of agent.


network.py
1. This is the neural network that we have used, as a Q-Table
2. It is a 3-layer deep neural network, with the number of inputs same as the no. of nodes, in which we have divided the state into
3. This Neural Network, is used for Function Approximation which gives an appropriate action, on a given state based on the reward
4. Further, we have divided the action space into three buckets:
    Buying - code 1
    Selling - code -1
    Do nothing - code 0
5. Based on the action returned from the Neural Network, we choose to do the appropriate action on the current state. (Eg. if the action returned is 1: If we are on an unowned property, we choose to buy it, else if the property is owned, we choose to start building in the group.)


## Authors
* Dhruv
* [Nikhil](https://github.com/nikhilsid)
* [Udbhav](https://github.com/udbhav-sharma)
