"""Route Optimization Engine."""
import networkx as nx
from typing import List, Dict, Tuple, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
import uuid

# Optional: OR-Tools for advanced optimization
try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    HAS_ORTOOLS = True
except ImportError:
    HAS_ORTOOLS = False

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import settings
from api.schemas.delivery import Coordinate, DeliveryStop
from loguru import logger

# Use FREE OSRM service instead of Google Maps (no API key needed!)
try:
    from api.services.osrm_service import OSRMService
    USE_OSRM = True
    logger.info("Using FREE OSRM service (no API key required)")
except ImportError:
    from api.services.maps import MapsService
    USE_OSRM = False
    logger.warning("OSRM not available, falling back to MapsService")

from api.models.safety_scorer import SafetyScorer
from api.services.weather import WeatherService
from api.services.traffic import TrafficService

# A* Algorithm
try:
    from api.models.astar_optimizer import AStarRouteOptimizer
    HAS_ASTAR = True
    logger.info("A* Algorithm available")
except ImportError:
    HAS_ASTAR = False
    logger.warning("A* Algorithm not available")

# Renovation ML Models
try:
    from ml.feature_engineer import FeatureEngineer
    from ml.time_predictor import DeliveryTimePredictor
    from ml.safety_classifier import SafetyClassifier
    from ml.rl_agent import SARSARouteAgent
    HAS_RENOVATION_ML = True
except ImportError:
    HAS_RENOVATION_ML = False

from database.database import SessionLocal
from loguru import logger
import asyncio


