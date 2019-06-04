'''
Test the advanced schedulers.
'''
import numpy
from unittest import TestCase
from unittest.mock import patch, PropertyMock
from mesa import Model, Agent
from mesa.time import (BaseScheduler, StagedActivation, RandomActivation,
                       SimultaneousActivation)

RANDOM = 'random'
STAGED = 'staged'
SIMULTANEOUS = 'simultaneous'

class MockRandomState(numpy.random.RandomState):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shuffle_call_count = 0

    def shuffle(self, x):
        self.shuffle_call_count += 1

class MockAgent(Agent):
    '''
    Minimalistic agent for testing purposes.
    '''

    def stage_one(self):
        self.model.log.append(self.unique_id + "_1")

    def stage_two(self):
        self.model.log.append(self.unique_id + "_2")

    def advance(self):
        pass


class MockModel(Model):

    def __init__(self, shuffle=False, activation=STAGED):
        '''
        Creates a Model instance with a schedule

        Args:
            shuffle (Bool): whether or not to instantiate a scheduler
                            with shuffling.
                            This option is only used for
                            StagedActivation schedulers.

            activation (str): which kind of scheduler to use.
                              'random' creates a RandomActivation scheduler.
                              'staged' creates a StagedActivation scheduler.
                              The default scheduler is a BaseScheduler.
        '''
        super().__init__()

        self.random_state = MockRandomState()

        self.log = []

        # Make scheduler
        if activation == STAGED:
            model_stages = ["stage_one", "stage_two"]
            self.schedule = StagedActivation(self, stage_list=model_stages,
                                             shuffle=shuffle,
                                             random_state=self.random_state)
        elif activation == RANDOM:
            self.schedule = RandomActivation(self, random_state=self.random_state)
        elif activation == SIMULTANEOUS:
            self.schedule = SimultaneousActivation(self, random_state=self.random_state)
        else:
            self.schedule = BaseScheduler(self, random_state=self.random_state)

        # Make agents
        for name in ["A", "B"]:
            agent = MockAgent(name, self)
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()


class TestStagedActivation(TestCase):
    '''
    Test the staged activation.
    '''

    expected_output = ["A_1", "B_1", "A_2", "B_2"]

    def test_no_shuffle(self):
        '''
        Testing staged activation without shuffling.
        '''
        model = MockModel(shuffle=False)
        model.step()
        assert model.log == self.expected_output

    def test_shuffle(self):
        '''
        Test staged activation with shuffling
        '''
        model = MockModel(shuffle=True)
        model.step()
        for output in self.expected_output[:2]:
            assert output in model.log[:2]
        for output in self.expected_output[2:]:
            assert output in model.log[2:]

    def test_shuffle_shuffles_agents(self):
        model = MockModel(shuffle=True)
        assert model.random_state.shuffle_call_count == 0
        model.step()
        assert model.random_state.shuffle_call_count == 1

    def test_remove(self):
        '''
        Test staged activation can remove an agent
        '''
        model = MockModel(shuffle=True)
        agent = model.schedule.agents[0]
        model.schedule.remove(model.schedule.agents[0])
        assert agent not in model.schedule.agents


class TestRandomActivation(TestCase):
    '''
    Test the random activation.
    '''

    def test_random_activation_step_shuffles(self):
        '''
        Test the random activation step
        '''
        model = MockModel(activation=RANDOM)
        model.schedule.step()
        assert model.random_state.shuffle_call_count == 1

    def test_random_activation_step_increments_step_and_time_counts(self):
        '''
        Test the random activation step increments step and time counts
        '''
        model = MockModel(activation=RANDOM)
        assert model.schedule.steps == 0
        assert model.schedule.time == 0
        model.schedule.step()
        assert model.schedule.steps == 1
        assert model.schedule.time == 1

    def test_random_activation_step_steps_each_agent(self):
        '''
        Test the random activation step causes each agent to step
        '''

        with patch('test_time.MockAgent.step') as mock_agent_step:
            model = MockModel(activation=RANDOM)
            model.step()
            # one step for each of 2 agents
            assert mock_agent_step.call_count == 2


class TestSimultaneousActivation(TestCase):
    '''
    Test the simultaneous activation.
    '''

    def test_simultaneous_activation_step_steps_and_advances_each_agent(self):
        '''
        Test the simultaneous activation step causes each agent to step
        '''

        with patch('test_time.MockAgent.step') as mock_agent_step,\
                patch('test_time.MockAgent.advance') as mock_agent_advance:
            model = MockModel(activation=SIMULTANEOUS)
            model.step()
            # one step for each of 2 agents
            assert mock_agent_step.call_count == 2
            assert mock_agent_advance.call_count == 2
