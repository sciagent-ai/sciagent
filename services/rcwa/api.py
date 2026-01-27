"""
RCWA Simulation Service API
FastAPI wrapper for S4 RCWA simulations.
"""

import sys
print(f"api.py loading...", flush=True)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json

from simulate import run_rcwa_simulation, optimize_grating, S4_AVAILABLE
print(f"api.py: imported S4_AVAILABLE = {S4_AVAILABLE}", flush=True)

app = FastAPI(
    title="RCWA Simulation Service",
    description="Rigorous Coupled-Wave Analysis for layered periodic structures using S4",
    version="1.0.0"
)


# Request/Response Models

class GratingParams(BaseModel):
    fill_factor: float = Field(0.5, ge=0.0, le=1.0, description="Fill factor (0-1)")
    depth: float = Field(200, gt=0, description="Grating depth in nm")
    substrate: str = Field("silicon", description="Substrate material")


class LayerPattern(BaseModel):
    type: str = Field("grating", description="Pattern type")
    fill_factor: float = Field(0.5, description="Fill factor for grating")
    material2: str = Field("air", description="Secondary material")


class Layer(BaseModel):
    material: str = Field(..., description="Layer material")
    thickness: Optional[float] = Field(None, description="Layer thickness in nm (None for semi-infinite)")
    pattern: Optional[LayerPattern] = Field(None, description="Pattern for patterned layers")


class SimulationRequest(BaseModel):
    period: float = Field(..., gt=0, description="Grating period in nm")
    wavelength: float = Field(..., gt=0, description="Incident wavelength in nm")
    angle_of_incidence: float = Field(0, ge=-90, le=90, description="Angle from normal in degrees")
    polarization: str = Field("s", description="'s' (TE) or 'p' (TM)")
    layers: Optional[List[Layer]] = Field(None, description="Full layer stack")
    grating_params: Optional[GratingParams] = Field(None, description="Simple grating shortcut")
    num_harmonics: int = Field(21, ge=3, description="Number of Fourier harmonics")
    output_orders: List[int] = Field([-2, -1, 0, 1, 2], description="Diffraction orders to compute")

    class Config:
        json_schema_extra = {
            "example": {
                "period": 500,
                "wavelength": 633,
                "angle_of_incidence": 45,
                "polarization": "s",
                "grating_params": {
                    "fill_factor": 0.5,
                    "depth": 200,
                    "substrate": "silicon"
                },
                "output_orders": [-1, 0, 1]
            }
        }


class OptimizationRequest(BaseModel):
    target_order: int = Field(..., description="Target diffraction order to maximize")
    target_type: str = Field("reflection", description="'reflection' or 'transmission'")
    wavelength: float = Field(..., gt=0, description="Wavelength in nm")
    angle_of_incidence: float = Field(0, description="Angle from normal in degrees")
    polarization: str = Field("s", description="'s' or 'p'")
    period_range: List[float] = Field([300, 800], description="[min, max] period in nm")
    fill_factor_range: List[float] = Field([0.2, 0.8], description="[min, max] fill factor")
    depth_range: List[float] = Field([50, 500], description="[min, max] depth in nm")
    num_samples: int = Field(10, ge=3, le=50, description="Samples per parameter")

    class Config:
        json_schema_extra = {
            "example": {
                "target_order": 1,
                "target_type": "reflection",
                "wavelength": 633,
                "angle_of_incidence": 45,
                "polarization": "s",
                "period_range": [400, 700],
                "fill_factor_range": [0.3, 0.7],
                "depth_range": [100, 400],
                "num_samples": 10
            }
        }


class SweepRequest(BaseModel):
    """Sweep a single parameter while holding others fixed."""
    base_params: SimulationRequest
    sweep_param: str = Field(..., description="Parameter to sweep: 'period', 'wavelength', 'fill_factor', 'depth', 'angle'")
    sweep_values: List[float] = Field(..., description="Values to sweep")

    class Config:
        json_schema_extra = {
            "example": {
                "base_params": {
                    "period": 500,
                    "wavelength": 633,
                    "angle_of_incidence": 45,
                    "polarization": "s",
                    "grating_params": {"fill_factor": 0.5, "depth": 200}
                },
                "sweep_param": "period",
                "sweep_values": [400, 450, 500, 550, 600]
            }
        }


# Endpoints

@app.get("/")
def root():
    """Service info."""
    print(f"root() called, S4_AVAILABLE={S4_AVAILABLE}", flush=True)
    return {
        "service": "RCWA Simulation Service",
        "version": "1.0.0",
        "s4_available": S4_AVAILABLE,
        "endpoints": ["/simulate", "/optimize", "/sweep", "/help", "/materials"]
    }


