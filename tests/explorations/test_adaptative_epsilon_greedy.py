from blobrl.explorations import AdaptativeEpsilonGreedy


def test_adaptative_epsilon_greedy_step_min():
    exploration = AdaptativeEpsilonGreedy(0.8, 0.1, 0.99)

    exploration.be_greedy(0)


def test_adaptative_epsilon_greedy_step():
    exploration = AdaptativeEpsilonGreedy(0.8, 0.1, 0.99)

    exploration.be_greedy(5)


def test__str__():
    explo = AdaptativeEpsilonGreedy(0.8, 0.1, 0.99)

    assert 'AdaptativeEpsilonGreedy-' + str(explo.epsilon_max) + '-' + str(explo.epsilon_min) + '-' + str(
        explo.gamma) == explo.__str__()