class RouteOptimizer:
    """Multi-objective route optimization engine."""
    
    def __init__(self):
        # Use FREE OSRM service (no API key, no billing!)
        if USE_OSRM:
            self.maps_service = OSRMService()
        else:
            self.maps_service = MapsService()
        
        self.safety_scorer = SafetyScorer()
        self.weather_service = WeatherService()
        self.traffic_service = TrafficService()
        
        # Initialize A* optimizer
        if HAS_ASTAR:
            self.astar_optimizer = AStarRouteOptimizer(
                weight_distance=0.3,
                weight_time=0.3,
                weight_safety=0.25,
                weight_traffic=0.15
            )
        
        # Initialize Renovation ML components
        if HAS_RENOVATION_ML:
            self.feature_engineer = FeatureEngineer(None)
            self.time_predictor = DeliveryTimePredictor()
            self.safety_classifier = SafetyClassifier()
            self.rl_agent = SARSARouteAgent()
            # Load models if they exist
            self.time_predictor.load_model()
            self.safety_classifier.load_model()
            self.rl_agent.load_model()
        
        from database.models import CrowdsourcedAlert
        self.AlertModel = CrowdsourcedAlert

    
    async def optimize_route(
        self,
        starting_point: Coordinate,
        stops: List[DeliveryStop],
        optimize_for: List[str] = ["time", "distance"],
        rider_info: Optional[Dict] = None,
        vehicle_type: str = "motorcycle",
        departure_time: Optional[datetime] = None
    ) -> Dict:
        """Optimize delivery route with multiple objectives.
        
        Args:
            starting_point: Starting location
            stops: List of delivery stops
            optimize_for: Objectives (time, distance, fuel, safety)
            rider_info: Rider information for safety optimization
            vehicle_type: Type of vehicle
            departure_time: When the route starts
        
        Returns:
            OptimizedRoute with sequence, distances, times, etc.
        """
        if not stops:
            raise ValueError("No stops provided")
        
        # Phase 4: Clustering & Batching
        if len(stops) > 10: # Only cluster if many stops
            logger.info("Performing proximity-based clustering for batching")
            stops = self._cluster_stops(stops, max_distance_meters=2000)

        # Phase 4: Capacity Planning
        if rider_info and (rider_info.get("max_weight") or rider_info.get("max_capacity")):
            max_weight = rider_info.get("max_weight", float('inf'))
            max_capacity = rider_info.get("max_capacity", float('inf'))
            
            total_weight = sum(s.package_weight or 0 for s in stops)
            total_count = len(stops)
            
            if total_weight > max_weight or total_count > max_capacity:
                 logger.warning(f"Batch exceeds capacity: Weight {total_weight}/{max_weight}, Count {total_count}/{max_capacity}")
                 # In production, would split into multiple routes
        
        logger.info(f"Optimizing route for {len(stops)} stops, objectives: {optimize_for}")

        
        # Prepare data
        all_points = [starting_point] + [stop.coordinates for stop in stops]
        
        # Fetch active crowdsourced alerts (last 4 hours)
        active_alerts = []
        try:
            db = SessionLocal()
            cutoff = datetime.utcnow() - timedelta(hours=4)
            active_alerts = db.query(self.AlertModel).filter(self.AlertModel.created_at >= cutoff).all()
            db.close()
            logger.info(f"Fetched {len(active_alerts)} active crowdsourced alerts for optimization")
        except Exception as e:
            logger.warning(f"Could not fetch crowdsourced alerts: {e}")

        # Create distance matrix
        distance_matrix = self._create_distance_matrix(all_points)
        
        # Create cost matrix based on objectives
        cost_matrix = self._create_cost_matrix(
            all_points,
            distance_matrix,
            optimize_for,
            rider_info,
            stops,
            departure_time,
            active_alerts
        )
        
        # Optimize using multiple algorithms
        if len(stops) == 1:
            # For finding alternatives between A and B
            return await self._optimize_single_leg_alternatives(
                starting_point,
                stops[0],
                optimize_for,
                rider_info,
                departure_time
            )
        elif settings.OPTIMIZATION_ALGORITHM == "astar" and HAS_ASTAR:
            # Use A* algorithm for optimal pathfinding
            logger.info("Using A* algorithm for route optimization")
            sequence = self._optimize_astar(starting_point, stops, rider_info, departure_time)
        elif settings.OPTIMIZATION_ALGORITHM == "genetic":
            sequence = self._optimize_genetic(cost_matrix, len(stops))
        elif settings.OPTIMIZATION_ALGORITHM == "nearest_neighbor":
            sequence = self._optimize_nearest_neighbor(cost_matrix)
        elif HAS_ORTOOLS and settings.OPTIMIZATION_ALGORITHM != "nearest_neighbor":
            # Use OR-Tools for hybrid optimization if available
            sequence = self._optimize_ortools(cost_matrix, len(stops))
        else:
            # Fallback to nearest neighbor if OR-Tools not available
            sequence = self._optimize_nearest_neighbor(cost_matrix)
        
        # Build route segments
        segments, total_stats = await self._build_route_segments(
            starting_point,
            stops,
            sequence,
            optimize_for,
            rider_info,
            departure_time
        )
        
        # Generate unique route ID
        route_id = f"ROUTE_{uuid.uuid4().hex[:10]}"
        
        # Estimate arrivals
        estimated_arrivals = self._calculate_arrivals(
            starting_point,
            stops,
            sequence,
            segments,
            departure_time
        )
        
        return {
            "route_id": route_id,
            "sequence": [stops[i].stop_id for i in sequence],
            "segments": segments,
            "total_distance_meters": total_stats["distance"],
            "total_duration_seconds": total_stats["duration"],
            "average_safety_score": total_stats["avg_safety"],
            "total_fuel_liters": total_stats["fuel"],
            "optimizations_applied": optimize_for,
            "estimated_arrivals": estimated_arrivals,
            "created_at": datetime.now()
        }
    
    def _create_distance_matrix(self, points: List[Coordinate]) -> List[List[float]]:
        """Create distance matrix between all points."""
        n = len(points)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    distance = self.maps_service.calculate_straight_distance(
                        points[i], points[j]
                    )
                    matrix[i][j] = distance
        
        return matrix
    
    def _create_cost_matrix(
        self,
        points: List[Coordinate],
        distance_matrix: List[List[float]],
        objectives: List[str],
        rider_info: Optional[Dict],
        stops: List[DeliveryStop],
        departure_time: Optional[datetime] = None,
        active_alerts: List = []
    ) -> List[List[float]]:
        """Create weighted cost matrix based on objectives."""
        n = len(points)
        cost_matrix = [[0.0] * n for _ in range(n)]
        
        # Determine time of day and night mode
        time_of_day = "day"
        night_mode = False
        if departure_time:
            hour = departure_time.hour
            if hour < 6 or hour >= 22:
                time_of_day = "night"
                night_mode = True
            elif hour < 8 or hour >= 18:
                time_of_day = "evening"
        
        # Check if night mode is explicitly requested
        if rider_info and rider_info.get("night_mode"):
            night_mode = True
            time_of_day = "night"
        
        # Get safety scores for all segments
        safety_matrix = [[1.0] * n for _ in range(n)]
        lighting_matrix = [[50.0] * n for _ in range(n)]  # Default lighting score
        
        if "safety" in objectives or night_mode:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        # Get safety score for segment
                        segment_coords = [points[i], points[j]]
                        safety_data = self.safety_scorer.score_route(segment_coords, time_of_day, rider_info)
                        
                        # Extract lighting score from safety factors
                        lighting_score = 50.0  # Default
                        if safety_data.get("segment_scores"):
                            for seg in safety_data["segment_scores"]:
                                factors = seg.get("factors", [])
                                for factor in factors:
                                    if factor.get("name") == "lighting":
                                        lighting_score = factor.get("score", 50.0)
                                        break
                        
                        lighting_matrix[i][j] = lighting_score
                        
                        # In night mode, heavily penalize low lighting
                        if night_mode:
                            # Inverse lighting score (higher lighting = lower cost)
                            # Heavily weight lighting in night mode
                            lighting_penalty = (100 - lighting_score) * 2.0  # 2x penalty for low lighting
                            safety_matrix[i][j] = (100 - safety_data["route_safety_score"]) + lighting_penalty
                        else:
                            # Normal safety scoring
                            safety_matrix[i][j] = 100 - safety_data["route_safety_score"]
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    cost_matrix[i][j] = 0
                else:
                    cost = 0
                    
                    # Distance-based cost
                    if "distance" in objectives:
                        cost += distance_matrix[i][j] / 1000.0  # km
                    
                    # Time-based cost
                    if "time" in objectives:
                        # Assume average speed of 30 km/h
                        time_cost = distance_matrix[i][j] / 8.33 / 60  # minutes
                        cost += time_cost * 0.1
                    
                    # Fuel cost
                    if "fuel" in objectives:
                        fuel_liters = distance_matrix[i][j] / 1000 * settings.FUEL_CONSUMPTION_PER_KM
                        cost += fuel_liters * 10  # Assuming fuel is expensive
                    
                    # Safety cost (for women riders or night deliveries)
                    if "safety" in objectives or night_mode:
                        safety_cost = safety_matrix[i][j] / 100.0
                        # In night mode, increase safety weight significantly
                        if night_mode:
                            safety_cost *= 3.0  # 3x weight for safety in night mode
                        cost += safety_cost
                    
                    # Traffic cost (considering current traffic conditions)
                    if "traffic" in objectives or "time" in objectives:
                        try:
                            traffic_level, _, traffic_duration = self.traffic_service.get_traffic_level(
                                points[i], points[j]
                            )
                            # Add traffic penalty to cost
                            if traffic_level == 'high':
                                cost += traffic_duration / 60.0 * 0.3  # 30% penalty for high traffic
                            elif traffic_level == 'medium':
                                cost += traffic_duration / 60.0 * 0.15  # 15% penalty
                        except Exception as e:
                            logger.warning(f"Could not get traffic data: {e}")
                    
                    # Crowdsourced feedback adjustment
                    if active_alerts:
                        for alert in active_alerts:
                            # Check if alert is near this segment
                            # Simple check: distance to start or end points
                            dist_to_start = self.maps_service.calculate_straight_distance(
                                points[i], Coordinate(latitude=alert.location['lat'], longitude=alert.location['lng'])
                            )
                            if dist_to_start < 500: # 500 meters
                                if alert.has_traffic_issues:
                                    cost += 5.0 # Significant penalty for reported traffic
                                    logger.info(f"Applying traffic penalty for alert near node {i}")
                                if alert.is_faster:
                                    cost -= 2.0 # Bonus for reputed fast route
                                    logger.info(f"Applying speed bonus for alert near node {i}")

                    cost_matrix[i][j] = cost
        
        return cost_matrix
    
    def _optimize_ortools(
        self,
        cost_matrix: List[List[float]],
        num_stops: int
    ) -> List[int]:
        """Optimize using OR-Tools (TSP solver)."""
        try:
            # Convert to distance matrix (integers for OR-Tools)
            manager = pywrapcp.RoutingIndexManager(
                num_stops + 1,  # +1 for depot
                1,  # number of vehicles
                0  # depot index
            )
            
            routing = pywrapcp.RoutingModel(manager)
            
            def distance_callback(from_index, to_index):
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return int(cost_matrix[from_node][to_node] * 1000)
            
            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
            
            # Set search parameters
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            )
            search_parameters.time_limit.seconds = 5
            
            solution = routing.SolveWithParameters(search_parameters)
            
            if solution:
                index = routing.Start(0)
                route = []
                while not routing.IsEnd(index):
                    node = manager.IndexToNode(index)
                    if node > 0:  # Skip depot (node 0)
                        route.append(node - 1)  # Adjust for depot offset
                    index = solution.Value(routing.NextVar(index))
                return route
            
        except Exception as e:
            logger.warning(f"OR-Tools optimization failed: {e}, falling back to nearest neighbor")
        
        return self._optimize_nearest_neighbor(cost_matrix)
    
    def _optimize_nearest_neighbor(
        self,
        cost_matrix: List[List[float]]
    ) -> List[int]:
        """Greedy nearest neighbor optimization."""
        n = len(cost_matrix)
        if n <= 1:
            return []
        
        route = []
        visited = {0}  # Depot is always visited first
        
        current = 0
        while len(route) < n - 1:  # -1 because depot is not in route
            min_cost = float('inf')
            next_node = None
            
            for i in range(1, n):  # Skip depot (0)
                if i not in visited and cost_matrix[current][i] < min_cost:
                    min_cost = cost_matrix[current][i]
                    next_node = i
            
            if next_node is not None:
                route.append(next_node - 1)  # Adjust for depot offset
                visited.add(next_node)
                current = next_node
        
        return route

    def _optimize_astar(
        self,
        starting_point: Coordinate,
        stops: List[DeliveryStop],
        rider_info: Optional[Dict],
        departure_time: Optional[datetime]
    ) -> List[int]:
        """Optimize route using A* algorithm"""
        if not HAS_ASTAR:
            logger.warning("A* not available, falling back to nearest neighbor")
            return list(range(len(stops)))
        
        # Prepare safety and traffic data
        safety_data = {}
        traffic_data = {}
        
        # Get safety scores for all stop locations
        for stop in stops:
            coord = (stop.coordinates.latitude, stop.coordinates.longitude)
            safety_score, _ = self.safety_scorer.score_location(
                stop.coordinates,
                time_of_day="day" if departure_time and 6 <= departure_time.hour < 20 else "night",
                rider_info=rider_info
            )
            safety_data[coord] = safety_score
        
        # Get traffic data
        for stop in stops:
            coord = (stop.coordinates.latitude, stop.coordinates.longitude)
            try:
                traffic_level, _, _ = self.traffic_service.get_traffic_level(
                    starting_point, stop.coordinates
                )
                traffic_data[coord] = traffic_level
            except:
                traffic_data[coord] = 'medium'
        
        # Use A* to find optimal sequence
        # For multi-stop, we'll use A* to find best path through all stops
        sequence = []
        remaining_stops = list(range(len(stops)))
        current_pos = (starting_point.latitude, starting_point.longitude)
        
        while remaining_stops:
            best_idx = None
            best_cost = float('inf')
            
            for idx in remaining_stops:
                stop = stops[idx]
                goal = (stop.coordinates.latitude, stop.coordinates.longitude)
                
                # Use A* heuristic to estimate cost
                cost = self.astar_optimizer.heuristic(
                    current_pos,
                    goal,
                    safety_data,
                    traffic_data,
                    departure_time.hour if departure_time else None
                )
                
                if cost < best_cost:
                    best_cost = cost
                    best_idx = idx
            
            if best_idx is not None:
                sequence.append(best_idx)
                remaining_stops.remove(best_idx)
                current_pos = (stops[best_idx].coordinates.latitude, 
                             stops[best_idx].coordinates.longitude)
        
        logger.info(f"A* optimization complete: {len(sequence)} stops sequenced")
        return sequence
    
    def _cluster_stops(self, stops: List[DeliveryStop], max_distance_meters: float) -> List[DeliveryStop]:
        """Perform proximity-based clustering (simplified)."""
        if not stops: return []
        # In a real implementation, use K-means or DBSCAN
        # For now, we'll just sort them to group nearby ones
        sorted_stops = sorted(stops, key=lambda s: (s.coordinates.latitude, s.coordinates.longitude))
        return sorted_stops

    def _optimize_genetic(

        self,
        cost_matrix: List[List[float]],
        num_stops: int
    ) -> List[int]:
        """Genetic algorithm optimization (simplified)."""
        # For simplicity, use nearest neighbor with variations
        # In production, implement full GA with population, crossover, mutation
        return self._optimize_nearest_neighbor(cost_matrix)
    
    async def _build_route_segments(
        self,
        starting_point: Coordinate,
        stops: List[DeliveryStop],
        sequence: List[int],
        objectives: List[str],
        rider_info: Optional[Dict],
        departure_time: Optional[datetime] = None
    ) -> Tuple[List[Dict], Dict]:
        """Build route segments with statistics using traffic-aware directions."""
        segments = []
        total_distance = 0
        total_duration = 0
        total_safety = 0
        total_fuel = 0
        
        # Get departure timestamp for traffic-aware routing
        dep_timestamp = None
        if departure_time:
            dep_timestamp = int(departure_time.timestamp())
        
        # First segment: starting point to first stop
        current_point = starting_point
        
        for i, stop_idx in enumerate(sequence):
            stop = stops[stop_idx]
            next_point = stop.coordinates
            
            # Get traffic-aware directions
            directions = self.maps_service.get_directions(
                origin=current_point,
                destination=next_point,
                mode="driving",
                departure_time=dep_timestamp,
                traffic_model="best_guess"
            )
            
            # Extract route geometry if available
            route_coords = None
            instructions = None
            if directions and 'route_coordinates' in directions:
                route_coords = directions['route_coordinates']
            
            if directions and 'instructions' in directions:
                instructions = directions['instructions']

            # Get traffic-aware duration
            traffic_level = "low"
            try:
                traffic_level, _, duration = self.traffic_service.get_traffic_level(
                    current_point, next_point
                )
            except Exception:
                # Fallback to average speed if traffic service fails
                duration = distance / 8.33
            
            # Get distance and duration from directions (traffic-aware)
            if directions and directions.get('legs'):
                leg = directions['legs'][0]
                distance = leg['distance']['value']  # meters
                # Use traffic duration if available, otherwise regular duration
                if 'duration_in_traffic' in leg:
                    duration = leg['duration_in_traffic']['value']  # seconds
                else:
                    duration = leg['duration']['value']  # seconds
            else:
                # Fallback to straight-line distance
                distance = self.maps_service.calculate_straight_distance(
                    current_point, next_point
                )
                duration = distance / 8.33  # Estimate
            
            # Get weather data for route points
            weather_points = [current_point, next_point]
            if route_coords:
                # Sample weather at intermediate points
                step = max(1, len(route_coords) // 5)
                weather_points = [current_point] + [
                    Coordinate(latitude=c['lat'], longitude=c['lng'])
                    for c in route_coords[::step]
                ] + [next_point]
            
            # Fetch weather data
            weather_data_list = await self.weather_service.get_route_weather(weather_points)
            
            # Average weather hazard for the segment
            avg_weather_hazard = 0
            if weather_data_list:
                hazards = [w['weather'].get('hazard_score', 0) for w in weather_data_list]
                avg_weather_hazard = sum(hazards) / len(hazards) if hazards else 0
            
            weather_data = {
                'hazard_score': avg_weather_hazard,
                'hazard_conditions': []
            }
            if weather_data_list:
                # Aggregate conditions
                all_conditions = []
                for w in weather_data_list:
                    all_conditions.extend(w['weather'].get('hazard_conditions', []))
                weather_data['hazard_conditions'] = list(set(all_conditions))
            
            # Get safety score with weather data
            segment_coords = [current_point, next_point]
            if route_coords:
                # Sample coordinates to avoid scoring every single point (slow)
                max_points = 15
                if len(route_coords) > max_points:
                    step = len(route_coords) // max_points
                    sampled_coords = [route_coords[i] for i in range(0, len(route_coords), step)]
                    if (len(route_coords) - 1) % step != 0:
                        sampled_coords.append(route_coords[-1])
                else:
                    sampled_coords = route_coords
                    
                segment_coords = [
                    Coordinate(latitude=c['lat'], longitude=c['lng'])
                    for c in sampled_coords
                ]
            
            # Determine time of day
            time_of_day = "day"
            if departure_time:
                hour = departure_time.hour
                if hour < 6 or hour >= 22:
                    time_of_day = "night"
                elif hour < 8 or hour >= 18:
                    time_of_day = "evening"
            
            safety_data = self.safety_scorer.score_route(
                segment_coords, time_of_day, rider_info
            )
            safety_score = safety_data["route_safety_score"]
            
            # Apply weather penalty to duration
            weather_penalty = self.weather_service.calculate_weather_penalty(weather_data)
            duration = duration * weather_penalty
            
            # Phase 4: Predictive Delivery Time Model
            if HAS_RENOVATION_ML and self.time_predictor.model:
                try:
                    # Prepare features for ML model
                    # [distance, traffic_level, hour, weather_hazard, etc.]
                    feature_row = pd.DataFrame([{
                        'distance': distance / 1000.0,
                        'traffic_level': 2 if traffic_level == 'high' else 1 if traffic_level == 'medium' else 0,
                        'hour': departure_time.hour if departure_time else 12,
                        'weather_hazard': weather_data['hazard_score']
                    }])
                    if hasattr(self.time_predictor, 'feature_columns') and self.time_predictor.feature_columns:
                        for col in self.time_predictor.feature_columns:
                             if col not in feature_row.columns:
                                 feature_row[col] = 0
                    
                    predicted_min = self.time_predictor.predict(feature_row)[0]
                    # Blend OSRM duration with ML prediction (70/30)
                    duration = (duration * 0.7) + (predicted_min * 60 * 0.3)
                    logger.debug(f"Applied ML time prediction: {predicted_min:.2f} min (Original: {duration/60:.2f} min)")
                except Exception as e:
                    logger.warning(f"Predictive time model failed: {e}")

            # Calculate fuel consumption

            fuel = distance / 1000 * settings.FUEL_CONSUMPTION_PER_KM
            
            # Get traffic level for this segment
            traffic_level = "low"
            try:
                traffic_level, _, _ = self.traffic_service.get_traffic_level(
                    current_point, next_point
                )
            except Exception:
                pass
            
            segments.append({
                "from_stop": f"START_{i}" if i == 0 else stops[sequence[i-1]].stop_id,
                "to_stop": stop.stop_id,
                "distance_meters": distance,
                "duration_seconds": duration,
                "safety_score": safety_score,
                "estimated_fuel_liters": fuel,
                "route_coordinates": route_coords,
                "instructions": instructions,
                "weather_data": weather_data,
                "has_traffic_data": directions and directions.get('has_traffic_data', False),
                "traffic_level": traffic_level
            })
            
            total_distance += distance
            total_duration += duration
            total_safety += safety_score
            total_fuel += fuel
            
            current_point = next_point
        
        avg_safety = total_safety / len(sequence) if sequence else 0
        
        return segments, {
            "distance": total_distance,
            "duration": total_duration,
            "avg_safety": avg_safety,
            "fuel": total_fuel
        }
    
    def _calculate_arrivals(
        self,
        starting_point: Coordinate,
        stops: List[DeliveryStop],
        sequence: List[int],
        segments: List[Dict],
        departure_time: Optional[datetime]
    ) -> Dict[str, datetime]:
        """Calculate estimated arrival times for each stop."""
        arrivals = {}
        
        if not departure_time:
            departure_time = datetime.now()
        
        current_time = departure_time
        
        for i, segment in enumerate(segments):
            duration_seconds = segment["duration_seconds"]
            current_time += timedelta(seconds=duration_seconds)
            stop_id = segment["to_stop"]
            arrivals[stop_id] = current_time
        
        return arrivals

    async def _optimize_single_leg_alternatives(
        self,
        starting_point: Coordinate,
        stop: DeliveryStop,
        optimize_for: List[str],
        rider_info: Optional[Dict],
        departure_time: Optional[datetime]
    ) -> Dict:
        """Find and rank alternative routes for a single stop."""
        dep_timestamp = int(departure_time.timestamp()) if departure_time else None
        
        # Get all route variations
        all_directions = self.maps_service.get_all_directions(
            origin=starting_point,
            destination=stop.coordinates,
            mode="driving",
            departure_time=dep_timestamp,
            traffic_model="best_guess"
        )
        
        candidates = []
        
        for directions in all_directions:
            # Process this route option
            segment, stats = await self._process_segment_data(
                starting_point,
                stop.coordinates,
                directions,
                rider_info,
                departure_time
            )
            
            # Create unique route object for this candidate
            route_id = f"ROUTE_{uuid.uuid4().hex[:10]}"
            
            # Calculate cost/score for ranking
            score = 0
            if "time" in optimize_for:
                score += stats["duration"]
            if "distance" in optimize_for:
                score += stats["distance"] * 0.1
            if "safety" in optimize_for:
                # Lower score is better for ranking (so invert safety)
                score += (100 - stats["avg_safety"]) * 10
            
            candidate = {
                "route_id": route_id,
                "sequence": [stop.stop_id],
                "segments": [segment.copy()],
                "total_distance_meters": stats["distance"],
                "total_duration_seconds": stats["duration"],
                "average_safety_score": stats["avg_safety"],
                "total_fuel_liters": stats["fuel"],
                "optimizations_applied": optimize_for,
                "estimated_arrivals": {
                    stop.stop_id: (departure_time or datetime.now()) + timedelta(seconds=stats["duration"])
                },
                "created_at": datetime.now(),
                "_ranking_score": score
            }
            segment["to_stop"] = stop.stop_id # Ensure ID is set
            candidates.append(candidate)
            
        if not candidates:
            # Fallback if no routes found (shouldn't happen with mock/real)
            raise ValueError("No routes found between points")
            
        # Sort candidates based on objectives
        # Default sort is ascending score (lower cost is better)
        candidates.sort(key=lambda x: x["_ranking_score"])
        
        best_route = candidates[0]
        alternatives = candidates[1:] if len(candidates) > 1 else []
        
        # Clean up internal ranking score
        del best_route["_ranking_score"]
        for alt in alternatives:
            del alt["_ranking_score"]
            
        best_route["alternatives"] = alternatives
        
        # RENOVATION: RL Agent Recommendation
        if HAS_RENOVATION_ML and candidates:
            try:
                # Prepare state for RL
                context = {
                    'current_lat': starting_point.latitude,
                    'current_lng': starting_point.longitude,
                    'hour': departure_time.hour if departure_time else datetime.now().hour,
                    'traffic_level': best_route.get('traffic_level', 'medium'),
                    'weather_condition': 'clear' # Default
                }
                state = self.rl_agent.get_state(context)
                
                # Available route IDs (indices)
                route_ids = [str(i) for i in range(len(candidates))]
                
                # Choose best action according to RL
                chosen_id = self.rl_agent.choose_action(state, route_ids)
                
                best_route["rl_recommended_id"] = chosen_id
                best_route["rl_state"] = str(state)
                logger.info(f"RL Agent Recommended Route ID: {chosen_id}")
            except Exception as e:
                logger.warning(f"RL recommendation failed: {e}")

        return best_route

    async def _process_segment_data(
        self,
        start_point: Coordinate,
        end_point: Coordinate,
        directions: Dict,
        rider_info: Optional[Dict],
        departure_time: Optional[datetime]
    ) -> Tuple[Dict, Dict]:
        """Process directions into a route segment with safety/weather data."""
        
        # Extract basic metrics
        distance = 0
        duration = 0
        
        if directions and directions.get('legs'):
            leg = directions['legs'][0]
            distance = leg['distance']['value']
            if 'duration_in_traffic' in leg:
                duration = leg['duration_in_traffic']['value']
            else:
                duration = leg['duration']['value']
        else:
            distance = self.maps_service.calculate_straight_distance(start_point, end_point)
            duration = distance / 8.33
            
        route_coords = directions.get('route_coordinates')
        instructions = directions.get('instructions')
        
        # Weather
        weather_points = [start_point, end_point]
        if route_coords:
            step = max(1, len(route_coords) // 5)
            weather_points = [start_point] + [
                Coordinate(latitude=c['lat'], longitude=c['lng'])
                for c in route_coords[::step]
            ] + [end_point]
            
        weather_data_list = await self.weather_service.get_route_weather(weather_points)
        
        avg_weather_hazard = 0
        weather_conditions = []
        if weather_data_list:
            hazards = [w['weather'].get('hazard_score', 0) for w in weather_data_list]
            avg_weather_hazard = sum(hazards) / len(hazards) if hazards else 0
            for w in weather_data_list:
                weather_conditions.extend(w['weather'].get('hazard_conditions', []))
        
        weather_data = {
            'hazard_score': avg_weather_hazard,
            'hazard_conditions': list(set(weather_conditions))
        }
        
        # Safety
        segment_coords = [start_point, end_point]
        if route_coords:
            # Sample coordinates to avoid scoring every single point (slow)
            # We take at most 15 points uniformly distributed
            max_points = 15
            if len(route_coords) > max_points:
                step = len(route_coords) // max_points
                sampled_coords = [route_coords[i] for i in range(0, len(route_coords), step)]
                # Ensure the last point is included
                if (len(route_coords) - 1) % step != 0:
                    sampled_coords.append(route_coords[-1])
            else:
                sampled_coords = route_coords
                
            segment_coords = [
                Coordinate(latitude=c['lat'], longitude=c['lng'])
                for c in sampled_coords
            ]
            
        time_of_day = "day"
        if departure_time:
            hour = departure_time.hour
            if hour < 6 or hour >= 22:
                time_of_day = "night"
            elif hour < 8 or hour >= 18:
                time_of_day = "evening"
                
        safety_data = self.safety_scorer.score_route(
            segment_coords, time_of_day, rider_info
        )
        safety_score = safety_data["route_safety_score"]

        # RENOVATION: ML Model Integration
        if HAS_RENOVATION_ML:
            try:
                # Prepare context for feature extraction
                route_context = {
                    'delivery_time': departure_time.isoformat() if departure_time else datetime.utcnow().isoformat(),
                    'total_distance': distance / 1000,
                    'segments': [{
                        'distance': distance / 1000,
                        'start_lat': start_point.latitude,
                        'start_lng': start_point.longitude,
                        'end_lat': end_point.latitude,
                        'end_lng': end_point.longitude
                    }]
                }
                
                # Extract features
                features_df = self.feature_engineer.extract_features(route_context)
                
                # Predict Time (minutes to seconds)
                ml_time_min = self.time_predictor.predict(features_df)[0]
                duration = float(ml_time_min * 60)
                
                # Predict Safety Score (Random Forest)
                ml_safety_score = self.safety_classifier.predict_safety_score(features_df)[0]
                safety_score = float(ml_safety_score)
                
                logger.info(f"ML Metrics - Time: {ml_time_min:.1f}m, Safety: {safety_score:.1f}")
            except Exception as e:
                logger.warning(f"ML prediction failed, using rule-based fallback: {e}")

        # Adjustments
        weather_penalty = self.weather_service.calculate_weather_penalty(weather_data)
        duration = duration * weather_penalty
        
        fuel = distance / 1000 * settings.FUEL_CONSUMPTION_PER_KM
        
        # Traffic level (simplified check)
        traffic_level = "low"
        if directions.get('has_traffic_data'):
             # If duration in traffic is significantly higher than base duration
             # We can't easily get base duration from here without another call, 
             # so we rely on what traffic service would say or infer from speed
             avg_speed_kmh = (distance / 1000) / (duration / 3600) if duration > 0 else 30
             if avg_speed_kmh < 15:
                 traffic_level = "high"
             elif avg_speed_kmh < 30:
                 traffic_level = "medium"
        
        segment = {
            "from_stop": "START", # Placeholder, should be fixed by caller if needed
            "to_stop": "END",
            "distance_meters": distance,
            "duration_seconds": duration,
            "safety_score": safety_score,
            "estimated_fuel_liters": fuel,
            "route_coordinates": route_coords,
            "instructions": instructions,
            "weather_data": weather_data,
            "has_traffic_data": directions.get('has_traffic_data', False),
            "traffic_level": traffic_level
        }
        
        stats = {
            "distance": distance,
            "duration": duration,
            "avg_safety": safety_score,
            "fuel": fuel
        }
        
        return segment, stats

