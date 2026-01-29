import numpy as np
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ABTester:
    """
    A/B Testing Framework for ML Models
    
    Features:
    - Experiment management
    - Traffic splitting (hash-based for consistency)
    - Performance comparison
    - Winner selection
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
             self.db_path = os.path.join(Path(__file__).parent.parent, "smartshield.db")
        else:
             self.db_path = db_path
             
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Experiments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_experiments (
            experiment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            model_type TEXT,
            version_a TEXT,
            version_b TEXT,
            traffic_split_a REAL DEFAULT 0.5,
            status TEXT DEFAULT 'active',
            start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_date DATETIME,
            description TEXT
        )
        """)
        
        # Assignment log
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiment_assignments (
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            entity_id TEXT,
            assigned_group TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (experiment_id) REFERENCES ml_experiments(experiment_id)
        )
        """)
        
        conn.commit()
        conn.close()
        
    def create_experiment(
        self, 
        name: str, 
        model_type: str, 
        version_a: str, 
        version_b: str, 
        split: float = 0.5,
        description: str = ""
    ) -> int:
        """Create a new experiment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO ml_experiments (name, model_type, version_a, version_b, traffic_split_a, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (name, model_type, version_a, version_b, split, description))
            exp_id = cursor.lastrowid
            conn.commit()
            return exp_id
        except sqlite3.IntegrityError:
            logger.error(f"Experiment {name} already exists")
            return -1
        finally:
            conn.close()
            
    def get_assigned_version(self, experiment_name: str, entity_id: str) -> str:
        """
        Assign an entity (user_id or delivery_id) to a group based on hash
        to ensure consistency.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT experiment_id, version_a, version_b, traffic_split_a 
        FROM ml_experiments 
        WHERE name = ? AND status = 'active'
        """, (experiment_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return "original" # Default if no experiment found
            
        exp_id, v_a, v_b, split = row
        
        # Hash-based splitting for consistency
        hash_val = int(hashlib.md5(f"{experiment_name}:{entity_id}".encode()).hexdigest(), 16)
        normalized_hash = (hash_val % 100) / 100.0
        
        assigned_group = "A" if normalized_hash < split else "B"
        assigned_version = v_a if assigned_group == "A" else v_b
        
        # Log assignment (Optional: could be heavy for high traffic)
        self._log_assignment(exp_id, entity_id, assigned_group)
        
        return assigned_version
        
    def _log_assignment(self, exp_id: int, entity_id: str, group: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO experiment_assignments (experiment_id, entity_id, assigned_group)
        VALUES (?, ?, ?)
        """, (exp_id, entity_id, group))
        conn.commit()
        conn.close()
        
    def compare_performance(self, experiment_name: str) -> Dict:
        """Compare metrics between groups A and B"""
        conn = sqlite3.connect(self.db_path)
        
        # Get experiment details
        cursor = conn.cursor()
        cursor.execute("SELECT experiment_id, version_a, version_b, model_type FROM ml_experiments WHERE name = ?", (experiment_name,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"error": "Experiment not found"}
            
        exp_id, v_a, v_b, model_type = row
        
        # Join assignments with prediction_log (created in model_monitor)
        # Assuming entity_id in assignments matches metadata/metadata['id'] in prediction_log
        # This is a bit complex as features/metadata are strings. 
        # Simplified: Use a temporary table or subquery if we can link them.
        
        # For simplicity in this demo, we'll fetch all assignments and then fetch corresponding logs
        query = f"""
        SELECT a.assigned_group, p.prediction, p.actual, p.model_name
        FROM experiment_assignments a
        JOIN ml_experiments e ON a.experiment_id = e.experiment_id
        JOIN prediction_log p ON (p.metadata LIKE '%' || a.entity_id || '%')
        WHERE e.name = ? AND p.actual IS NOT NULL
        """
        
        df = pd.read_sql_query(query, conn, params=(experiment_name,))
        conn.close()
        
        if df.empty:
            return {"status": "No data for comparison"}
            
        results = {}
        for group in ['A', 'B']:
            group_df = df[df['assigned_group'] == group]
            if not group_df.empty:
                y_true = group_df['actual'].values
                y_pred = group_df['prediction'].values
                
                # Metric calculation based on model type
                if model_type == 'time':
                    mae = np.mean(np.abs(y_true - y_pred))
                    rmse = np.sqrt(np.mean((y_true - y_pred)**2))
                    results[group] = {"mae": float(mae), "rmse": float(rmse), "count": len(group_df)}
                else:
                    # Generic accuracy for classification
                    acc = np.mean((y_pred > 50 if model_type == 'safety' else y_pred) == (y_true > 50 if model_type == 'safety' else y_true))
                    results[group] = {"accuracy": float(acc), "count": len(group_df)}
                    
        return {
            "experiment": experiment_name,
            "results": results,
            "winner": self._determine_winner(results, model_type) if len(results) == 2 else None
        }
        
    def _determine_winner(self, results: Dict, model_type: str) -> Optional[str]:
        if 'A' not in results or 'B' not in results:
            return None
            
        if model_type == 'time':
            return "A" if results['A']['mae'] < results['B']['mae'] else "B"
        else:
            return "A" if results['A'].get('accuracy', 0) > results['B'].get('accuracy', 0) else "B"
            
    def stop_experiment(self, name: str, winner_version: str):
        """Stop experiment and mark winner"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE ml_experiments 
        SET status = 'completed', end_date = CURRENT_TIMESTAMP 
        WHERE name = ?
        """, (name,))
        conn.commit()
        conn.close()
        logger.info(f"Experiment {name} stopped. Winner: {winner_version}")
