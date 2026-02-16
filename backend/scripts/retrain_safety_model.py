"""Script to retrain the safety scorer model using database feedback."""
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.database import SessionLocal
from database.models import SafetyFeedback
from api.models.safety_scorer import SafetyScorer
from loguru import logger

def retrain_model():
    """Fetch feedback and retrain safety model."""
    logger.info("Starting safety model retraining process...")
    
    db = SessionLocal()
    try:
        # Get processed and unprocessed feedback
        # In a real app, we might only use high-quality or verified feedback
        feedback_records = db.query(SafetyFeedback).all()
        
        if not feedback_records:
            logger.info("No feedback records found in database. Skipping retraining.")
            return False
            
        logger.info(f"Found {len(feedback_records)} feedback samples in database.")
        
        # Format for SafetyScorer
        feedback_list = []
        for fb in feedback_records:
            feedback_list.append({
                "location": fb.location,
                "rating": fb.rating,
                "time_of_day": fb.time_of_day,
                "feedback_type": fb.feedback_type
            })
            
        # Initialize scorer and retrain
        scorer = SafetyScorer()
        scorer.retrain_with_feedback(feedback_list)
        
        # Mark records as processed if needed (Phase 3)
        # for fb in feedback_records:
        #    fb.processed = True
        # db.commit()
        
        logger.info("Retraining complete!")
        return True
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error during retraining: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    retrain_model()
