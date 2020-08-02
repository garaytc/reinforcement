import os
import pickle
from copy import deepcopy

import torch
import torch.nn.functional as F
import torch.optim as optim
from gym.spaces import flatdim

from torchforce.agents import DQN
from torchforce.memories import ExperienceReplay


class DoubleDQN(DQN):
    """ from 'Deep Reinforcement Learning with Double Q-learning' in https://arxiv.org/pdf/1509.06461.pdf """

    def __init__(self, action_space, observation_space, memory=ExperienceReplay(), neural_network=None, step_copy=500,
                 step_train=2, batch_size=32, gamma=0.99, loss=None, optimizer=None, greedy_exploration=None,
                 device=None):
        """

        :param device: torch device to run agent
        :type: torch.device
        :param action_space:
        :param observation_space:
        :param memory:
        :param neural_network:
        :param step_copy:
        :param step_train:
        :param batch_size:
        :param gamma:
        :param loss:
        :param optimizer:
        :param greedy_exploration:
        """
        super().__init__(action_space, observation_space, memory, neural_network, step_train, batch_size, gamma, loss,
                         optimizer, greedy_exploration, device=device)

        self.neural_network_target = deepcopy(self.neural_network)
        self.copy_online_to_target()
        self.step_copy = step_copy

        if optimizer is None:
            self.optimizer = optim.Adam(self.neural_network.parameters())

    def learn(self, observation, action, reward, next_observation, done) -> None:
        """ learn from parameters

        :param observation: stat of environment
        :type observation: gym.Space
        :param action: action taken by agent
        :type action: int, float, list
        :param reward: reward win
        :type reward: int, float, np.int, np.float
        :type reward: int, np.int
        :param next_observation:
        :type next_observation: gym.Space
        :param done: if env is finished
        :type done: bool
        """
        super().learn(observation, action, reward, next_observation, done)

        if (self.step % self.step_copy) == 0:
            self.copy_online_to_target()

    def train(self):
        """

        """
        observations, actions, rewards, next_observations, dones = self.memory.sample(self.batch_size)

        actions_next = torch.argmax(self.neural_network.forward(next_observations).detach(), dim=1)
        actions_next_one_hot = F.one_hot(actions_next.to(torch.int64), num_classes=self.action_space.n)
        q_next = self.neural_network_target.forward(next_observations).detach() * actions_next_one_hot

        q = rewards + self.gamma * torch.max(q_next, dim=1)[0] * (1 - dones)

        actions_one_hot = F.one_hot(actions.to(torch.int64), num_classes=self.action_space.n)
        q_predict = torch.max(self.neural_network.forward(observations) * actions_one_hot, dim=1)[0]

        self.optimizer.zero_grad()
        loss = self.loss(q_predict, q)
        loss.backward()
        self.optimizer.step()

    def copy_online_to_target(self):
        """

        """
        self.neural_network_target.load_state_dict(self.neural_network.state_dict())

    def save(self, file_name, dire_name="."):
        """ Save agent at dire_name/file_name

        :param file_name: name of file for save
        :type file_name: string
        :param dire_name: name of directory where we would save it
        :type file_name: string
        """
        os.makedirs(os.path.abspath(dire_name), exist_ok=True)

        dict_save = dict()
        dict_save["observation_space"] = pickle.dumps(self.observation_space)
        dict_save["action_space"] = pickle.dumps(self.action_space)
        dict_save["neural_network_class"] = pickle.dumps(type(self.neural_network))
        dict_save["neural_network"] = self.neural_network.state_dict()
        dict_save["step_train"] = pickle.dumps(self.step_train)
        dict_save["batch_size"] = pickle.dumps(self.batch_size)
        dict_save["gamma"] = pickle.dumps(self.gamma)
        dict_save["loss"] = pickle.dumps(self.loss)
        dict_save["optimizer"] = pickle.dumps(self.optimizer)
        dict_save["greedy_exploration"] = pickle.dumps(self.greedy_exploration)
        dict_save["step_copy"] = pickle.dumps(self.step_copy)

        torch.save(dict_save, os.path.abspath(os.path.join(dire_name, file_name)))

    @classmethod
    def load(cls, file_name, dire_name=".", device=None):
        """ load agent form dire_name/file_name

        :param device: torch device to run agent
        :type: torch.device
        :param file_name: name of file for load
        :type file_name: string
        :param dire_name: name of directory where we would load it
        :type file_name: string
        """
        dict_save = torch.load(os.path.abspath(os.path.join(dire_name, file_name)))

        neural_network = pickle.loads(dict_save["neural_network_class"])(
            observation_shape=flatdim(pickle.loads(dict_save["observation_space"])),
            action_shape=flatdim(pickle.loads(dict_save["action_space"])))
        neural_network.load_state_dict(dict_save["neural_network"])

        double_dqn = DoubleDQN(observation_space=pickle.loads(dict_save["observation_space"]),
                               action_space=pickle.loads(dict_save["action_space"]),
                               neural_network=neural_network,
                               step_train=pickle.loads(dict_save["step_train"]),
                               batch_size=pickle.loads(dict_save["batch_size"]),
                               gamma=pickle.loads(dict_save["gamma"]),
                               loss=pickle.loads(dict_save["loss"]),
                               optimizer=pickle.loads(dict_save["optimizer"]),
                               greedy_exploration=pickle.loads(dict_save["greedy_exploration"]))

        double_dqn.step_copy = pickle.loads(dict_save["step_copy"])

        return double_dqn

    def __str__(self):
        return 'DoubleDQN-' + str(self.observation_space) + "-" + str(self.action_space) + "-" + str(
            self.neural_network) + "-" + str(self.memory) + "-" + str(self.step_train) + "-" + str(
            self.step) + "-" + str(self.batch_size) + "-" + str(self.gamma) + "-" + str(self.loss) + "-" + str(
            self.optimizer) + "-" + str(self.greedy_exploration) + "-" + str(self.step_copy)
