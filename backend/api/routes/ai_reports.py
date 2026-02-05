"""
API Routes for AI-Powered Report Summarization (FastAPI)
Provides endpoints for generating intelligent summaries
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.ai.report_summarizer import ReportSummarizer, ReportFormatter
# Assuming there's a dependency for authentication
# from backend.api.deps import get_current_user

router = APIRouter(prefix="/api/ai/reports", tags=["ai-reports"])

def get_date_range(time_period: str):
    """Calculate date range based on time period"""
    end_date = datetime.now()
    
    if time_period == "daily":
        start_date = end_date - timedelta(days=1)
    elif time_period == "weekly":
        start_date = end_date - timedelta(weeks=1)
    elif time_period == "monthly":
        start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(weeks=1)  # Default to weekly
    
    return start_date, end_date

# Mock aggregation functions (you should replace these with actual database calls)
def aggregate_user_data(start_date, end_date):
    return {
        "total_users": 1250,
        "new_users": 180,
        "returning_users": 1070,
        "avg_session_duration": 12.5,
        "total_requests": 3450,
        "safe_routes": 2890,
        "emergency_alerts": 15,
        "avg_safety_score": 87.3,
        "hospital_searches": 2100,
        "route_optimizations": 1850,
        "feedback_count": 245,
        "top_features": ["Hospital Search", "Route Optimization", "Emergency Alert"],
        "engagement_rate": 75.0
    }

def aggregate_rider_data(start_date, end_date):
    return {
        "total_riders": 85,
        "active_riders": 72,
        "routes_completed": 1250,
        "avg_efficiency": 87.5,
        "on_time_rate": 92.3,
        "rl_success_rate": 89.0,
        "avg_time_saved": 8.5,
        "safety_violations": 3,
        "fuel_improvement": 12.5,
        "total_distance": 15420,
        "avg_distance": 12.3,
        "peak_performance": "Good",
        "top_riders": [],
        "issues": [],
        "model_version": "v2.1"
    }

def aggregate_feedback_data(start_date, end_date):
    return {
        "total_feedback": 245,
        "avg_rating": 4.3,
        "response_rate": 85.0,
        "positive_sentiment": 68.5,
        "neutral_sentiment": 22.0,
        "negative_sentiment": 9.5,
        "categories": {"Navigation": 45, "Safety": 30, "UI/UX": 15, "Performance": 10},
        "top_issues": ["Slow route calculation"],
        "feature_requests": ["Offline mode"],
        "sample_comments": ["Great app!"],
        "previous_rating": 4.1,
        "rating_change": 0.2
    }

def aggregate_ml_model_data():
    return {
        "model_type": "RL Agent",
        "version": "v2.1",
        "accuracy": 91.5,
        "precision": 89.2,
        "recall": 93.1,
        "f1_score": 91.1,
        "total_predictions": 15420,
        "successful_optimizations": 13890,
        "avg_improvement": 18.5,
        "satisfaction_impact": 12.3
    }

@router.post("/user-summary")
async def generate_user_summary(payload: Dict[str, Any]):
    try:
        time_period = payload.get('time_period', 'weekly')
        provider = payload.get('provider', 'openai')
        output_format = payload.get('format', 'json')
        
        start_date, end_date = get_date_range(time_period)
        user_data = aggregate_user_data(start_date, end_date)
        
        summarizer = ReportSummarizer(provider=provider)
        summary = summarizer.summarize_user_report(user_data, time_period)
        
        if output_format == 'markdown':
            return {"report": ReportFormatter.to_markdown(summary), "format": "markdown"}
        elif output_format == 'html':
            return {"report": ReportFormatter.to_html(summary), "format": "html"}
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rider-summary")
async def generate_rider_summary(payload: Dict[str, Any]):
    try:
        time_period = payload.get('time_period', 'weekly')
        provider = payload.get('provider', 'openai')
        output_format = payload.get('format', 'json')
        
        start_date, end_date = get_date_range(time_period)
        rider_data = aggregate_rider_data(start_date, end_date)
        
        summarizer = ReportSummarizer(provider=provider)
        summary = summarizer.summarize_rider_report(rider_data, time_period)
        
        if output_format == 'markdown':
            return {"report": ReportFormatter.to_markdown(summary), "format": "markdown"}
        elif output_format == 'html':
            return {"report": ReportFormatter.to_html(summary), "format": "html"}
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback-summary")
async def generate_feedback_summary(payload: Dict[str, Any]):
    try:
        time_period = payload.get('time_period', 'weekly')
        provider = payload.get('provider', 'openai')
        output_format = payload.get('format', 'json')
        
        start_date, end_date = get_date_range(time_period)
        feedback_data = aggregate_feedback_data(start_date, end_date)
        
        summarizer = ReportSummarizer(provider=provider)
        summary = summarizer.summarize_feedback_report(feedback_data, time_period)
        
        if output_format == 'markdown':
            return {"report": ReportFormatter.to_markdown(summary), "format": "markdown"}
        elif output_format == 'html':
            return {"report": ReportFormatter.to_html(summary), "format": "html"}
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ml-performance")
async def generate_ml_performance_summary(payload: Dict[str, Any]):
    try:
        provider = payload.get('provider', 'openai')
        output_format = payload.get('format', 'json')
        
        ml_data = aggregate_ml_model_data()
        
        summarizer = ReportSummarizer(provider=provider)
        summary = summarizer.summarize_ml_model_performance(ml_data)
        
        if output_format == 'markdown':
            return {"report": ReportFormatter.to_markdown(summary), "format": "markdown"}
        elif output_format == 'html':
            return {"report": ReportFormatter.to_html(summary), "format": "html"}
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/executive-dashboard")
async def generate_executive_dashboard(payload: Dict[str, Any]):
    try:
        time_period = payload.get('time_period', 'weekly')
        provider = payload.get('provider', 'openai')
        output_format = payload.get('format', 'json')
        
        start_date, end_date = get_date_range(time_period)
        user_data = aggregate_user_data(start_date, end_date)
        rider_data = aggregate_rider_data(start_date, end_date)
        feedback_data = aggregate_feedback_data(start_date, end_date)
        ml_data = aggregate_ml_model_data()
        
        summarizer = ReportSummarizer(provider=provider)
        summary = summarizer.generate_executive_dashboard_summary(
            user_data, rider_data, feedback_data, ml_data
        )
        
        if output_format == 'markdown':
            return {"report": ReportFormatter.to_markdown(summary), "format": "markdown"}
        elif output_format == 'html':
            return {"report": ReportFormatter.to_html(summary), "format": "html"}
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Report Summarizer",
        "timestamp": datetime.now().isoformat()
    }
