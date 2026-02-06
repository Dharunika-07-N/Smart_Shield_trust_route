"""
Generative AI Service for Smart Shield
Integrates OpenAI GPT models for enhanced feedback analysis and safety recommendations
"""
import openai
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from loguru import logger
from functools import lru_cache
import hashlib

class GenAIService:
    """Service for integrating Generative AI capabilities"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

        if not self.api_key:
            logger.warning("OpenAI API key not found. GenAI features will be disabled.")
            self.enabled = False
        else:
            openai.api_key = self.api_key
            self.enabled = True
            logger.info(f"GenAI service initialized with model: {self.model}")

    async def analyze_feedback_sentiment(self, feedback_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze rider feedback using GPT to extract safety concerns and sentiment

        Args:
            feedback_text: Raw feedback text from rider
            context: Additional context (route_id, time, location, etc.)

        Returns:
            Dict containing sentiment analysis, safety concerns, and recommendations
        """
        if not self.enabled:
            return self._fallback_sentiment_analysis(feedback_text, context)

        try:
            prompt = f"""
            Analyze this delivery rider feedback for safety concerns and sentiment.
            Provide a structured analysis in JSON format.

            Feedback: "{feedback_text}"

            Context:
            - Time: {context.get('time', 'Unknown')}
            - Location: {context.get('location', 'Unknown')}
            - Route ID: {context.get('route_id', 'Unknown')}

            Return JSON with:
            {{
                "sentiment": "positive/negative/neutral",
                "safety_concerns": ["list", "of", "concerns"],
                "severity_level": "low/medium/high/critical",
                "recommendations": ["actionable", "recommendations"],
                "categories": ["safety", "traffic", "service", "other"]
            }}
            """

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
            )

            result = json.loads(response.choices[0].message.content.strip())
            result["analyzed_at"] = datetime.utcnow().isoformat()
            result["ai_model"] = self.model

            logger.info(f"AI feedback analysis completed for route {context.get('route_id')}")
            return result

        except Exception as e:
            logger.error(f"AI feedback analysis failed: {e}")
            return self._fallback_sentiment_analysis(feedback_text, context)

    async def generate_safety_briefing(self, route_data: Dict[str, Any], rider_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized safety briefing for riders before route start

        Args:
            route_data: Route details (stops, time, distance, safety scores)
            rider_profile: Rider information (experience, gender, preferences)

        Returns:
            Dict containing safety tips, risk areas, and emergency contacts
        """
        if not self.enabled:
            return self._fallback_safety_briefing(route_data, rider_profile)

        try:
            prompt = f"""
            Generate a personalized safety briefing for a delivery rider.

            Route Details:
            - Distance: {route_data.get('distance_km', 0)} km
            - Duration: {route_data.get('duration_minutes', 0)} minutes
            - Start Time: {route_data.get('start_time', 'Unknown')}
            - Safety Score: {route_data.get('safety_score', 50)}/100
            - High-risk areas: {', '.join(route_data.get('high_risk_areas', []))}

            Rider Profile:
            - Experience: {rider_profile.get('experience_months', 0)} months
            - Gender: {rider_profile.get('gender', 'Unknown')}
            - Previous incidents: {rider_profile.get('incident_count', 0)}

            Generate a concise safety briefing with:
            1. Key safety tips
            2. Emergency contacts
            3. Risk mitigation strategies
            4. What to do in case of emergency

            Keep it under 300 words, practical and reassuring.
            """

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3  # Lower temperature for safety content
                )
            )

            briefing_text = response.choices[0].message.content.strip()

            return {
                "briefing": briefing_text,
                "generated_at": datetime.utcnow().isoformat(),
                "ai_model": self.model,
                "personalized": True
            }

        except Exception as e:
            logger.error(f"AI safety briefing generation failed: {e}")
            return self._fallback_safety_briefing(route_data, rider_profile)

    async def optimize_route_with_ai(self, route_options: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to analyze multiple route options and recommend the best one

        Args:
            route_options: List of route alternatives with metrics
            constraints: User preferences (safety priority, time limits, etc.)

        Returns:
            Dict with AI-recommended route and reasoning
        """
        if not self.enabled:
            return self._fallback_route_optimization(route_options, constraints)

        try:
            routes_text = "\n".join([
                f"Route {i+1}: {r.get('distance_km', 0)}km, {r.get('duration_min', 0)}min, "
                f"Safety: {r.get('safety_score', 50)}/100, Traffic: {r.get('traffic_level', 'unknown')}"
                for i, r in enumerate(route_options)
            ])

            prompt = f"""
            Analyze these delivery route options and recommend the best one.

            Available Routes:
            {routes_text}

            Constraints:
            - Safety Priority: {constraints.get('safety_priority', 'medium')} (low/medium/high)
            - Max Time: {constraints.get('max_time_minutes', 'unlimited')} minutes
            - Rider Experience: {constraints.get('rider_experience', 'unknown')}
            - Time of Day: {constraints.get('time_of_day', 'daytime')}

            Consider:
            1. Safety first for night routes or inexperienced riders
            2. Time efficiency during peak hours
            3. Traffic conditions
            4. Distance optimization

            Return JSON with:
            {{
                "recommended_route_index": 0,
                "reasoning": "detailed explanation",
                "trade_offs": "what's gained/lost vs other options",
                "confidence_score": 0.85
            }}
            """

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=0.2  # Lower temperature for decision-making
                )
            )

            result = json.loads(response.choices[0].message.content.strip())
            result["analyzed_at"] = datetime.utcnow().isoformat()
            result["ai_model"] = self.model

            return result

        except Exception as e:
            logger.error(f"AI route optimization failed: {e}")
            return self._fallback_route_optimization(route_options, constraints)

    def _fallback_sentiment_analysis(self, feedback_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback sentiment analysis when AI is unavailable"""
        # Simple keyword-based analysis
        text_lower = feedback_text.lower()
        safety_keywords = ['unsafe', 'danger', 'scary', 'attack', 'harassment', 'accident']
        positive_keywords = ['safe', 'good', 'great', 'excellent', 'fine']

        has_safety_concerns = any(keyword in text_lower for keyword in safety_keywords)
        has_positive = any(keyword in text_lower for keyword in positive_keywords)

        if has_safety_concerns:
            sentiment = "negative"
            severity = "high" if 'attack' in text_lower or 'harassment' in text_lower else "medium"
        elif has_positive:
            sentiment = "positive"
            severity = "low"
        else:
            sentiment = "neutral"
            severity = "low"

        return {
            "sentiment": sentiment,
            "safety_concerns": ["AI analysis unavailable - manual review recommended"] if has_safety_concerns else [],
            "severity_level": severity,
            "recommendations": ["Review feedback manually", "Monitor route safety"],
            "categories": ["safety"] if has_safety_concerns else ["other"],
            "fallback": True,
            "analyzed_at": datetime.utcnow().isoformat()
        }

    def _fallback_safety_briefing(self, route_data: Dict[str, Any], rider_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback safety briefing when AI is unavailable"""
        return {
            "briefing": "Standard Safety Guidelines:\n1. Stay alert and aware of surroundings\n2. Keep emergency contacts handy\n3. Report any unsafe areas immediately\n4. Follow traffic rules at all times",
            "generated_at": datetime.utcnow().isoformat(),
            "personalized": False,
            "fallback": True
        }

    def _fallback_route_optimization(self, route_options: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback route optimization when AI is unavailable"""
        # Simple rule-based selection
        safety_priority = constraints.get('safety_priority', 'medium')

        if safety_priority == 'high':
            # Choose safest route
            best_idx = max(range(len(route_options)),
                          key=lambda i: route_options[i].get('safety_score', 50))
        else:
            # Choose fastest route
            best_idx = min(range(len(route_options)),
                          key=lambda i: route_options[i].get('duration_min', 60))

        return {
            "recommended_route_index": best_idx,
            "reasoning": f"Fallback selection based on {safety_priority} priority",
            "trade_offs": "AI analysis unavailable",
            "confidence_score": 0.5,
            "fallback": True,
            "analyzed_at": datetime.utcnow().isoformat()
        }

    @lru_cache(maxsize=100)
    def _get_cache_key(self, content: str, context: str) -> str:
        """Generate cache key for AI responses"""
        combined = f"{content}:{context}"
        return hashlib.md5(combined.encode()).hexdigest()
