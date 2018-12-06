import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torch.utils.data import DataLoader,sampler,Dataset
#import torchvision.datasets as dset
#import torchvision.transforms as T
import timeit
from PIL import Image
import os
import numpy as np
import scipy.io

class Network:
    def __init__(self):
        self.input_count = 23
        self.hidden_layer_count = 150
        self.output_layer_count = 1
        self.learning_rate = 0.2
        self.epsilon = 0.5 #prevent overfitting
        self.alpha = 0.2 #
        self.currentEpoch = 1
        self.gamma = 0.95
        self.lamda = 0.8
        self.model = self.model = nn.Sequential(
            nn.Linear(self.input_count+1, self.hidden_layer_count),
            nn.Sigmoid(),
            nn.Linear(self.hidden_layer_count, 1)
        )
        self.dtype = torch.FloatTensor #CPU type
        self.model.type(self.dtype)
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=self.learning_rate)

    def train(self, inp, Y): #inp is a 24 element tensor
        for epoch in range(1):
            # Forward Propagation
            Y_pred = self.model(inp)
            #print (Y_pred.item())

            Y = torch.tensor(Y).float()
            # Compute and print loss
            loss = self.criterion(Y_pred, Y)
            #print('epoch: ', epoch,' loss: ', loss.item())
            # Zero the gradients
            self.optimizer.zero_grad()
    
            # perform a backward pass (backpropagation)
            loss.backward()
    
            # Update the parameters
            self.optimizer.step()


    def getTensor (self, input_state):
        input_ar = np.asarray(input_state)
        input_tensor = torch.from_numpy(input_ar).float()
        return input_tensor
    
    def run(self, input_state):
        y_pred = self.model(input_state)
        return y_pred.item()



        