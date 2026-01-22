"""
Enhanced ML Model Training Script
Trains all ML models with real data and dynamic statistics
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from ml.time_predictor import DeliveryTimePredictor
from ml.safety_classifier import SafetyClassifier
from ml.rl_agent import SARSARouteAgent
from ml.feature_engineer import FeatureEngineer
from loguru import logger


class MLModelTrainer:
    """Orchestrates training of all ML models"""
    
    def __init__(self, data_dir="backend/data/ml_training"):
        self.data_dir = Path(data_dir)
        self.models_dir = Path("backend/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.time_predictor = DeliveryTimePredictor()
        self.safety_classifier = SafetyClassifier()
        self.rl_agent = SARSARouteAgent()
        
        self.training_stats = {}
    
    def load_data(self, filename):
        """Load CSV data file"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            logger.warning(f"Data file not found: {filepath}")
            return None
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} records from {filename}")
            return df
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return None
    
    def train_time_predictor(self):
        """Train delivery time prediction model"""
        logger.info("=" * 60)
        logger.info("Training Delivery Time Predictor")
        logger.info("=" * 60)
        
        df = self.load_data('historical_deliveries.csv')
        if df is None or len(df) < 100:
            logger.warning("Insufficient data for time predictor. Need at least 100 samples.")
            return False
        
        # Feature engineering
        features = [
            'distance_km', 'traffic_level', 'hour', 'day_of_week',
            'is_weekend', 'is_peak_hour', 'num_turns', 'num_traffic_lights'
        ]
        
        # Encode categorical variables
        traffic_map = {'low': 0, 'medium': 1, 'high': 2}
        df['traffic_level'] = df['traffic_level'].map(traffic_map)
        
        # Create derived features
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_peak_hour'] = df['hour'].isin([8, 9, 17, 18, 19]).astype(int)
        
        # Prepare X and y
        X = df[features]
        y = df['actual_time_minutes']
        
        # Train model
        results = self.time_predictor.train(X, y)
        
        self.training_stats['time_predictor'] = {
            'samples': len(df),
            'mae': results['mae'],
            'r2': results['r2'],
            'features': features,
            'feature_importance': results['feature_importance'],
            'trained_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Time Predictor trained successfully!")
        logger.info(f"   MAE: {results['mae']:.2f} minutes")
        logger.info(f"   R²: {results['r2']:.4f}")
        
        return True
    
    def train_safety_classifier(self):
        """Train safety classification model"""
        logger.info("=" * 60)
        logger.info("Training Safety Classifier")
        logger.info("=" * 60)
        
        df = self.load_data('crime_incidents.csv')
        if df is None or len(df) < 100:
            logger.warning("Insufficient data for safety classifier. Need at least 100 samples.")
            return False
        
        # Aggregate crime data by location grid
        df['lat_grid'] = (df['latitude'] * 100).round() / 100
        df['lng_grid'] = (df['longitude'] * 100).round() / 100
        
        # Create features
        location_stats = df.groupby(['lat_grid', 'lng_grid']).agg({
            'incident_id': 'count',
            'severity': lambda x: (x == 'high').sum(),
            'resolved': 'mean'
        }).reset_index()
        
        location_stats.columns = ['lat', 'lng', 'crime_count', 'high_severity_count', 'resolution_rate']
        
        # Create safety labels (binary: safe=1, unsafe=0)
        location_stats['is_safe'] = (
            (location_stats['crime_count'] < 5) & 
            (location_stats['high_severity_count'] == 0)
        ).astype(int)
        
        features = ['crime_count', 'high_severity_count', 'resolution_rate']
        X = location_stats[features]
        y = location_stats['is_safe']
        
        # Train model
        results = self.safety_classifier.train(X, y)
        
        self.training_stats['safety_classifier'] = {
            'samples': len(location_stats),
            'accuracy': results['accuracy'],
            'precision': results['precision'],
            'recall': results['recall'],
            'f1': results['f1'],
            'features': features,
            'trained_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Safety Classifier trained successfully!")
        logger.info(f"   Accuracy: {results['accuracy']:.4f}")
        logger.info(f"   F1 Score: {results['f1']:.4f}")
        
        return True
    
    def train_rl_agent(self):
        """Train reinforcement learning agent"""
        logger.info("=" * 60)
        logger.info("Training RL Agent")
        logger.info("=" * 60)
        
        df = self.load_data('rl_episodes.csv')
        if df is None or len(df) < 50:
            logger.warning("Insufficient data for RL agent. Need at least 50 episodes.")
            return False
        
        # Parse episode data
        episodes = []
        for _, row in df.iterrows():
            episode = {
                'states': eval(row['state_sequence']),
                'actions': eval(row['action_sequence']),
                'rewards': eval(row['reward_sequence']),
                'total_reward': row['total_reward']
            }
            episodes.append(episode)
        
        # Train RL agent
        results = self.rl_agent.train_from_episodes(episodes)
        
        self.training_stats['rl_agent'] = {
            'episodes': len(episodes),
            'avg_reward': results.get('avg_reward', 0),
            'convergence': results.get('convergence', False),
            'trained_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ RL Agent trained successfully!")
        logger.info(f"   Episodes: {len(episodes)}")
        logger.info(f"   Avg Reward: {results.get('avg_reward', 0):.2f}")
        
        return True
    
    def generate_statistics_report(self):
        """Generate dynamic statistics report"""
        logger.info("=" * 60)
        logger.info("Generating Statistics Report")
        logger.info("=" * 60)
        
        # Load all data
        deliveries = self.load_data('historical_deliveries.csv')
        crimes = self.load_data('crime_incidents.csv')
        riders = self.load_data('rider_performance.csv')
        traffic = self.load_data('traffic_patterns.csv')
        
        stats = {
            'data_summary': {
                'total_deliveries': len(deliveries) if deliveries is not None else 0,
                'total_crime_incidents': len(crimes) if crimes is not None else 0,
                'total_riders': len(riders) if riders is not None else 0,
                'traffic_data_points': len(traffic) if traffic is not None else 0
            },
            'delivery_statistics': {},
            'safety_statistics': {},
            'rider_statistics': {},
            'traffic_statistics': {}
        }
        
        # Delivery statistics
        if deliveries is not None and len(deliveries) > 0:
            stats['delivery_statistics'] = {
                'avg_time_minutes': float(deliveries['actual_time_minutes'].mean()),
                'avg_distance_km': float(deliveries['distance_km'].mean()),
                'success_rate': float(deliveries['success'].mean()),
                'peak_hour_deliveries': int((deliveries['hour'].isin([8, 9, 17, 18, 19])).sum()),
                'weekend_deliveries': int((deliveries['day_of_week'] >= 5).sum())
            }
        
        # Safety statistics
        if crimes is not None and len(crimes) > 0:
            stats['safety_statistics'] = {
                'high_severity_incidents': int((crimes['severity'] == 'high').sum()),
                'resolution_rate': float(crimes['resolved'].mean()),
                'night_incidents': int((crimes['time_of_day'] == 'night').sum()),
                'most_common_crime': crimes['crime_type'].mode()[0] if len(crimes) > 0 else 'N/A'
            }
        
        # Rider statistics
        if riders is not None and len(riders) > 0:
            stats['rider_statistics'] = {
                'avg_experience_months': float(riders['experience_months'].mean()),
                'avg_success_rate': float(riders['success_rate'].mean()),
                'avg_rating': float(riders['avg_rating'].mean()),
                'total_deliveries': int(riders['total_deliveries'].sum())
            }
        
        # Traffic statistics
        if traffic is not None and len(traffic) > 0:
            stats['traffic_statistics'] = {
                'avg_speed_kmh': float(traffic['avg_speed_kmh'].mean()),
                'high_congestion_periods': int((traffic['congestion_level'] == 'high').sum()),
                'peak_hour_avg_speed': float(
                    traffic[traffic['hour'].isin([8, 9, 17, 18, 19])]['avg_speed_kmh'].mean()
                ) if len(traffic[traffic['hour'].isin([8, 9, 17, 18, 19])]) > 0 else 0
            }
        
        # Save statistics
        stats_file = self.models_dir / 'training_statistics.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, indent=2, fp=f)
        
        logger.info(f"✅ Statistics report saved to {stats_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("TRAINING STATISTICS SUMMARY")
        print("=" * 60)
        print(json.dumps(stats, indent=2))
        print("=" * 60)
        
        return stats
    
    def train_all_models(self):
        """Train all ML models"""
        logger.info("\n🚀 Starting ML Model Training Pipeline\n")
        
        success_count = 0
        
        # Train each model
        if self.train_time_predictor():
            success_count += 1
        
        if self.train_safety_classifier():
            success_count += 1
        
        if self.train_rl_agent():
            success_count += 1
        
        # Generate statistics
        stats = self.generate_statistics_report()
        
        # Save training summary
        summary = {
            'training_stats': self.training_stats,
            'data_stats': stats,
            'models_trained': success_count,
            'timestamp': datetime.now().isoformat()
        }
        
        summary_file = self.models_dir / 'training_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, indent=2, fp=f)
        
        logger.info(f"\n✅ Training complete! {success_count}/3 models trained successfully")
        logger.info(f"📊 Training summary saved to {summary_file}")
        
        return success_count == 3


if __name__ == "__main__":
    # Create sample data first
    from ml.data_templates import save_templates_to_csv
    
    print("Creating sample data templates...")
    save_templates_to_csv()
    
    print("\n" + "=" * 60)
    print("IMPORTANT: Fill the CSV files with real data before training!")
    print("=" * 60)
    print("\nTo train models with real data:")
    print("1. Collect historical delivery data (10,000+ records recommended)")
    print("2. Gather crime incident data (5,000+ records recommended)")
    print("3. Compile rider performance data (100+ riders recommended)")
    print("4. Run: python backend/ml/train_models.py")
    print("\nFor now, creating sample data for demonstration...")
    
    # Train with sample data
    trainer = MLModelTrainer()
    trainer.train_all_models()
