"""
A* Heuristic Route Optimizer with Multi-Objective Cost Function
Optimizes for: Time, Distance, Safety, and Traffic
"""
import heapq
import networkx as nx
import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import math

@dataclass(order=True)
class PriorityNode:
    """Priority queue node for A* algorithm"""
    f_score: float
    node: Tuple[float, float] = field(compare=False)
    g_score: float = field(compare=False)
    h_score: float = field(compare=False)
    path: List[Tuple[float, float]] = field(compare=False)


class AStarRouteOptimizer:
    """
    A* Algorithm implementation for route optimization
    with multi-objective heuristic function
    """
    
    def __init__(self, 
                 weight_distance: float = 0.3,
                 weight_time: float = 0.3,
                 weight_safety: float = 0.2,
                 weight_traffic: float = 0.2):
        """
        Initialize A* optimizer with configurable weights
        
        Args:
            weight_distance: Weight for distance component (0-1)
            weight_time: Weight for time component (0-1)
            weight_safety: Weight for safety component (0-1)
            weight_traffic: Weight for traffic component (0-1)
        """
        self.w_distance = weight_distance
        self.w_time = weight_time
        self.w_safety = weight_safety
        self.w_traffic = weight_traffic
        
        # Normalize weights
        total = sum([weight_distance, weight_time, weight_safety, weight_traffic])
        if total > 0:
            self.w_distance /= total
            self.w_time /= total
            self.w_safety /= total
            self.w_traffic /= total
    
    def haversine_distance(self, 
                          coord1: Tuple[float, float], 
                          coord2: Tuple[float, float]) -> float:
        """
        Calculate great-circle distance between two points (in meters)
        
        Args:
            coord1: (latitude, longitude) of first point
            coord2: (latitude, longitude) of second point
            
        Returns:
            Distance in meters
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) *
             math.sin(delta_lambda / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def get_safety_penalty(self, 
                          coord: Tuple[float, float],
                          safety_data: Optional[Dict] = None) -> float:
        """
        Calculate safety penalty for a location (0-1, lower is safer)
        
        Args:
            coord: (latitude, longitude)
            safety_data: Dictionary of safety scores by location
            
        Returns:
            Safety penalty (0 = safest, 1 = most dangerous)
        """
        if not safety_data:
            return 0.2  # Default moderate safety
        
        # Find nearest safety score
        min_dist = float('inf')
        nearest_score = 75.0  # Default
        
        for loc, score in safety_data.items():
            dist = self.haversine_distance(coord, loc)
            if dist < min_dist:
                min_dist = dist
                nearest_score = score
        
        # Convert safety score (0-100) to penalty (0-1)
        # Higher safety score = lower penalty
        penalty = (100 - nearest_score) / 100
        return max(0.0, min(1.0, penalty))
    
    def get_traffic_multiplier(self,
                               coord: Tuple[float, float],
                               traffic_data: Optional[Dict] = None,
                               time_of_day: Optional[int] = None) -> float:
        """
        Calculate traffic multiplier (1.0 = no traffic, 2.0 = heavy traffic)
        
        Args:
            coord: (latitude, longitude)
            traffic_data: Dictionary of traffic levels by location
            time_of_day: Hour of day (0-23)
            
        Returns:
            Traffic multiplier (1.0-2.5)
        """
        if not traffic_data:
            # Use time-based heuristic
            if time_of_day is None:
                time_of_day = datetime.now().hour
            
            # Peak hours: 8-9 AM, 5-7 PM
            if time_of_day in [8, 9, 17, 18, 19]:
                return 1.8  # Heavy traffic
            elif time_of_day in [7, 10, 11, 12, 13, 14, 15, 16, 20]:
                return 1.3  # Moderate traffic
            else:
                return 1.0  # Light traffic
        
        # Find nearest traffic data
        min_dist = float('inf')
        nearest_level = 'low'
        
        for loc, level in traffic_data.items():
            dist = self.haversine_distance(coord, loc)
            if dist < min_dist:
                min_dist = dist
                nearest_level = level
        
        traffic_multipliers = {
            'low': 1.0,
            'medium': 1.4,
            'high': 2.0,
            'severe': 2.5
        }
        
        return traffic_multipliers.get(nearest_level, 1.0)
    
    def estimate_travel_time(self,
                            coord1: Tuple[float, float],
                            coord2: Tuple[float, float],
                            avg_speed_kmh: float = 30.0) -> float:
        """
        Estimate travel time between two points (in seconds)
        
        Args:
            coord1: Starting coordinate
            coord2: Ending coordinate
            avg_speed_kmh: Average speed in km/h
            
        Returns:
            Estimated time in seconds
        """
        distance_m = self.haversine_distance(coord1, coord2)
        distance_km = distance_m / 1000
        time_hours = distance_km / avg_speed_kmh
        return time_hours * 3600  # Convert to seconds
    
    def heuristic(self,
                 current: Tuple[float, float],
                 goal: Tuple[float, float],
                 safety_data: Optional[Dict] = None,
                 traffic_data: Optional[Dict] = None,
                 time_of_day: Optional[int] = None) -> float:
        """
        Multi-objective heuristic function for A*
        
        h(n) = w1*distance + w2*time + w3*safety + w4*traffic
        
        Args:
            current: Current node coordinates
            goal: Goal node coordinates
            safety_data: Safety scores by location
            traffic_data: Traffic levels by location
            time_of_day: Hour of day
            
        Returns:
            Heuristic cost estimate
        """
        # Component 1: Euclidean distance (admissible)
        h_distance = self.haversine_distance(current, goal) / 1000  # km
        
        # Component 2: Time estimate
        traffic_mult = self.get_traffic_multiplier(current, traffic_data, time_of_day)
        h_time = self.estimate_travel_time(current, goal) * traffic_mult / 60  # minutes
        
        # Component 3: Safety penalty
        h_safety = self.get_safety_penalty(current, safety_data) * 100  # scale to 0-100
        
        # Component 4: Traffic penalty
        h_traffic = (traffic_mult - 1.0) * 50  # scale to 0-75
        
        # Weighted combination
        h_total = (self.w_distance * h_distance +
                  self.w_time * h_time +
                  self.w_safety * h_safety +
                  self.w_traffic * h_traffic)
        
        return h_total
    
    def get_neighbors(self,
                     node: Tuple[float, float],
                     graph: Optional[nx.Graph] = None,
                     grid_resolution: float = 0.001) -> List[Tuple[float, float]]:
        """
        Get neighboring nodes (8-directional grid if no graph provided)
        
        Args:
            node: Current node
            graph: NetworkX graph (if available)
            grid_resolution: Grid spacing in degrees (~100m)
            
        Returns:
            List of neighbor coordinates
        """
        if graph and node in graph:
            return list(graph.neighbors(node))
        
        # 8-directional grid neighbors
        lat, lon = node
        neighbors = []
        for dlat in [-grid_resolution, 0, grid_resolution]:
            for dlon in [-grid_resolution, 0, grid_resolution]:
                if dlat == 0 and dlon == 0:
                    continue
                neighbors.append((lat + dlat, lon + dlon))
        
        return neighbors
    
    def reconstruct_path(self, 
                        came_from: Dict,
                        current: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Reconstruct path from start to current node"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
    
    def find_optimal_route(self,
                          start: Tuple[float, float],
                          goal: Tuple[float, float],
                          safety_data: Optional[Dict] = None,
                          traffic_data: Optional[Dict] = None,
                          graph: Optional[nx.Graph] = None,
                          max_iterations: int = 10000) -> Dict:
        """
        Find optimal route using A* algorithm
        
        Args:
            start: Starting coordinates (lat, lon)
            goal: Goal coordinates (lat, lon)
            safety_data: Safety scores by location
            traffic_data: Traffic levels by location
            graph: Road network graph (optional)
            max_iterations: Maximum iterations to prevent infinite loops
            
        Returns:
            Dictionary with path, cost, and metrics
        """
        # Initialize
        open_set = []
        closed_set: Set[Tuple[float, float]] = set()
        came_from: Dict[Tuple[float, float], Tuple[float, float]] = {}
        
        g_score: Dict[Tuple[float, float], float] = {start: 0}
        h_score = self.heuristic(start, goal, safety_data, traffic_data)
        f_score: Dict[Tuple[float, float], float] = {start: h_score}
        
        # Add start node to open set
        heapq.heappush(open_set, PriorityNode(
            f_score=h_score,
            node=start,
            g_score=0,
            h_score=h_score,
            path=[start]
        ))
        
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            
            # Get node with lowest f_score
            current_priority = heapq.heappop(open_set)
            current = current_priority.node
            
            # Check if we reached the goal
            if self.haversine_distance(current, goal) < 100:  # Within 100m
                path = self.reconstruct_path(came_from, current)
                
                return {
                    'path': path,
                    'total_cost': g_score[current],
                    'total_distance_m': sum(
                        self.haversine_distance(path[i], path[i+1])
                        for i in range(len(path)-1)
                    ),
                    'iterations': iterations,
                    'nodes_explored': len(closed_set),
                    'success': True
                }
            
            closed_set.add(current)
            
            # Explore neighbors
            for neighbor in self.get_neighbors(current, graph):
                if neighbor in closed_set:
                    continue
                
                # Calculate tentative g_score
                edge_distance = self.haversine_distance(current, neighbor)
                edge_time = self.estimate_travel_time(current, neighbor)
                edge_safety = self.get_safety_penalty(neighbor, safety_data)
                edge_traffic = self.get_traffic_multiplier(neighbor, traffic_data)
                
                # Multi-objective edge cost
                edge_cost = (self.w_distance * edge_distance / 1000 +
                           self.w_time * edge_time / 60 +
                           self.w_safety * edge_safety * 100 +
                           self.w_traffic * (edge_traffic - 1.0) * 50)
                
                tentative_g = g_score[current] + edge_cost
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    # This path is better
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h = self.heuristic(neighbor, goal, safety_data, traffic_data)
                    f_score[neighbor] = tentative_g + h
                    
                    heapq.heappush(open_set, PriorityNode(
                        f_score=f_score[neighbor],
                        node=neighbor,
                        g_score=tentative_g,
                        h_score=h,
                        path=[]
                    ))
        
        # No path found
        return {
            'path': [],
            'total_cost': float('inf'),
            'total_distance_m': 0,
            'iterations': iterations,
            'nodes_explored': len(closed_set),
            'success': False,
            'error': 'No path found within iteration limit'
        }


# Example usage
if __name__ == "__main__":
    # Initialize optimizer
    optimizer = AStarRouteOptimizer(
        weight_distance=0.3,
        weight_time=0.3,
        weight_safety=0.25,
        weight_traffic=0.15
    )
    
    # Example coordinates (Coimbatore area)
    start = (11.0168, 76.9558)  # Coimbatore center
    goal = (11.0500, 76.9800)   # Destination
    
    # Example safety data
    safety_data = {
        (11.0200, 76.9600): 85,  # Safe area
        (11.0300, 76.9700): 60,  # Moderate
        (11.0400, 76.9750): 40,  # Less safe
    }
    
    # Example traffic data
    traffic_data = {
        (11.0250, 76.9650): 'medium',
        (11.0350, 76.9720): 'high',
    }
    
    # Find optimal route
    result = optimizer.find_optimal_route(
        start=start,
        goal=goal,
        safety_data=safety_data,
        traffic_data=traffic_data
    )
    
    print(f"Success: {result['success']}")
    print(f"Path length: {len(result['path'])} nodes")
    print(f"Total distance: {result['total_distance_m']:.0f} meters")
    print(f"Iterations: {result['iterations']}")
    print(f"Nodes explored: {result['nodes_explored']}")
