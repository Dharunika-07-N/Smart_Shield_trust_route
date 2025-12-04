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
from api.services.weather import WeatherService

from loguru import logger
import asyncio


class RouteOptimizer:
    """Multi-objective route optimization engine."""

    def __init__(self):
        self.maps_service = MapsService()
        self.safety_scorer = SafetyScorer()
        self.traffic_service = TrafficService()
        self.weather_service = WeatherService()

    def optimize_route(
        self,
        starting_point: Coordinate,
        stops: List[DeliveryStop],
        optimize_for: List[str] = ["time", "distance"],
        rider_info: Optional[Dict] = None,
        vehicle_type: str = "motorcycle",
        departure_time: Optional[datetime] = None
    ) -> Dict:

        if not stops:
            raise ValueError("No stops provided")

        logger.info(f"Optimizing route for {len(stops)} stops, objectives: {optimize_for}")

        all_points = [starting_point] + [stop.coordinates for stop in stops]

        # Distance matrix
        distance_matrix = self._create_distance_matrix(all_points)

        # Cost matrix
        cost_matrix = self._create_cost_matrix(
            all_points, distance_matrix, optimize_for, rider_info, stops
        )

        # Optimization strategy
        if settings.OPTIMIZATION_ALGORITHM == "genetic":
            sequence = self._optimize_genetic(cost_matrix, len(stops))
        elif settings.OPTIMIZATION_ALGORITHM == "nearest_neighbor":
            sequence = self._optimize_nearest_neighbor(cost_matrix)
        elif HAS_ORTOOLS:
            sequence = self._optimize_ortools(cost_matrix, len(stops))
        else:
            sequence = self._optimize_nearest_neighbor(cost_matrix)

        # Build route
        segments, total_stats = self._build_route_segments(
            starting_point, stops, sequence, optimize_for, rider_info, departure_time
        )

        route_id = f"ROUTE_{int(datetime.now().timestamp())}"

        # Estimate arrival times
        estimated_arrivals = self._calculate_arrivals(
            starting_point, stops, sequence, segments, departure_time
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

    def _create_distance_matrix(self, points: List[Coordinate]):
        n = len(points)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = self.maps_service.calculate_straight_distance(
                        points[i], points[j]
                    )
        return matrix

    def _create_cost_matrix(
        self,
        points,
        distance_matrix,
        objectives,
        rider_info,
        stops
    ):
        n = len(points)
        cost_matrix = [[0.0] * n for _ in range(n)]

        # Safety matrix
        safety_matrix = [[1.0] * n for _ in range(n)]
        if "safety" in objectives:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        s = self.safety_scorer.score_route([points[i], points[j]], "day", rider_info)
                        safety_matrix[i][j] = 100 - s["route_safety_score"]

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue

                dist = distance_matrix[i][j] / 1000  # km
                cost = 0

                if "distance" in objectives:
                    cost += dist

                if "time" in objectives:
                    time_cost = distance_matrix[i][j] / 8.33 / 60
                    cost += time_cost * 0.1

                if "fuel" in objectives:
                    fuel_cost = dist * settings.FUEL_CONSUMPTION_PER_KM
                    cost += fuel_cost * 10

                if "safety" in objectives:
                    cost += safety_matrix[i][j] / 100.0

                # Traffic data
                if "traffic" in objectives or "time" in objectives:
                    try:
                        traffic_level, _, traffic_dur = self.traffic_service.get_traffic_level(
                            points[i], points[j]
                        )
                        if traffic_level == "high":
                            cost += (traffic_dur / 60) * 0.3
                        elif traffic_level == "medium":
                            cost += (traffic_dur / 60) * 0.15
                    except:
                        pass

                cost_matrix[i][j] = cost

        return cost_matrix

    def _optimize_ortools(self, cost_matrix, num_stops):
        try:
            manager = pywrapcp.RoutingIndexManager(num_stops + 1, 1, 0)
            routing = pywrapcp.RoutingModel(manager)

            def distance_callback(from_index, to_index):
                f = manager.IndexToNode(from_index)
                t = manager.IndexToNode(to_index)
                return int(cost_matrix[f][t] * 1000)

            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

            params = pywrapcp.DefaultRoutingSearchParameters()
            params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            params.time_limit.seconds = 5

            sol = routing.SolveWithParameters(params)

            if sol:
                index = routing.Start(0)
                route = []
                while not routing.IsEnd(index):
                    node = manager.IndexToNode(index)
                    if node > 0:
                        route.append(node - 1)
                    index = sol.Value(routing.NextVar(index))
                return route

        except Exception:
            pass

        return self._optimize_nearest_neighbor(cost_matrix)

    def _optimize_nearest_neighbor(self, cost_matrix):
        n = len(cost_matrix)
        visited = {0}
        route = []
        current = 0

        while len(route) < n - 1:
            next_node = None
            min_cost = float("inf")

            for i in range(1, n):
                if i not in visited and cost_matrix[current][i] < min_cost:
                    min_cost = cost_matrix[current][i]
                    next_node = i

            route.append(next_node - 1)
            visited.add(next_node)
            current = next_node

        return route

    def _optimize_genetic(self, cost_matrix, num_stops):
        return self._optimize_nearest_neighbor(cost_matrix)

    def _build_route_segments(
        self,
        starting_point,
        stops,
        sequence,
        objectives,
        rider_info,
        departure_time=None
    ):
        segments = []
        total_distance = 0
        total_duration = 0
        total_safety = 0
        total_fuel = 0

        dep_timestamp = int(departure_time.timestamp()) if departure_time else None
        current_point = starting_point

        for i, stop_idx in enumerate(sequence):
            stop = stops[stop_idx]
            next_point = stop.coordinates

            directions = self.maps_service.get_directions(
                origin=current_point,
                destination=next_point,
                mode="driving",
                departure_time=dep_timestamp,
                traffic_model="best_guess"
            )

            # Traffic data
            try:
                traffic_level, _, duration = self.traffic_service.get_traffic_level(
                    current_point, next_point
                )
            except:
                traffic_level = "low"
                duration = None

            # Extract geometry
            route_coords = directions.get("route_coordinates") if directions else None

            # Distance & duration
            if directions and directions.get("legs"):
                leg = directions["legs"][0]
                distance = leg["distance"]["value"]
                duration = leg.get("duration_in_traffic", leg["duration"])["value"]
            else:
                distance = self.maps_service.calculate_straight_distance(
                    current_point, next_point
                )
                duration = distance / 8.33

            # Weather sampling
            weather_points = [current_point, next_point]
            if route_coords:
                step = max(1, len(route_coords) // 5)
                weather_points = (
                    [current_point]
                    + [Coordinate(latitude=c["lat"], longitude=c["lng"]) for c in route_coords[::step]]
                    + [next_point]
                )

            weather_data_list = asyncio.run(
                self.weather_service.get_route_weather(weather_points)
            )

            avg_weather_hazard = 0
            if weather_data_list:
                hazards = [w["weather"].get("hazard_score", 0) for w in weather_data_list]
                avg_weather_hazard = sum(hazards) / len(hazards)

            weather_data = {
                "hazard_score": avg_weather_hazard,
                "hazard_conditions": list({
                    cond
                    for w in weather_data_list
                    for cond in w["weather"].get("hazard_conditions", [])
                })
                if weather_data_list
                else []
            }

            # Safety scoring
            if route_coords:
                segment_coords = [
                    Coordinate(latitude=c["lat"], longitude=c["lng"])
                    for c in route_coords
                ]
            else:
                segment_coords = [current_point, next_point]

            time_of_day = "day"
            if departure_time:
                hour = departure_time.hour
                if hour < 6 or hour >= 22:
                    time_of_day = "night"
                elif hour < 8 or hour >= 18:
                    time_of_day = "evening"

            safety_data = self.safety_scorer.score_route(segment_coords, time_of_day, rider_info)
            safety_score = safety_data["route_safety_score"]

            # Weather penalty
            weather_penalty = self.weather_service.calculate_weather_penalty(weather_data)
            duration *= weather_penalty

            # Fuel
            fuel = distance / 1000 * settings.FUEL_CONSUMPTION_PER_KM

            segments.append({
                "from_stop": f"START_{i}" if i == 0 else stops[sequence[i - 1]].stop_id,
                "to_stop": stop.stop_id,
                "distance_meters": distance,
                "duration_seconds": duration,
                "safety_score": safety_score,
                "estimated_fuel_liters": fuel,
                "traffic_level": traffic_level,
                "route_coordinates": route_coords,
                "weather_data": weather_data,
                "has_traffic_data": directions.get("has_traffic_data", False) if directions else False
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
        starting_point,
        stops,
        sequence,
        segments,
        departure_time
    ):
        arrivals = {}

        if not departure_time:
            departure_time = datetime.now()

        current_time = departure_time

        for seg in segments:
            current_time += timedelta(seconds=seg["duration_seconds"])
            arrivals[seg["to_stop"]] = current_time

        return arrivals
