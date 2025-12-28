import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from api.models.safety_scorer import SafetyScorer
from api.schemas.delivery import Coordinate
from loguru import logger

def test_police_scoring():
    logger.info("Initializing SafetyScorer (should trigger retraining if model is old)...")
    scorer = SafetyScorer()
    
    # R.S. Puram (Near a station)
    # Station at: 11.014206, 76.951475
    expert_location = Coordinate(latitude=11.0143, longitude=76.9515)
    
    # Far away location
    far_location = Coordinate(latitude=11.1000, longitude=77.1000)
    
    logger.info("Scoring location NEAR police station...")
    score1, factors1 = scorer.score_location(expert_location)
    logger.info(f"Score: {score1}")
    for f in factors1:
        if f['factor'] == 'police_proximity':
            logger.info(f"Police Proximity Factor: {f}")
            
    logger.info("-" * 50)
            
    logger.info("Scoring location FAR from police station...")
    score2, factors2 = scorer.score_location(far_location)
    logger.info(f"Score: {score2}")
    for f in factors2:
        if f['factor'] == 'police_proximity':
            logger.info(f"Police Proximity Factor: {f}")

if __name__ == "__main__":
    test_police_scoring()
