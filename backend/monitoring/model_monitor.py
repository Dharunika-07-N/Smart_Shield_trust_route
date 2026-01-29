import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import sqlite3
from datetime import datetime, timedelta
from scipy import stats
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelMonitor:
    """
    Monitor model performance and detect drift
    
    Features:
    - Performance tracking
    - Feature drift detection
    - Prediction drift detection
    - Automated retraining triggers
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
             self.db_path = os.path.join(Path(__file__).parent.parent.parent, "backend", "smartshield.db")
             # Fallback if running from root without proper environment setup
             if not os.path.exists(os.path.dirname(self.db_path)):
                 self.db_path = "smartshield.db" 
        else:
             self.db_path = db_path

        self.drift_threshold = 0.1  # 10% drift triggers alert
        self.performance_degradation_threshold = 0.15  # 15% worse
        
        # Ensure schema
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prediction_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT, 
            timestamp DATETIME, 
            prediction REAL, 
            actual REAL, 
            features TEXT, 
            metadata TEXT
        )
        """)
        conn.commit()
        conn.close()
    
    def track_prediction(
        self,
        model_name: str,
        prediction: float,
        features: Dict,
        actual: float = None,
        metadata: Dict = None
    ):
        """Track a prediction for monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO prediction_log 
        (model_name, timestamp, prediction, actual, features, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            model_name,
            datetime.now().isoformat(),
            float(prediction) if prediction is not None else None,
            float(actual) if actual is not None else None,
            str(features),
            str(metadata) if metadata else None
        ))
        
        conn.commit()
        conn.close()
    
    def calculate_performance_metrics(
        self,
        model_name: str,
        time_window_days: int = 7
    ) -> Dict:
        """
        Calculate recent performance metrics
        """
        conn = sqlite3.connect(self.db_path)
        
        cutoff_date = (datetime.now() - timedelta(days=time_window_days)).isoformat()
        
        query = f"""
        SELECT prediction, actual
        FROM prediction_log
        WHERE model_name = ?
        AND actual IS NOT NULL
        AND timestamp > ?
        """
        
        df = pd.read_sql_query(query, conn, params=(model_name, cutoff_date))
        conn.close()
        
        if len(df) < 10:
            # Try getting any data if recent data is missing to avoid total failure to report
            return {'status': 'insufficient_data', 'num_samples': len(df)}
        
        y_true = df['actual'].values
        y_pred = df['prediction'].values
        
        # Calculate metrics
        mae = np.mean(np.abs(y_true - y_pred))
        mse = np.mean((y_true - y_pred) ** 2)
        rmse = np.sqrt(mse)
        
        # MAPE
        non_zero = y_true != 0
        if non_zero.any():
            mape = np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100
        else:
            mape = None
        
        # R²
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape) if mape is not None else None,
            'r2': float(r2),
            'num_samples': len(df),
            'time_window_days': time_window_days
        }
    
    def detect_feature_drift(
        self,
        model_name: str,
        current_features: pd.DataFrame,
        reference_window_days: int = 30,
        method: str = 'ks_test'
    ) -> Dict:
        """
        Detect drift in feature distributions
        
        Methods:
        - ks_test: Kolmogorov-Smirnov test
        - psi: Population Stability Index
        """
        conn = sqlite3.connect(self.db_path)
        
        cutoff_date = (datetime.now() - timedelta(days=reference_window_days)).isoformat()
        
        query = f"""
        SELECT features
        FROM prediction_log
        WHERE model_name = ?
        AND timestamp > ?
        LIMIT 1000
        """
        
        df = pd.read_sql_query(query, conn, params=(model_name, cutoff_date))
        conn.close()
        
        if len(df) < 30:
            return {'status': 'insufficient_reference_data'}
        
        # Parse features from stored strings
        reference_features = []
        for features_str in df['features']:
            try:
                features_dict = eval(features_str)
                reference_features.append(features_dict)
            except:
                continue
        
        if not reference_features:
            return {'status': 'no_parseable_features'}
        
        reference_df = pd.DataFrame(reference_features)
        
        drift_results = {}
        
        for col in current_features.columns:
            if col not in reference_df.columns:
                continue
            
            current_vals = current_features[col].dropna()
            reference_vals = reference_df[col].dropna()
            
            if len(current_vals) == 0 or len(reference_vals) == 0:
                continue
            
            if method == 'ks_test':
                # Kolmogorov-Smirnov test
                statistic, p_value = stats.ks_2samp(current_vals, reference_vals)
                
                drift_results[col] = {
                    'method': 'ks_test',
                    'statistic': float(statistic),
                    'p_value': float(p_value),
                    'drift_detected': p_value < 0.05,
                    'drift_magnitude': float(statistic)
                }
                
            elif method == 'psi':
                # Population Stability Index
                psi = self._calculate_psi(reference_vals, current_vals)
                
                drift_results[col] = {
                    'method': 'psi',
                    'psi_value': float(psi),
                    'drift_detected': psi > 0.1,
                    'drift_magnitude': float(psi)
                }
        
        # Overall drift score
        if drift_results:
            drift_magnitudes = [v['drift_magnitude'] for v in drift_results.values()]
            overall_drift = np.mean(drift_magnitudes)
            
            return {
                'overall_drift': float(overall_drift),
                'drift_detected': overall_drift > self.drift_threshold,
                'features_drifted': [k for k, v in drift_results.items() if v['drift_detected']],
                'feature_details': drift_results
            }
        
        return {'status': 'no_common_features'}
    
    @staticmethod
    def _calculate_psi(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
        """
        Calculate Population Stability Index
        
        PSI = Σ (current% - reference%) * ln(current% / reference%)
        """
        # Create bins based on reference distribution
        # Handle cases with low variance/singularity in reference
        if np.all(reference == reference[0]):
             # If reference is constant, cannot calculate PSI meaningfully if current is different
             # Return low PSI if current is also constant and same, high if different
             if np.all(current == reference[0]): return 0.0
             else: return 1.0 # arbitrary high

        ref_percentiles = np.percentile(reference, np.linspace(0, 100, bins + 1))
        
        # Calculate frequencies
        ref_freq = np.histogram(reference, bins=ref_percentiles)[0] / len(reference)
        cur_freq = np.histogram(current, bins=ref_percentiles)[0] / len(current)
        
        # Avoid division by zero
        ref_freq = np.where(ref_freq == 0, 0.0001, ref_freq)
        cur_freq = np.where(cur_freq == 0, 0.0001, cur_freq)
        
        # Calculate PSI
        psi = np.sum((cur_freq - ref_freq) * np.log(cur_freq / ref_freq))
        
        return psi
    
    def detect_prediction_drift(
        self,
        model_name: str,
        time_window_days: int = 7,
        reference_window_days: int = 30
    ) -> Dict:
        """Detect drift in prediction distributions"""
        conn = sqlite3.connect(self.db_path)
        
        # Current window
        current_cutoff = (datetime.now() - timedelta(days=time_window_days)).isoformat()
        current_query = f"""
        SELECT prediction
        FROM prediction_log
        WHERE model_name = ?
        AND timestamp > ?
        """
        current_df = pd.read_sql_query(current_query, conn, params=(model_name, current_cutoff))
        
        # Reference window
        reference_start = (datetime.now() - timedelta(days=reference_window_days + time_window_days)).isoformat()
        reference_end = (datetime.now() - timedelta(days=time_window_days)).isoformat()
        reference_query = f"""
        SELECT prediction
        FROM prediction_log
        WHERE model_name = ?
        AND timestamp BETWEEN ? AND ?
        """
        reference_df = pd.read_sql_query(
            reference_query, conn,
            params=(model_name, reference_start, reference_end)
        )
        
        conn.close()
        
        if len(current_df) < 5 or len(reference_df) < 5: # Lowered threshold for PoC
            return {'status': 'insufficient_data'}
        
        # KS test
        statistic, p_value = stats.ks_2samp(
            current_df['prediction'],
            reference_df['prediction']
        )
        
        return {
            'ks_statistic': float(statistic),
            'p_value': float(p_value),
            'drift_detected': p_value < 0.05,
            'current_mean': float(current_df['prediction'].mean()),
            'reference_mean': float(reference_df['prediction'].mean()),
            'mean_shift': float(current_df['prediction'].mean() - reference_df['prediction'].mean())
        }
    
    def check_retraining_needed(self, model_name: str) -> Tuple[bool, Dict]:
        """
        Determine if model needs retraining
        
        Returns:
            needs_retraining: Boolean
            reasons: Dict with reasons and metrics
        """
        reasons = {}
        needs_retraining = False
        
        # Check performance degradation
        current_perf = self.calculate_performance_metrics(model_name, time_window_days=7)
        
        if current_perf.get('status') != 'insufficient_data':
            # Get baseline performance
            baseline_perf = self.get_baseline_performance(model_name)
            
            if baseline_perf:
                # Compare metrics
                if 'mae' in current_perf and 'mae' in baseline_perf:
                    mae_increase = (current_perf['mae'] - baseline_perf['mae']) / baseline_perf['mae']
                    
                    if mae_increase > self.performance_degradation_threshold:
                        needs_retraining = True
                        reasons['performance_degradation'] = {
                            'current_mae': current_perf['mae'],
                            'baseline_mae': baseline_perf['mae'],
                            'increase_pct': mae_increase * 100
                        }
        
        # Check feature drift
        # (Would need current feature data to check this properly)
        
        # Check time since last training
        last_training = self.get_last_training_time(model_name)
        if last_training:
            days_since_training = (datetime.now() - last_training).days
            
            if days_since_training > 30:  # Retrain every 30 days
                needs_retraining = True
                reasons['time_based'] = {
                    'days_since_training': days_since_training,
                    'threshold_days': 30
                }
        else:
             # Never trained?
             pass
        
        return needs_retraining, reasons
    
    def get_baseline_performance(self, model_name: str) -> Dict:
        """Get baseline performance metrics from training history"""
        conn = sqlite3.connect(self.db_path)
        
        # Ensure training_history exists
        try:
            query = """
            SELECT metrics
            FROM training_history
            WHERE models_trained LIKE ?
            ORDER BY timestamp DESC
            LIMIT 1
            """
            
            cursor = conn.cursor()
            cursor.execute(query, (f'%{model_name}%',))
            row = cursor.fetchone()
        except sqlite3.OperationalError:
            row = None
        
        conn.close()
        
        if row:
            try:
                metrics = eval(row[0])
                if model_name in metrics:
                     # New format: {'safety': {...}, 'time': {...}}
                     return metrics[model_name].get('test', {})
                else:
                     # Maybe old format or direct metrics dict
                     return metrics.get('test', {})
            except:
                return {}
        
        return {}
    
    def get_last_training_time(self, model_name: str) -> datetime:
        """Get timestamp of last training"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            query = """
            SELECT timestamp
            FROM training_history
            WHERE models_trained LIKE ?
            ORDER BY timestamp DESC
            LIMIT 1
            """
            
            cursor = conn.cursor()
            cursor.execute(query, (f'%{model_name}%',))
            row = cursor.fetchone()
        except sqlite3.OperationalError:
             row = None
        
        conn.close()
        
        if row:
            try:
                 return datetime.fromisoformat(row[0])
            except ValueError:
                 return None
        
        return None
    
    def generate_monitoring_report(self, model_name: str) -> Dict:
        """Generate comprehensive monitoring report"""
        report = {
            'model_name': model_name,
            'timestamp': datetime.now().isoformat(),
            'performance': self.calculate_performance_metrics(model_name),
            'prediction_drift': self.detect_prediction_drift(model_name),
            'retraining_check': {}
        }
        
        needs_retraining, reasons = self.check_retraining_needed(model_name)
        report['retraining_check'] = {
            'needs_retraining': needs_retraining,
            'reasons': reasons
        }
        
        return report
