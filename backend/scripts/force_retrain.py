import sys
from pathlib import Path
import os

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from api.models.safety_scorer import SafetyScorer
from config.config import settings
from loguru import logger

def force_retrain():
    print("🧠 Forcing SafetyScorer model retraining...")
    
    # Remove old model and scaler to force retraining
    if Path(settings.SAFETY_MODEL_PATH).exists():
        os.remove(settings.SAFETY_MODEL_PATH)
    if Path(settings.SAFETY_SCALER_PATH).exists():
        os.remove(settings.SAFETY_SCALER_PATH)
        
    scorer = SafetyScorer()
    # The constructor calls _initialize_model which calls _train_initial_model
    
    print("✅ SafetyScorer model retrained and initialized with new data.")

if __name__ == "__main__":
    force_retrain()
