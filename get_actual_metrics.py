
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

def get_metrics():
    db_path = 'backend/smartshield.db'
    conn = sqlite3.connect(db_path)
    
    # 1. Delivery Time Metrics
    df_outcomes = pd.read_sql_query("SELECT estimated_time, actual_time, estimated_distance, actual_distance, safety_score, success FROM delivery_outcomes", conn)
    
    if not df_outcomes.empty:
        avg_est_time = df_outcomes['estimated_time'].mean()
        avg_act_time = df_outcomes['actual_time'].mean()
        avg_est_dist = df_outcomes['estimated_distance'].mean()
        avg_act_dist = df_outcomes['actual_distance'].mean()
        avg_safety = df_outcomes['safety_score'].mean()
        success_rate = df_outcomes['success'].mean() * 100
        
        print("\n--- Delivery Performance Metrics ---")
        print(f"Average Estimated Time (Target): {avg_est_time:.2f} mins")
        print(f"Average Actual Time (Actual): {avg_act_time:.2f} mins")
        print(f"Time Variance: {((avg_act_time - avg_est_time) / avg_est_time) * 100:+.2f}%")
        
        print(f"\nAverage Estimated Distance (Target): {avg_est_dist:.2f} km")
        print(f"Average Actual Distance (Actual): {avg_act_dist:.2f} km")
        print(f"Distance Variance: {((avg_act_dist - avg_est_dist) / avg_est_dist) * 100:+.2f}%")
        
        print(f"\nAverage Safety Score: {avg_safety:.2f}/100")
        print(f"Delivery Success Rate: {success_rate:.2f}%")

    # 2. AI Model Metrics from training_history
    df_history = pd.read_sql_query("SELECT metrics FROM training_history ORDER BY timestamp DESC LIMIT 1", conn)
    if not df_history.empty:
        import ast
        metrics_raw = df_history.iloc[0]['metrics']
        try:
            metrics = ast.literal_eval(metrics_raw)
            print("\n--- AI Model Performance (Actuals) ---")
            if 'safety' in metrics and 'f1_weighted' in metrics['safety']:
                 print(f"Safety Classifier F1 Score: {metrics['safety']['f1_weighted']:.4f} (Target: >0.85)")
            if 'time' in metrics and 'r2' in metrics['time']:
                 print(f"Time Predictor R2 Score: {metrics['time']['r2']:.4f} (Target: >0.80)")
            if 'rl' in metrics and 'avg_episode_reward' in metrics['rl']:
                 print(f"RL Agent Avg Reward: {metrics['rl']['avg_episode_reward']:.2f}")
        except:
            print("\nCould not parse AI metrics.")

    conn.close()

if __name__ == "__main__":
    get_metrics()
