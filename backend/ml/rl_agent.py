import numpy as np
from collections import defaultdict
import pickle
import os
from pathlib import Path

class SARSARouteAgent:
    """
    SARSA (State-Action-Reward-State-Action) agent for adaptive route learning
    """
    def __init__(self, alpha=0.1, gamma=0.95, epsilon=0.1):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.model_dir = os.path.join(Path(__file__).parent.parent, "models")
        self.model_path = os.path.join(self.model_dir, "sarsa_q_table.pkl")
        
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)

    def get_state(self, route_context):
        """
        Convert route context to discrete state
        """
        location_bucket = self._discretize_location(
            route_context.get('current_lat', 0),
            route_context.get('current_lng', 0)
        )
        
        time_bucket = self._discretize_time(route_context.get('hour', 12))
        traffic_bucket = self._discretize_traffic(route_context.get('traffic_level', 0.5))
        weather_bucket = self._discretize_weather(route_context.get('weather_condition', 'clear'))
        
        return (location_bucket, time_bucket, traffic_bucket, weather_bucket)

    def _discretize_location(self, lat, lng):
        """Discretize location into grid cells (~1.1km)"""
        lat_bucket = int(lat * 100) % 1000
        lng_bucket = int(lng * 100) % 1000
        return f"{lat_bucket}_{lng_bucket}"

    def _discretize_time(self, hour):
        """Discretize hour into time periods"""
        if 6 <= hour < 10:
            return "morning_rush"
        elif 10 <= hour < 17:
            return "daytime"
        elif 17 <= hour < 20:
            return "evening_rush"
        else:
            return "night"

    def _discretize_traffic(self, traffic_level):
        """Discretize traffic level"""
        if traffic_level < 0.3:
            return "low"
        elif traffic_level < 0.7:
            return "medium"
        else:
            return "high"

    def _discretize_weather(self, weather_condition):
        """Discretize weather condition"""
        return weather_condition

    def choose_action(self, state, available_routes):
        """
        Epsilon-greedy action selection
        """
        if not available_routes:
            return None
            
        if np.random.random() < self.epsilon:
            # Explore
            return np.random.choice(available_routes)
        else:
            # Exploit
            q_values = [self.q_table[state][route_id] for route_id in available_routes]
            
            if not q_values or max(q_values) == 0:
                return np.random.choice(available_routes)
            
            best_idx = np.argmax(q_values)
            return available_routes[best_idx]

    def update(self, state, action, reward, next_state, next_action):
        """
        SARSA update rule
        """
        current_q = self.q_table[state][action]
        next_q = self.q_table[next_state][next_action]
        
        new_q = current_q + self.alpha * (
            reward + self.gamma * next_q - current_q
        )
        
        self.q_table[state][action] = new_q

    def calculate_reward(self, route_outcome):
        """
        Multi-objective reward function
        """
        # Time efficiency
        predicted = route_outcome.get('predicted_time', 1)
        actual = route_outcome.get('actual_time', 1)
        time_ratio = actual / predicted if predicted > 0 else 1.0
        time_reward = -1 * (time_ratio - 1) * 10
        
        # Safety
        safety_reward = (route_outcome.get('safety_score', 50) / 100) * 10
        
        # Success bonus
        success_reward = 20 if route_outcome.get('delivered_successfully', True) else -30
        
        # Distance penalty
        distance_reward = -route_outcome.get('distance_km', 0) * 0.1
        
        return (0.25 * time_reward + 0.40 * safety_reward + 0.30 * success_reward + 0.05 * distance_reward)

    def save_model(self):
        """Save Q-table to disk"""
        with open(self.model_path, 'wb') as f:
            pickle.dump(dict(self.q_table), f)
        print(f"✅ SARSA Q-table saved ({len(self.q_table)} states)")

    def load_model(self):
        """Load Q-table from disk"""
        if not os.path.exists(self.model_path):
            return
        with open(self.model_path, 'rb') as f:
            saved_q_table = pickle.load(f)
            self.q_table = defaultdict(lambda: defaultdict(float), saved_q_table)
        print(f"✅ SARSA Q-table loaded")
