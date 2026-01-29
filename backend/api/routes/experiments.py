from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import sys
from pathlib import Path

# Add backend to path for module resolution
backend_path = str(Path(__file__).parent.parent.parent)
if backend_path not in sys.path:
    sys.path.append(backend_path)

from ml.ab_tester import ABTester

router = APIRouter()
ab_tester = ABTester()

class ExperimentCreateRequest(BaseModel):
    name: str
    model_type: str # "safety" or "time"
    version_a: str
    version_b: str
    traffic_split_a: float = 0.5
    description: Optional[str] = ""

class ExperimentStopRequest(BaseModel):
    name: str
    winner_version: str

@router.post("/experiments/create")
async def create_experiment(request: ExperimentCreateRequest):
    """Create a new model experiment"""
    exp_id = ab_tester.create_experiment(
        request.name,
        request.model_type,
        request.version_a,
        request.version_b,
        request.traffic_split_a,
        request.description
    )
    if exp_id == -1:
        raise HTTPException(status_code=400, detail="Experiment name already exists")
    return {"status": "success", "experiment_id": exp_id}

@router.get("/experiments/assignment/{experiment_name}/{entity_id}")
async def get_assignment(experiment_name: str, entity_id: str):
    """Get model version assignment for an entity"""
    version = ab_tester.get_assigned_version(experiment_name, entity_id)
    return {"experiment": experiment_name, "assigned_version": version}

@router.get("/experiments/compare/{experiment_name}")
async def compare_performance(experiment_name: str):
    """Compare group performance"""
    comparison = ab_tester.compare_performance(experiment_name)
    if "error" in comparison:
        raise HTTPException(status_code=404, detail=comparison["error"])
    return comparison

@router.post("/experiments/stop")
async def stop_experiment(request: ExperimentStopRequest):
    """Stop experiment and finalize winner"""
    ab_tester.stop_experiment(request.name, request.winner_version)
    return {"status": "success", "message": f"Experiment {request.name} stopped"}
