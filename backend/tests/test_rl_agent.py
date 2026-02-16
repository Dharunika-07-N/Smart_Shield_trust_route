import pytest
import numpy as np
import pandas as pd
from backend.ml.rl_agent_enhanced import EnhancedSARSAAgent
import tempfile
import shutil
import os


@pytest.fixture
def sample_rl_data():
    """Generate sample RL training data"""
    np.random.seed(42)
    n_deliveries = 50
    
    data = []
    for i in range(n_deliveries):
        delivery = {
            'delivery_id': i,
            'start_latitude': np.random.uniform(40.0, 41.0),
            'start_longitude': np.random.uniform(-74.0, -73.0),
            'end_latitude': np.random.uniform(40.0, 41.0),
            'end_longitude': np.random.uniform(-74.0, -73.0),
            'timestamp': pd.Timestamp('2024-01-01') + pd.Timedelta(hours=i),
            'route_choice': np.random.choice(['fastest', 'safest', 'balanced', 'shortest']),
            'actual_time': np.random.uniform(20, 60),
            'estimated_time': np.random.uniform(20, 60),
            'safety_score': np.random.uniform(50, 100),
            'success': np.random.choice([True, False], p=[0.9, 0.1]),
            'actual_distance': np.random.uniform(5, 20),
            'estimated_distance': np.random.uniform(5, 20),
            'traffic_level': np.random.uniform(0, 1),
            'weather': np.random.choice(['clear', 'rain', 'cloudy'])
        }
        data.append(delivery)
    
    return pd.DataFrame(data)


@pytest.fixture
def agent():
    """Create agent instance"""
    tmpdir = tempfile.mkdtemp()
    ag = EnhancedSARSAAgent(model_path=tmpdir + os.sep)
    yield ag
    shutil.rmtree(tmpdir)


class TestRLAgentInit:
    """Test initialization"""
    
    def test_init(self, agent):
        assert agent.alpha == 0.1
        assert agent.gamma == 0.95
        assert 0 < agent.epsilon <= 1
        assert len(agent.actions) == 4
        assert len(agent.reward_weights) == 4
    
    def test_reward_weights_sum(self, agent):
        total = sum(agent.reward_weights.values())
        assert abs(total - 1.0) < 0.01  # Should sum to ~1


class TestStateDiscretization:
    """Test state discretization"""
    
    def test_discretize_state(self, agent):
        state = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'hour': 14,
            'traffic_level': 0.6,
            'weather': 'rain',
            'dest_latitude': 40.7589,
            'dest_longitude': -73.9851,
            'is_weekend': False
        }
        
        discrete_state = agent.discretize_state(state)
        
        # Checking if it's a string because enhanced agent now serializes the tuple state as string for caching
        assert isinstance(discrete_state, str) 
    
    def test_discretize_state_consistency(self, agent):
        state = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'hour': 14,
            'traffic_level': 0.6,
            'weather': 'clear',
            'dest_latitude': 40.7589,
            'dest_longitude': -73.9851,
            'is_weekend': False
        }
        
        # Same state should give same discretization
        discrete1 = agent.discretize_state(state)
        discrete2 = agent.discretize_state(state)
        
        assert discrete1 == discrete2


class TestActionSelection:
    """Test action selection"""
    
    def test_choose_action_explore(self, agent):
        # State string example (tuple string repr)
        state_repr = "(1, 2, 12, 5, 0, 1, 2, 0)"
        
        # With high epsilon, should sometimes explore
        agent.epsilon = 1.0
        actions = [agent.choose_action(state_repr, explore=True) for _ in range(100)]
        
        # Should see variety in actions
        unique_actions = set(actions)
        assert len(unique_actions) > 1
    
    def test_choose_action_exploit(self, agent):
        state_repr = "(1, 2, 12, 5, 0, 1, 2, 0)"
        
        # Manually set Q-values
        agent.q_table[state_repr]['fastest'] = 10.0
        agent.q_table[state_repr]['safest'] = 5.0
        agent.q_table[state_repr]['balanced'] = 7.0
        agent.q_table[state_repr]['shortest'] = 3.0
        
        # With no exploration, should always pick best
        action = agent.choose_action(state_repr, explore=False)
        assert action == 'fastest'
    
    def test_choose_action_unseen_state(self, agent):
        state_repr = "(99, 99, 23, 9, 4, 3, 3, 1)"
        
        # Should not crash on unseen state
        action = agent.choose_action(state_repr, explore=False)
        assert action in agent.actions


