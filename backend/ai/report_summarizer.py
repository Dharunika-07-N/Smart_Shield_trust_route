"""
AI-Powered Report Summarizer for Smart Shield
Generates intelligent summaries from ML models, user data, and feedback
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai


class ReportSummarizer:
    """
    Generates AI-powered summaries for various report types
    Supports multiple LLM providers: OpenAI, Anthropic, Google Gemini
    """
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize the summarizer with specified AI provider
        
        Args:
            provider: 'openai', 'anthropic', or 'gemini'
        """
        self.provider = provider.lower()
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.model = "gpt-4-turbo-preview"
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            self.model = "claude-3-sonnet-20240229"
        elif self.provider == "gemini":
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _generate_summary(self, prompt: str, system_context: str = None) -> str:
        """
        Generate summary using the configured LLM provider
        
        Args:
            prompt: The main prompt with data to summarize
            system_context: System-level instructions for the AI
            
        Returns:
            Generated summary text
        """
        try:
            if self.provider == "openai":
                messages = []
                if system_context:
                    messages.append({"role": "system", "content": system_context})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,  # Lower temperature for more factual summaries
                    max_tokens=1500
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    temperature=0.3,
                    system=system_context or "",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif self.provider == "gemini":
                full_prompt = f"{system_context}\n\n{prompt}" if system_context else prompt
                response = self.model.generate_content(full_prompt)
                return response.text
                
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def summarize_user_report(self, user_data: Dict[str, Any], 
                             time_period: str = "weekly") -> Dict[str, str]:
        """
        Generate comprehensive user activity summary
        
        Args:
            user_data: Dictionary containing user metrics and activity data
            time_period: 'daily', 'weekly', or 'monthly'
            
        Returns:
            Dictionary with different summary formats
        """
        system_context = """You are an expert healthcare analytics assistant for Smart Shield.
        Analyze user behavior data and provide clear, actionable insights.
        Focus on: usage patterns, safety metrics, engagement levels, and recommendations.
        Be concise but comprehensive."""
        
        prompt = f"""
Analyze the following {time_period} user report data and provide a comprehensive summary:

**User Metrics:**
- Total Active Users: {user_data.get('total_users', 0)}
- New Users: {user_data.get('new_users', 0)}
- Returning Users: {user_data.get('returning_users', 0)}
- Average Session Duration: {user_data.get('avg_session_duration', 0)} minutes
- Total Requests: {user_data.get('total_requests', 0)}

**Safety Metrics:**
- Safe Routes Taken: {user_data.get('safe_routes', 0)}
- Emergency Alerts: {user_data.get('emergency_alerts', 0)}
- Safety Score (Avg): {user_data.get('avg_safety_score', 0)}/100

**Engagement:**
- Hospital Searches: {user_data.get('hospital_searches', 0)}
- Route Optimizations: {user_data.get('route_optimizations', 0)}
- Feedback Submitted: {user_data.get('feedback_count', 0)}

**Top Features Used:**
{json.dumps(user_data.get('top_features', []), indent=2)}

Provide:
1. **Executive Summary** (2-3 sentences)
2. **Key Insights** (3-5 bullet points)
3. **Trends & Patterns** (2-3 observations)
4. **Recommendations** (2-3 actionable items)
5. **Alerts** (Any concerning patterns)
"""
        
        summary = self._generate_summary(prompt, system_context)
        
        return {
            "summary": summary,
            "generated_at": datetime.now().isoformat(),
            "time_period": time_period,
            "data_points": len(user_data),
            "provider": self.provider
        }
    
    def summarize_rider_report(self, rider_data: Dict[str, Any],
                               time_period: str = "weekly") -> Dict[str, str]:
        """
        Generate rider performance summary from ML model outputs
        
        Args:
            rider_data: Dictionary containing rider metrics and route data
            time_period: 'daily', 'weekly', or 'monthly'
            
        Returns:
            Dictionary with performance summary
        """
        system_context = """You are an expert logistics and route optimization analyst for Smart Shield.
        Analyze rider performance data from ML models and provide actionable insights.
        Focus on: efficiency, safety compliance, route optimization, and improvement areas."""
        
        prompt = f"""
Analyze the following {time_period} rider performance report:

**Performance Metrics:**
- Total Riders: {rider_data.get('total_riders', 0)}
- Active Riders: {rider_data.get('active_riders', 0)}
- Total Routes Completed: {rider_data.get('routes_completed', 0)}
- Average Route Efficiency: {rider_data.get('avg_efficiency', 0)}%
- On-Time Delivery Rate: {rider_data.get('on_time_rate', 0)}%

**ML Model Insights:**
- RL Agent Optimization Success Rate: {rider_data.get('rl_success_rate', 0)}%
- Average Route Time Saved: {rider_data.get('avg_time_saved', 0)} minutes
- Safety Violations: {rider_data.get('safety_violations', 0)}
- Fuel Efficiency Improvement: {rider_data.get('fuel_improvement', 0)}%

**Route Analysis:**
- Total Distance Covered: {rider_data.get('total_distance', 0)} km
- Average Distance per Route: {rider_data.get('avg_distance', 0)} km
- Peak Hours Performance: {rider_data.get('peak_performance', 'N/A')}

**Top Performers:**
{json.dumps(rider_data.get('top_riders', []), indent=2)}

**Issues Detected:**
{json.dumps(rider_data.get('issues', []), indent=2)}

Provide:
1. **Executive Summary** (2-3 sentences)
2. **Performance Highlights** (3-5 key achievements)
3. **ML Model Impact** (How AI improved operations)
4. **Areas for Improvement** (2-3 specific recommendations)
5. **Risk Alerts** (Any safety or efficiency concerns)
"""
        
        summary = self._generate_summary(prompt, system_context)
        
        return {
            "summary": summary,
            "generated_at": datetime.now().isoformat(),
            "time_period": time_period,
            "ml_model_version": rider_data.get('model_version', 'unknown'),
            "provider": self.provider
        }
    
    def summarize_feedback_report(self, feedback_data: Dict[str, Any],
                                  time_period: str = "weekly") -> Dict[str, str]:
        """
        Generate feedback analysis summary with sentiment insights
        
        Args:
            feedback_data: Dictionary containing feedback metrics and comments
            time_period: 'daily', 'weekly', or 'monthly'
            
        Returns:
            Dictionary with feedback analysis
        """
        system_context = """You are an expert customer experience analyst for Smart Shield.
        Analyze user feedback data and extract meaningful insights.
        Focus on: sentiment trends, common issues, feature requests, and user satisfaction."""
        
        prompt = f"""
Analyze the following {time_period} feedback report:

**Feedback Metrics:**
- Total Feedback Received: {feedback_data.get('total_feedback', 0)}
- Average Rating: {feedback_data.get('avg_rating', 0)}/5.0
- Response Rate: {feedback_data.get('response_rate', 0)}%

**Sentiment Analysis:**
- Positive: {feedback_data.get('positive_sentiment', 0)}%
- Neutral: {feedback_data.get('neutral_sentiment', 0)}%
- Negative: {feedback_data.get('negative_sentiment', 0)}%

**Category Breakdown:**
{json.dumps(feedback_data.get('categories', {}), indent=2)}

**Top Issues Reported:**
{json.dumps(feedback_data.get('top_issues', []), indent=2)}

**Feature Requests:**
{json.dumps(feedback_data.get('feature_requests', []), indent=2)}

**Sample Comments:**
{json.dumps(feedback_data.get('sample_comments', []), indent=2)}

**Trend Comparison:**
- Previous Period Rating: {feedback_data.get('previous_rating', 0)}/5.0
- Rating Change: {feedback_data.get('rating_change', 0)}

Provide:
1. **Executive Summary** (2-3 sentences)
2. **Sentiment Overview** (Overall user satisfaction analysis)
3. **Critical Issues** (Top 3 problems to address immediately)
4. **Positive Highlights** (What users love)
5. **Actionable Recommendations** (3-5 specific improvements)
6. **Trend Analysis** (How feedback is changing over time)
"""
        
        summary = self._generate_summary(prompt, system_context)
        
        return {
            "summary": summary,
            "generated_at": datetime.now().isoformat(),
            "time_period": time_period,
            "sentiment_score": feedback_data.get('avg_rating', 0),
            "provider": self.provider
        }
    
    def summarize_ml_model_performance(self, model_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate ML model performance summary
        
        Args:
            model_data: Dictionary containing model metrics and performance data
            
        Returns:
            Dictionary with model performance summary
        """
        system_context = """You are an expert ML engineer analyzing model performance for Smart Shield.
        Provide technical yet understandable insights about model accuracy, efficiency, and improvements.
        Focus on: prediction accuracy, training metrics, real-world impact, and optimization suggestions."""
        
        prompt = f"""
Analyze the following ML model performance data:

**Model Information:**
- Model Type: {model_data.get('model_type', 'Unknown')}
- Version: {model_data.get('version', 'N/A')}
- Last Trained: {model_data.get('last_trained', 'N/A')}
- Training Duration: {model_data.get('training_duration', 0)} minutes

**Performance Metrics:**
- Accuracy: {model_data.get('accuracy', 0)}%
- Precision: {model_data.get('precision', 0)}%
- Recall: {model_data.get('recall', 0)}%
- F1 Score: {model_data.get('f1_score', 0)}
- Loss: {model_data.get('loss', 0)}

**Real-World Impact:**
- Total Predictions Made: {model_data.get('total_predictions', 0)}
- Successful Optimizations: {model_data.get('successful_optimizations', 0)}
- Average Improvement: {model_data.get('avg_improvement', 0)}%
- User Satisfaction Impact: {model_data.get('satisfaction_impact', 0)}%

**Resource Usage:**
- Inference Time (avg): {model_data.get('avg_inference_time', 0)} ms
- Memory Usage: {model_data.get('memory_usage', 0)} MB
- API Calls: {model_data.get('api_calls', 0)}

**Comparison with Previous Version:**
{json.dumps(model_data.get('version_comparison', {}), indent=2)}

Provide:
1. **Executive Summary** (2-3 sentences for non-technical stakeholders)
2. **Technical Performance** (Detailed metrics analysis)
3. **Real-World Impact** (How the model helps users)
4. **Optimization Opportunities** (2-3 improvement suggestions)
5. **Deployment Recommendations** (Should we deploy, retrain, or optimize?)
"""
        
        summary = self._generate_summary(prompt, system_context)
        
        return {
            "summary": summary,
            "generated_at": datetime.now().isoformat(),
            "model_version": model_data.get('version', 'unknown'),
            "performance_score": model_data.get('accuracy', 0),
            "provider": self.provider
        }
    
    def generate_executive_dashboard_summary(self, 
                                            user_data: Dict,
                                            rider_data: Dict,
                                            feedback_data: Dict,
                                            ml_data: Dict) -> Dict[str, str]:
        """
        Generate a comprehensive executive summary combining all reports
        
        Args:
            user_data: User metrics
            rider_data: Rider performance data
            feedback_data: Feedback analysis
            ml_data: ML model performance
            
        Returns:
            Comprehensive executive summary
        """
        system_context = """You are a senior healthcare technology analyst providing executive briefings.
        Synthesize multiple data sources into a clear, strategic overview for C-level executives.
        Focus on: business impact, strategic insights, ROI, and high-level recommendations."""
        
        prompt = f"""
Create a comprehensive executive summary for Smart Shield platform:

**USER ACTIVITY:**
- Active Users: {user_data.get('total_users', 0)}
- Safety Score: {user_data.get('avg_safety_score', 0)}/100
- Engagement Rate: {user_data.get('engagement_rate', 0)}%

**RIDER OPERATIONS:**
- Active Riders: {rider_data.get('active_riders', 0)}
- Route Efficiency: {rider_data.get('avg_efficiency', 0)}%
- On-Time Rate: {rider_data.get('on_time_rate', 0)}%

**USER SATISFACTION:**
- Average Rating: {feedback_data.get('avg_rating', 0)}/5.0
- Positive Sentiment: {feedback_data.get('positive_sentiment', 0)}%
- Response Rate: {feedback_data.get('response_rate', 0)}%

**AI/ML PERFORMANCE:**
- Model Accuracy: {ml_data.get('accuracy', 0)}%
- Optimization Success: {ml_data.get('successful_optimizations', 0)}
- User Impact: {ml_data.get('satisfaction_impact', 0)}% improvement

Provide:
1. **Executive Summary** (3-4 sentences - the big picture)
2. **Key Wins** (Top 3 achievements this period)
3. **Strategic Insights** (2-3 business-critical observations)
4. **Challenges & Risks** (Top 2 concerns)
5. **Strategic Recommendations** (3 high-impact actions)
6. **ROI Highlights** (Quantifiable business value)
"""
        
        summary = self._generate_summary(prompt, system_context)
        
        return {
            "summary": summary,
            "generated_at": datetime.now().isoformat(),
            "report_type": "executive_dashboard",
            "provider": self.provider,
            "data_sources": ["users", "riders", "feedback", "ml_models"]
        }


class ReportFormatter:
    """
    Formats AI-generated summaries into various output formats
    """
    
    @staticmethod
    def to_markdown(summary_data: Dict[str, str]) -> str:
        """Convert summary to Markdown format"""
        md = f"""# Smart Shield Report Summary
        
**Generated:** {summary_data.get('generated_at', 'N/A')}  
**Period:** {summary_data.get('time_period', 'N/A')}  
**AI Provider:** {summary_data.get('provider', 'N/A')}

---

{summary_data.get('summary', 'No summary available')}

---

*Generated by Smart Shield AI Report Summarizer*
"""
        return md
    
    @staticmethod
    def to_html(summary_data: Dict[str, str]) -> str:
        """Convert summary to HTML format"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Smart Shield Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .metadata {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary {{ line-height: 1.6; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #bdc3c7; color: #7f8c8d; }}
    </style>
</head>
<body>
    <h1>Smart Shield Report Summary</h1>
    <div class="metadata">
        <strong>Generated:</strong> {summary_data.get('generated_at', 'N/A')}<br>
        <strong>Period:</strong> {summary_data.get('time_period', 'N/A')}<br>
        <strong>AI Provider:</strong> {summary_data.get('provider', 'N/A')}
    </div>
    <div class="summary">
        {summary_data.get('summary', 'No summary available').replace('\n', '<br>')}
    </div>
    <div class="footer">
        <em>Generated by Smart Shield AI Report Summarizer</em>
    </div>
</body>
</html>
"""
        return html
    
    @staticmethod
    def to_json(summary_data: Dict[str, str]) -> str:
        """Convert summary to JSON format"""
        return json.dumps(summary_data, indent=2)


# Example usage
if __name__ == "__main__":
    # Initialize summarizer
    summarizer = ReportSummarizer(provider="openai")
    
    # Example user data
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
        "top_features": ["Hospital Search", "Route Optimization", "Emergency Alert"]
    }
    
    # Generate summary
    summary = summarizer.summarize_user_report(user_data, time_period="weekly")
    
    # Format as markdown
    formatter = ReportFormatter()
    markdown_report = formatter.to_markdown(summary)
    print(markdown_report)
