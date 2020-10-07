from blobrl.agents import CategoricalDQN
from blobrl.networks import C51Network

from tests.agents import TestDQN

TestDQN.__test__ = False


class TestCategorical_dqn(TestDQN):
    __test__ = True

    agent = CategoricalDQN
    network = C51Network

    def test__str__(self):
        for o, a in self.list_work:
            agent = self.agent(o, a)

            assert 'CategoricalDQN-' + str(agent.observation_space) + "-" + str(agent.action_space) + "-" + str(
                agent.neural_network) + "-" + str(agent.memory) + "-" + str(agent.step_train) + "-" + str(
                agent.step) + "-" + str(agent.batch_size) + "-" + str(agent.gamma) + "-" + str(agent.loss) + "-" + str(
                agent.optimizer) + "-" + str(agent.greedy_exploration) + "-" + str(agent.num_atoms) + "-" + str(
                agent.r_min) + "-" + str(agent.r_max) + "-" + str(agent.delta_z) + "-" + str(agent.z) == agent.__str__()
