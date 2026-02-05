"""
Test Suite for AI Report Summarizer
Demonstrates usage and validates functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ai.report_summarizer import ReportSummarizer, ReportFormatter


def test_user_report_summary():
    """Test user activity report generation"""
    print("\n" + "="*60)
    print("TEST 1: User Activity Report Summary")
    print("="*60 + "\n")
    
    # Sample user data
    user_data = {
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
    
    try:
        # Initialize summarizer with OpenAI
        summarizer = ReportSummarizer(provider="openai")
        
        # Generate summary
        print("Generating AI summary... (this may take 10-15 seconds)")
        summary = summarizer.summarize_user_report(user_data, time_period="weekly")
        
        # Display results
        print("\n✅ Summary Generated Successfully!\n")
        print(f"Generated At: {summary['generated_at']}")
        print(f"Time Period: {summary['time_period']}")
        print(f"AI Provider: {summary['provider']}")
        print(f"\n{'-'*60}\n")
        print(summary['summary'])
        print(f"\n{'-'*60}\n")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_rider_report_summary():
    """Test rider performance report generation"""
    print("\n" + "="*60)
    print("TEST 2: Rider Performance Report Summary")
    print("="*60 + "\n")
    
    # Sample rider data
    rider_data = {
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
        "top_riders": [
            {"name": "Rider #42", "efficiency": 95.2},
            {"name": "Rider #17", "efficiency": 93.8},
            {"name": "Rider #31", "efficiency": 92.1}
        ],
        "issues": [
            "3 safety violations in Zone A",
            "Delayed deliveries during peak hours"
        ],
        "model_version": "v2.1"
    }
    
    try:
        summarizer = ReportSummarizer(provider="openai")
        
        print("Generating AI summary... (this may take 10-15 seconds)")
        summary = summarizer.summarize_rider_report(rider_data, time_period="weekly")
        
        print("\n✅ Summary Generated Successfully!\n")
        print(f"Generated At: {summary['generated_at']}")
        print(f"ML Model Version: {summary['ml_model_version']}")
        print(f"\n{'-'*60}\n")
        print(summary['summary'])
        print(f"\n{'-'*60}\n")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_feedback_report_summary():
    """Test feedback analysis report generation"""
    print("\n" + "="*60)
    print("TEST 3: Feedback Analysis Report Summary")
    print("="*60 + "\n")
    
    # Sample feedback data
    feedback_data = {
        "total_feedback": 245,
        "avg_rating": 4.3,
        "response_rate": 85.0,
        "positive_sentiment": 68.5,
        "neutral_sentiment": 22.0,
        "negative_sentiment": 9.5,
        "categories": {
            "Navigation": 45,
            "Safety": 30,
            "UI/UX": 15,
            "Performance": 10
        },
        "top_issues": [
            "Route calculation slow in peak hours",
            "Map loading issues in rural areas",
            "Notification delays"
        ],
        "feature_requests": [
            "Offline mode for maps",
            "Voice navigation support",
            "Multi-stop routing"
        ],
        "sample_comments": [
            "Great app! Saved me 15 minutes on my hospital visit.",
            "Love the safety features, but maps could load faster.",
            "Very helpful during emergencies."
        ],
        "previous_rating": 4.1,
        "rating_change": 0.2
    }
    
    try:
        summarizer = ReportSummarizer(provider="openai")
        
        print("Generating AI summary... (this may take 10-15 seconds)")
        summary = summarizer.summarize_feedback_report(feedback_data, time_period="weekly")
        
        print("\n✅ Summary Generated Successfully!\n")
        print(f"Sentiment Score: {summary['sentiment_score']}/5.0")
        print(f"\n{'-'*60}\n")
        print(summary['summary'])
        print(f"\n{'-'*60}\n")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_ml_performance_summary():
    """Test ML model performance report generation"""
    print("\n" + "="*60)
    print("TEST 4: ML Model Performance Report Summary")
    print("="*60 + "\n")
    
    # Sample ML model data
    ml_data = {
        "model_type": "Reinforcement Learning Agent",
        "version": "v2.1",
        "last_trained": "2026-02-01",
        "training_duration": 45,
        "accuracy": 91.5,
        "precision": 89.2,
        "recall": 93.1,
        "f1_score": 91.1,
        "loss": 0.087,
        "total_predictions": 15420,
        "successful_optimizations": 13890,
        "avg_improvement": 18.5,
        "satisfaction_impact": 12.3,
        "avg_inference_time": 45,
        "memory_usage": 512,
        "api_calls": 15420,
        "version_comparison": {
            "v2.0_accuracy": 88.3,
            "v2.1_accuracy": 91.5,
            "improvement": 3.2
        }
    }
    
    try:
        summarizer = ReportSummarizer(provider="openai")
        
        print("Generating AI summary... (this may take 10-15 seconds)")
        summary = summarizer.summarize_ml_model_performance(ml_data)
        
        print("\n✅ Summary Generated Successfully!\n")
        print(f"Model Version: {summary['model_version']}")
        print(f"Performance Score: {summary['performance_score']}%")
        print(f"\n{'-'*60}\n")
        print(summary['summary'])
        print(f"\n{'-'*60}\n")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_executive_dashboard():
    """Test comprehensive executive dashboard generation"""
    print("\n" + "="*60)
    print("TEST 5: Executive Dashboard Summary")
    print("="*60 + "\n")
    
    # Combine all data sources
    user_data = {"total_users": 1250, "avg_safety_score": 87.3, "engagement_rate": 75.0}
    rider_data = {"active_riders": 72, "avg_efficiency": 87.5, "on_time_rate": 92.3}
    feedback_data = {"avg_rating": 4.3, "positive_sentiment": 68.5, "response_rate": 85.0}
    ml_data = {"accuracy": 91.5, "successful_optimizations": 13890, "satisfaction_impact": 12.3}
    
    try:
        summarizer = ReportSummarizer(provider="openai")
        
        print("Generating comprehensive AI summary... (this may take 15-20 seconds)")
        summary = summarizer.generate_executive_dashboard_summary(
            user_data, rider_data, feedback_data, ml_data
        )
        
        print("\n✅ Executive Summary Generated Successfully!\n")
        print(f"Report Type: {summary['report_type']}")
        print(f"Data Sources: {', '.join(summary['data_sources'])}")
        print(f"\n{'-'*60}\n")
        print(summary['summary'])
        print(f"\n{'-'*60}\n")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_output_formats():
    """Test different output formats"""
    print("\n" + "="*60)
    print("TEST 6: Output Format Testing")
    print("="*60 + "\n")
    
    user_data = {
        "total_users": 1250,
        "new_users": 180,
        "avg_safety_score": 87.3
    }
    
    try:
        summarizer = ReportSummarizer(provider="openai")
        formatter = ReportFormatter()
        
        print("Generating summary...")
        summary = summarizer.summarize_user_report(user_data, time_period="weekly")
        
        # Test Markdown format
        print("\n📄 MARKDOWN FORMAT:")
        print("-" * 60)
        markdown = formatter.to_markdown(summary)
        print(markdown[:300] + "...\n")
        
        # Test HTML format
        print("🌐 HTML FORMAT:")
        print("-" * 60)
        html = formatter.to_html(summary)
        print(html[:300] + "...\n")
        
        # Test JSON format
        print("📊 JSON FORMAT:")
        print("-" * 60)
        json_output = formatter.to_json(summary)
        print(json_output[:300] + "...\n")
        
        print("✅ All formats generated successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*60)
    print("🧪 AI REPORT SUMMARIZER - TEST SUITE")
    print("="*60)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  WARNING: OPENAI_API_KEY not found in environment variables")
        print("Please set your API key in the .env file to run tests.\n")
        return
    
    tests = [
        ("User Report Summary", test_user_report_summary),
        ("Rider Report Summary", test_rider_report_summary),
        ("Feedback Report Summary", test_feedback_report_summary),
        ("ML Performance Summary", test_ml_performance_summary),
        ("Executive Dashboard", test_executive_dashboard),
        ("Output Formats", test_output_formats)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'-'*60}")
    print(f"Total: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print(f"{'-'*60}\n")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run all tests
    run_all_tests()