@app.get("/help")
def help_endpoint():
    """Detailed API documentation and usage examples."""
    return {
        "description": "RCWA (Rigorous Coupled-Wave Analysis) simulation service for diffraction gratings",
        "s4_available": S4_AVAILABLE,
        "endpoints": {
            "POST /simulate": {
                "description": "Run a single RCWA simulation",
                "required_params": ["period", "wavelength"],
                "optional_params": ["angle_of_incidence", "polarization", "grating_params", "layers", "num_harmonics", "output_orders"],
                "example": {
                    "curl": 'curl -X POST http://localhost:8001/simulate -H "Content-Type: application/json" -d \'{"period": 500, "wavelength": 633, "angle_of_incidence": 45, "grating_params": {"fill_factor": 0.5, "depth": 200}}\'',
                }
            },
            "POST /optimize": {
                "description": "Grid search optimization to maximize efficiency in a target order",
                "required_params": ["target_order", "wavelength"],
                "example": {
                    "curl": 'curl -X POST http://localhost:8001/optimize -H "Content-Type: application/json" -d \'{"target_order": 1, "target_type": "reflection", "wavelength": 633, "angle_of_incidence": 45, "num_samples": 10}\'',
                }
            },
            "POST /sweep": {
                "description": "Sweep a parameter and return results for each value",
                "required_params": ["base_params", "sweep_param", "sweep_values"],
            },
            "GET /materials": {
                "description": "List available materials and their refractive indices"
            }
        },
        "physics_notes": {
            "grating_equation": "sin(theta_m) = sin(theta_i) + m * lambda / period",
            "parameters": {
                "period": "Grating period in nm. Determines which diffraction orders propagate.",
                "wavelength": "Incident light wavelength in nm.",
                "angle_of_incidence": "Angle from surface normal in degrees.",
                "fill_factor": "Fraction of period occupied by high-index material (0-1).",
                "depth": "Grating groove depth in nm. Affects diffraction efficiency.",
                "polarization": "'s' (TE, E-field parallel to grooves) or 'p' (TM, E-field perpendicular)."
            },
            "efficiency_tips": [
                "For +1 order at 45 deg, period ~ lambda / (1 - sin(45)) ~ 2.4*lambda is a starting point",
                "Optimal depth often near lambda/4 to lambda/2 in the grating material",
                "Fill factor around 0.5 often gives best first-order efficiency",
                "More harmonics (num_harmonics) = more accurate but slower"
            ]
        },
        "example_workflow": [
            "1. Start with /simulate to understand baseline performance",
            "2. Use /sweep to explore parameter dependence",
            "3. Use /optimize for automated parameter search",
            "4. Refine with more simulations around the optimum"
        ]
    }


@app.get("/materials")
def list_materials():
    """List available materials."""
    return {
        "materials": {
            "air": {"n": 1.0, "k": 0.0, "description": "Air/vacuum"},
            "silicon": {"n": 3.88, "k": 0.02, "description": "Silicon at 633nm"},
            "sio2": {"n": 1.46, "k": 0.0, "description": "Silicon dioxide"},
            "glass": {"n": 1.5, "k": 0.0, "description": "Generic glass"},
            "tio2": {"n": 2.5, "k": 0.0, "description": "Titanium dioxide"},
            "gold": {"n": 0.18, "k": 3.0, "description": "Gold at 633nm"},
            "silver": {"n": 0.13, "k": 4.0, "description": "Silver at 633nm"},
        },
        "note": "Refractive indices are approximate values at 633nm. Silicon has wavelength-dependent values in the visible range."
    }


@app.post("/simulate")
def simulate(request: SimulationRequest):
    """
    Run an RCWA simulation.

    Returns diffraction efficiencies for each order in reflection and transmission.
    """
    try:
        # Convert layers if provided
        layers = None
        if request.layers:
            layers = [l.model_dump() for l in request.layers]

        grating_params = None
        if request.grating_params:
            grating_params = request.grating_params.model_dump()

        result = run_rcwa_simulation(
            period=request.period,
            wavelength=request.wavelength,
            angle_of_incidence=request.angle_of_incidence,
            polarization=request.polarization,
            layers=layers,
            grating_params=grating_params,
            num_harmonics=request.num_harmonics,
            output_orders=request.output_orders
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize")
def optimize(request: OptimizationRequest):
    """
    Run grid search optimization to maximize diffraction efficiency.

    Warning: Can be slow for large num_samples (total = num_samples^3 simulations).
    """
    try:
        result = optimize_grating(
            target_order=request.target_order,
            target_type=request.target_type,
            wavelength=request.wavelength,
            angle_of_incidence=request.angle_of_incidence,
            polarization=request.polarization,
            period_range=tuple(request.period_range),
            fill_factor_range=tuple(request.fill_factor_range),
            depth_range=tuple(request.depth_range),
            num_samples=request.num_samples
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sweep")
def sweep(request: SweepRequest):
    """
    Sweep a single parameter and return results for each value.

    Useful for understanding parameter sensitivity.
    """
    try:
        results = []
        base = request.base_params

        for value in request.sweep_values:
            # Copy base params and modify the sweep parameter
            params = {
                "period": base.period,
                "wavelength": base.wavelength,
                "angle_of_incidence": base.angle_of_incidence,
                "polarization": base.polarization,
                "grating_params": base.grating_params.model_dump() if base.grating_params else None,
                "num_harmonics": base.num_harmonics,
                "output_orders": base.output_orders,
            }

            # Apply sweep value
            if request.sweep_param == "period":
                params["period"] = value
            elif request.sweep_param == "wavelength":
                params["wavelength"] = value
            elif request.sweep_param == "angle":
                params["angle_of_incidence"] = value
            elif request.sweep_param == "fill_factor" and params["grating_params"]:
                params["grating_params"]["fill_factor"] = value
            elif request.sweep_param == "depth" and params["grating_params"]:
                params["grating_params"]["depth"] = value
            else:
                raise ValueError(f"Unknown sweep parameter: {request.sweep_param}")

            result = run_rcwa_simulation(**params)
            result["sweep_value"] = value
            results.append(result)

        return {
            "sweep_param": request.sweep_param,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
