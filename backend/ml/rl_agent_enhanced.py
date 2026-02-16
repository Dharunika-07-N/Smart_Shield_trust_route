import numpy as np
import pandas as pd
import joblib
import logging
from typing import Dict, Tuple, List, Union
from collections import defaultdict, deque
from datetime import datetime
import json
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedSARSAAgent:
    """
    Advanced SARSA Agent for Adaptive Route Learning
    
    Improvements:
    - Experience replay
    - Epsilon-greedy with decay
    - Learning rate scheduling
    - Reward normalization
    - State aggregation for continuous values
    - Performance tracking
    """
    
    def __init__(
        self,
        model_path: str = None,
        alpha: float = 0.1,  # Learning rate
        gamma: float = 0.95,  # Discount factor
        epsilon: float = 0.3,  # Exploration rate
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995
    ):
        if model_path is None:
             self.model_path = os.path.join(Path(__file__).parent.parent, "models") + os.sep
        else:
             self.model_path = model_path
             
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path, exist_ok=True)

        self.alpha = alpha
        self.alpha_min = 0.001
        self.alpha_decay = 0.9995
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Q-table: state -> action -> Q-value
        # Using vanilla dict for serialization safety, initialized with 0
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Experience replay buffer
        self.replay_buffer = deque(maxlen=10000)
        
        # State discretization bins
        self.location_bins = 20
        self.time_bins = 24  # hours
        self.traffic_bins = 10
        self.weather_bins = 5
        
        # Actions (route choices)
        self.actions = ['fastest', 'safest', 'balanced', 'shortest']
        
        # Reward weights
        self.reward_weights = {
            'time_efficiency': 0.25,
            'safety': 0.40,
            'success': 0.30,
            'distance': 0.05
        }
        
        # Performance tracking
        self.episode_rewards = []
        self.episode_metrics = []
        self.training_history = []
        
    def discretize_state(self, state: Dict) -> Tuple:
        """
        Convert continuous state to discrete representation
        """
        # Location discretization (grid-based)
        lat = int(state.get('latitude', 0) * 100) % self.location_bins
        lon = int(state.get('longitude', 0) * 100) % self.location_bins
        
        # Time discretization
        hour = state.get('hour', 12)
        time_bucket = hour  # Already discrete (0-23)
        
        # Traffic discretization
        traffic = state.get('traffic_level', 0.5)
        traffic_bucket = int(traffic * self.traffic_bins)
        
        # Weather discretization
        weather_map = {
            'clear': 0, 'cloudy': 1, 'rain': 2, 
            'heavy_rain': 3, 'storm': 4, 'snow': 5
        }
        weather = weather_map.get(state.get('weather', 'clear'), 0)
        
        # Destination (simplified - use quadrant)
        dest_lat = int(state.get('dest_latitude', 0) * 100) % 4
        dest_lon = int(state.get('dest_longitude', 0) * 100) % 4
        
        # Is weekend
        is_weekend = int(state.get('is_weekend', False))
        
        return str((lat, lon, time_bucket, traffic_bucket, 
                weather, dest_lat, dest_lon, is_weekend)) # Return as string for JSON serialization
    
    def choose_action(self, state: str, explore: bool = True) -> str:
        """
        Epsilon-greedy action selection
        
        Args:
            state: Discretized state tuple (stringified)
            explore: Whether to use epsilon-greedy (False for deployment)
        """
        if explore and np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.choice(self.actions)
        else:
            # Exploit: best action
            q_values = self.q_table[state]
            
            if not q_values:
                # If state not seen, random action
                return np.random.choice(self.actions)
            
            # Choose action with highest Q-value
            # Handle empty q_values just in case
            if len(q_values) == 0:
                 return np.random.choice(self.actions)
                 
            best_action = max(q_values.items(), key=lambda x: x[1])[0]
            return best_action
    
    def calculate_reward(self, outcome: Dict) -> float:
        """
        Calculate reward from delivery outcome
        """
        # Time efficiency (negative reward for delays)
        actual_time = outcome.get('actual_time', 60) or 60
        estimated_time = outcome.get('estimated_time', 60) or 60
        time_ratio = actual_time / estimated_time
        time_reward = 1.0 - min(time_ratio - 1.0, 1.0)  # Penalty for delays
        time_reward = max(time_reward, -1.0)  # Clip at -1
        
        # Safety score (normalized to 0-1)
        safety_reward = outcome.get('safety_score', 50) / 100.0
        
        # Success reward
        success_reward = 1.0 if outcome.get('success', False) else -1.0
        
        # Distance efficiency
        actual_dist = outcome.get('actual_distance', 10) or 10
        est_dist = outcome.get('estimated_distance', 10) or 10
        distance_ratio = actual_dist / est_dist
        distance_reward = 1.0 - min(distance_ratio - 1.0, 1.0)
        distance_reward = max(distance_reward, -1.0)
        
        # Weighted total reward
        total_reward = (
            self.reward_weights['time_efficiency'] * time_reward +
            self.reward_weights['safety'] * safety_reward +
            self.reward_weights['success'] * success_reward +
            self.reward_weights['distance'] * distance_reward
        )
        
        return total_reward
    
    def update_q_value(
        self,
        state: str,
        action: str,
        reward: float,
        next_state: str,
        next_action: str
    ):
        """
        SARSA update rule
        """
        current_q = self.q_table[state][action]
        next_q = self.q_table[next_state][next_action]
        
        # SARSA update
        new_q = current_q + self.alpha * (reward + self.gamma * next_q - current_q)
        
        self.q_table[state][action] = new_q
    
    def train_episode(self, experiences: List[Dict]) -> Dict:
        """
        Train on a single episode
        """
        episode_reward = 0
        transitions = []
        
        # Loop through all experiences
        for i, exp in enumerate(experiences):
            # Discretize states
            state = self.discretize_state(exp['state'])
            next_state = self.discretize_state(exp['next_state'])
            
            action = exp['action']
            reward = exp['reward']
            
            # Get next action for SARSA
            if i + 1 < len(experiences):
                next_action = experiences[i + 1]['action']
            else:
                # Terminal state approximation
                next_action = action # assume same policy or use choose_action
            
            # Update Q-value
            self.update_q_value(state, action, reward, next_state, next_action)
            
            episode_reward += reward
            transitions.append((state, action, reward, next_state, next_action))
            
            # Store in replay buffer
            self.replay_buffer.append(transitions[-1])
        
        # Decay exploration and learning rate
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.alpha = max(self.alpha_min, self.alpha * self.alpha_decay)
        
        self.episode_rewards.append(episode_reward)
        
        metrics = {
            'episode_reward': float(episode_reward),
            'epsilon': float(self.epsilon),
            'alpha': float(self.alpha),
            'q_table_size': len(self.q_table),
            'avg_reward_last_100': float(np.mean(self.episode_rewards[-100:])) if len(self.episode_rewards) >= 100 else float(episode_reward)
        }
        
        self.episode_metrics.append(metrics)
        
        return metrics
    
    def experience_replay(self, batch_size: int = 32):
        """
        Train on random samples from experience replay buffer
        """
        if len(self.replay_buffer) < batch_size:
            return
        
        # Sample random batch
        indices = np.random.choice(len(self.replay_buffer), batch_size, replace=False)
        batch = [self.replay_buffer[i] for i in indices]
        
        for state, action, reward, next_state, next_action in batch:
            self.update_q_value(state, action, reward, next_state, next_action)
    
    def train_from_history(self, delivery_history: pd.DataFrame) -> Dict:
        """
        Train from historical delivery data
        """
        logger.info(f"Training on {len(delivery_history)} historical deliveries...")
        
        # Group by delivery_id to create episodes
        episodes = []
        
        # delivery_history might be empty
        if delivery_history.empty:
             return {'status': 'No data'}
             
        for delivery_id, group in delivery_history.groupby('delivery_id'):
            experiences = []
            
            for idx, row in group.iterrows():
                state = {
                    'latitude': row['start_latitude'],
                    'longitude': row['start_longitude'],
                    'dest_latitude': row['end_latitude'],
                    'dest_longitude': row['end_longitude'],
                    'hour': pd.to_datetime(row['timestamp']).hour,
                    'is_weekend': pd.to_datetime(row['timestamp']).dayofweek >= 5,
                    'traffic_level': row.get('traffic_level', 0.5),
                    'weather': row.get('weather', 'clear')
                }
                
                action = row['route_choice']
                
                outcome = {
                    'actual_time': row['actual_time'],
                    'estimated_time': row['estimated_time'],
                    'safety_score': row.get('safety_score', 75),
                    'success': row.get('success', True),
                    'actual_distance': row.get('actual_distance', row.get('estimated_distance')),
                    'estimated_distance': row.get('estimated_distance')
                }
                
                reward = self.calculate_reward(outcome)
                
                experiences.append({
                    'state': state,
                    'action': action,
                    'reward': reward,
                    'next_state': state,  # Simplified, in reality would be distinct
                    'done': True
                })
            
            episodes.append(experiences)
        
        # Train on episodes
        total_metrics = []
        for episode in episodes:
            if len(episode) > 0:
                metrics = self.train_episode(episode)
                total_metrics.append(metrics)
        
        # Additional experience replay
        for _ in range(10):
            self.experience_replay(batch_size=32)
        
        if not total_metrics:
              return {'status': 'No valid episodes'}

        # Aggregate metrics
        final_metrics = {
            'num_episodes': len(episodes),
            'total_transitions': sum(len(ep) for ep in episodes),
            'avg_episode_reward': float(np.mean([m['episode_reward'] for m in total_metrics])),
            'final_epsilon': float(self.epsilon),
            'final_alpha': float(self.alpha),
            'q_table_size': len(self.q_table),
            'timestamp': datetime.now().isoformat()
        }
        
        self.training_history.append(final_metrics)
        
        logger.info(f"Training complete. Avg reward: {final_metrics['avg_episode_reward']:.3f}")
        
        return final_metrics
    
    def recommend_route(self, state: Dict) -> Tuple[str, Dict]:
        """
        Recommend best route for deployment
        """
        discrete_state = self.discretize_state(state)
        action = self.choose_action(discrete_state, explore=False)
        
        q_values = dict(self.q_table[discrete_state])
        
        # If no Q-values, return default
        if not q_values:
            q_values = {a: 0.0 for a in self.actions}
            action = 'balanced'  # Default
        
        return action, q_values
    
    def get_performance_summary(self) -> Dict:
        """Get training performance summary"""
        if not self.episode_rewards:
            return {'status': 'No training data'}
        
        recent_rewards = self.episode_rewards[-100:]
        
        return {
            'total_episodes': len(self.episode_rewards),
            'avg_reward': float(np.mean(self.episode_rewards)),
            'recent_avg_reward': float(np.mean(recent_rewards)),
            'best_reward': float(max(self.episode_rewards)),
            'worst_reward': float(min(self.episode_rewards)),
            'current_epsilon': float(self.epsilon),
            'current_alpha': float(self.alpha),
            'q_table_size': len(self.q_table),
            'replay_buffer_size': len(self.replay_buffer)
        }
    
    def save_model(self, version: str = None):
        """Save agent with versioning"""
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_data = {
            'q_table': dict(self.q_table),
            'epsilon': self.epsilon,
            'alpha': self.alpha,
            'gamma': self.gamma,
            'reward_weights': self.reward_weights,
            'episode_rewards': self.episode_rewards,
            'training_history': self.training_history,
            'version': version
        }
        
        model_file = f"{self.model_path}sarsa_agent_v{version}.pkl"
        joblib.dump(model_data, model_file)
        
        logger.info(f"Agent saved: {model_file}")
        return model_file
    
    def load_model(self, version: str = 'latest'):
        """Load agent"""
        import glob
        
        if version == 'latest':
            model_files = glob.glob(f"{self.model_path}sarsa_agent_v*.pkl")
            if not model_files:
                logger.warning("No agent files found")
                return False
            model_file = max(model_files)
        else:
            model_file = f"{self.model_path}sarsa_agent_v{version}.pkl"
            if not os.path.exists(model_file):
                return False
        
        model_data = joblib.load(model_file)
        
        # Convert back to defaultdict
        self.q_table = defaultdict(lambda: defaultdict(float))
        for state, actions in model_data['q_table'].items():
            for action, value in actions.items():
                self.q_table[state][action] = value
        
        self.epsilon = model_data['epsilon']
        self.alpha = model_data['alpha']
        self.gamma = model_data['gamma']
        self.reward_weights = model_data.get('reward_weights', self.reward_weights)
        self.episode_rewards = model_data.get('episode_rewards', [])
        self.training_history = model_data.get('training_history', [])
        
        logger.info(f"Agent loaded: {model_file}")
        return True
