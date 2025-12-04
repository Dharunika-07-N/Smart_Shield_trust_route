"""Route Optimization Engine."""
import networkx as nx
from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

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
from api.services.maps import MapsService
from api.models.safety_scorer import SafetyScorer
from api.services.traffic import TrafficService
from loguru import logger


class RouteOptimizer:
    """Multi-objective route optimization engine."""
    
    def __init__(self):
        self.maps_service = MapsService()
        self.safety_scorer = SafetyScorer()
        self.traffic_service = TrafficService()
    
    def optimize_route(
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
            Optimized route with sequence, distances, times, etc.
        """
        if not stops:
            raise ValueError("No stops provided")
        
        logger.info(f"Optimizing route for {len(stops)} stops, objectives: {optimize_for}")
        
        # Prepare data
        all_points = [starting_point] + [stop.coordinates for stop in stops]
        
        # Create distance matrix
        distance_matrix = self._create_distance_matrix(all_points)
        
        # Create cost matrix based on objectives
        cost_matrix = self._create_cost_matrix(
            all_points,
            distance_matrix,
            optimize_for,
            rider_info,
            stops
        )
        
        # Optimize using multiple algorithms
        if settings.OPTIMIZATION_ALGORITHM == "genetic":
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
        segments, total_stats = self._build_route_segments(
            starting_point,
            stops,
            sequence,
            optimize_for,
            rider_info
        )
        
        # Generate route ID
        route_id = f"ROUTE_{int(datetime.now().timestamp())}"
        
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
        stops: List[DeliveryStop]
    ) -> List[List[float]]:
        """Create weighted cost matrix based on objectives."""
        n = len(points)
        cost_matrix = [[0.0] * n for _ in range(n)]
        
        # Get safety scores for all segments
        safety_matrix = [[1.0] * n for _ in range(n)]
        if "safety" in objectives:
            time_of_day = "day"  # Could be extracted from departure_time
            for i in range(n):
                for j in range(n):
                    if i != j:
                        # Get safety score for segment
                        segment_coords = [points[i], points[j]]
                        safety_data = self.safety_scorer.score_route(segment_coords, time_of_day, rider_info)
                        # Inverse safety score (higher safety = lower cost)
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
                    if "safety" in objectives:
                        safety_cost = safety_matrix[i][j] / 100.0
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
    
    def _optimize_genetic(
        self,
        cost_matrix: List[List[float]],
        num_stops: int
    ) -> List[int]:
        """Genetic algorithm optimization (simplified)."""
        # For simplicity, use nearest neighbor with variations
        # In production, implement full GA with population, crossover, mutation
        return self._optimize_nearest_neighbor(cost_matrix)
    
    def _build_route_segments(
        self,
        starting_point: Coordinate,
        stops: List[DeliveryStop],
        sequence: List[int],
        objectives: List[str],
        rider_info: Optional[Dict]
    ) -> Tuple[List[Dict], Dict]:
        """Build route segments with statistics."""
        segments = []
        total_distance = 0
        total_duration = 0
        total_safety = 0
        total_fuel = 0
        
        # First segment: starting point to first stop
        current_point = starting_point
        
        for i, stop_idx in enumerate(sequence):
            stop = stops[stop_idx]
            next_point = stop.coordinates
            
            # Calculate distance
            distance = self.maps_service.calculate_straight_distance(
                current_point, next_point
            )
            
            # Get traffic-aware duration
            traffic_level = "low"
            try:
                traffic_level, _, duration = self.traffic_service.get_traffic_level(
                    current_point, next_point
                )
            except Exception:
                # Fallback to average speed if traffic service fails
                duration = distance / 8.33
            
            # Get safety score
            segment_coords = [current_point, next_point]
            safety_data = self.safety_scorer.score_route(
                segment_coords, "day", rider_info
            )
            safety_score = safety_data["route_safety_score"]
            
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