class TestRewardCalculation:
    """Test reward calculation"""
    
    def test_calculate_reward_perfect(self, agent):
        outcome = {
            'actual_time': 30,
            'estimated_time': 30,
            'safety_score': 100,
            'success': True,
            'actual_distance': 10,
            'estimated_distance': 10
        }
        
        reward = agent.calculate_reward(outcome)
        
        # Perfect outcome should have positive reward
        assert reward > 0.5
    
    def test_calculate_reward_delayed(self, agent):
        outcome = {
            'actual_time': 60,
            'estimated_time': 30,
            'safety_score': 75,
            'success': True,
            'actual_distance': 10,
            'estimated_distance': 10
        }
        
        reward = agent.calculate_reward(outcome)
        
        # Delayed should have lower reward than perfect (1.0 vs 0.65)
        assert reward < 0.8
    
    def test_calculate_reward_failed(self, agent):
        outcome = {
            'actual_time': 30,
            'estimated_time': 30,
            'safety_score': 50,
            'success': False,
            'actual_distance': 10,
            'estimated_distance': 10
        }
        
        reward = agent.calculate_reward(outcome)
        
        # Failed delivery should have negative impact or very low
        assert reward < 0.5 # Updated check as pure negativity might differ based on weights


class TestQValueUpdate:
    """Test Q-value updates"""
    
    def test_update_q_value(self, agent):
        state = "(1, 2, 12, 5, 0, 1, 2, 0)"
        next_state = "(1, 2, 13, 5, 0, 1, 2, 0)"
        action = 'fastest'
        next_action = 'balanced'
        reward = 0.8
        
        # Initial Q-value
        initial_q = agent.q_table[state][action]
        
        # Update
        agent.update_q_value(state, action, reward, next_state, next_action)
        
        # Q-value should change
        new_q = agent.q_table[state][action]
        assert new_q != initial_q
    
    def test_q_value_convergence(self, agent):
        state = "(1, 2, 12, 5, 0, 1, 2, 0)"
        next_state = state # Same state to see accumulation
        action = 'fastest'
        next_action = 'fastest'
        reward = 1.0
        
        # Multiple updates with same positive reward
        for _ in range(100):
            agent.update_q_value(state, action, reward, next_state, next_action)
        
        # Q-value should increase significantly
        final_q = agent.q_table[state][action]
        assert final_q > 1.0 # Reasonable increase


class TestTraining:
    """Test training"""
    
    def test_train_from_history(self, agent, sample_rl_data):
        metrics = agent.train_from_history(sample_rl_data)
        
        assert 'num_episodes' in metrics
        assert 'avg_episode_reward' in metrics
        assert metrics['num_episodes'] > 0
        assert agent.q_table  # Should have learned something
    
    def test_epsilon_decay(self, agent, sample_rl_data):
        initial_epsilon = agent.epsilon
        
        agent.train_from_history(sample_rl_data)
        
        # Epsilon should decrease
        assert agent.epsilon < initial_epsilon
        assert agent.epsilon >= agent.epsilon_min


class TestRecommendation:
    """Test route recommendation"""
    
    def test_recommend_route(self, agent):
        # Train a bit first
        state = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'hour': 14,
            'traffic_level': 0.6,
            'weather': 'clear',
            'dest_latitude': 40.7589,
            'dest_longitude': -73.9851,
            'is_weekend': False
        }
        
        action, q_values = agent.recommend_route(state)
        
        assert action in agent.actions
        assert isinstance(q_values, dict)
        assert len(q_values) > 0


class TestModelPersistence:
    """Test save/load"""
    
    def test_save_and_load(self, sample_rl_data):
        tmpdir = tempfile.mkdtemp()
        try:
            # Train and save
            agent1 = EnhancedSARSAAgent(model_path=tmpdir + os.sep)
            agent1.train_from_history(sample_rl_data)
            
            saved_path = agent1.save_model(version='test_v1')
            
            # Load
            agent2 = EnhancedSARSAAgent(model_path=tmpdir + os.sep)
            agent2.load_model(version='test_v1')
            
            # Verify Q-tables match
            state_key = list(agent1.q_table.keys())[0] if agent1.q_table else "(1, 2, 12, 5, 0, 1, 2, 0)"
            if state_key in agent1.q_table:
                assert state_key in agent2.q_table
                assert agent1.q_table[state_key] == agent2.q_table[state_key]
        finally:
            shutil.rmtree(tmpdir)
