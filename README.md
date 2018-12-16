# Monopoly


File Details

agent.py
1. This is our RL-agent file. We have used Q-learning as a way of doing Reinforcement Learning
    a. Implemented Q-Learning to learn the states
    b. Incorporated the usage of EligibilityTraces, which helps in keeping the history and also helps us increasing the number of state-transitions, which helps us in training the agent faster. 
    c. The usage of Eligibility Traces, helps us determine, which particular set of states have led to a particular good or bad state
    d. This also helps us use the properties of Monte Carlo method within Reinforcement Learning 
    e. We have calculated the reward based on the current state of the game. The same state will give different rewards to each player. This depends on the player’s relative position in the game. This is calculated in ‘calculateReward’     


network.py
1. This is the neural network that we have used, as a Q-Table
2. It is a 3-layer deep neural network, with the number of inputs same as the no. of nodes, in which we have divided the state into
3. This Neural Network, is used for Function Approximation which gives an appropriate action, on a given state based on the reward
4. Further, we have divided the action space into three buckets:
    Buying - code 1
    Selling - code -1
    Do nothing - code 0
5. Based on the action returned from the Neural Network, we choose to do the appropriate action on the current state. (Eg. if the action returned is 1: If we are on an unowned property, we choose to buy it, else if the property is owned, we choose to start building in the group.)
