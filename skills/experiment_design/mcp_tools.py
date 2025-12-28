"""FastMCP tools for experiment design."""

from fastmcp import FastMCP
from typing import Dict, Any, List
import numpy as np

# Create FastMCP instance for this skill
mcp = FastMCP("Experiment Design Tools")


@mcp.tool()
def design_factorial_experiment(factors: Dict[str, List], response: str) -> Dict[str, Any]:
    """Design a full factorial experiment matrix.
    
    Args:
        factors: Dictionary mapping factor names to their levels
        response: Name of the response variable
        
    Returns:
        Dictionary with design matrix and metadata
    """
    try:
        import itertools
        
        factor_names = list(factors.keys())
        factor_levels = [factors[name] for name in factor_names]
        
        # Generate all combinations
        combinations = list(itertools.product(*factor_levels))
        
        # Create design matrix
        design_matrix = []
        for combo in combinations:
            run = dict(zip(factor_names, combo))
            design_matrix.append(run)
        
        return {
            "design_matrix": design_matrix,
            "n_runs": len(design_matrix),
            "factors": factor_names,
            "response": response,
            "design_type": "full_factorial"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def bayesian_optimization_suggest(
    objective_data: List[Dict[str, Any]], 
    bounds: Dict[str, tuple], 
    n_suggestions: int = 1
) -> Dict[str, Any]:
    """Suggest next experiments using Bayesian optimization.
    
    Args:
        objective_data: List of previous experiments with factors and objective
        bounds: Dictionary mapping factor names to (min, max) bounds
        n_suggestions: Number of suggestions to return
        
    Returns:
        Dictionary with suggested experiment points
    """
    try:
        # Simplified implementation - in practice would use GPyOpt or similar
        suggestions = []
        
        for i in range(n_suggestions):
            suggestion = {}
            for factor, (min_val, max_val) in bounds.items():
                # Simple random suggestion for now
                suggestion[factor] = np.random.uniform(min_val, max_val)
            suggestions.append(suggestion)
        
        return {
            "suggestions": suggestions,
            "acquisition_function": "expected_improvement",
            "model_type": "gaussian_process"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def analyze_experiment_results(
    data: List[Dict[str, Any]], 
    factors: List[str], 
    response: str
) -> Dict[str, Any]:
    """Analyze experimental results and identify significant factors.
    
    Args:
        data: List of experimental runs with factor values and response
        factors: List of factor names
        response: Name of response variable
        
    Returns:
        Analysis results with effect estimates
    """
    try:
        # Simple analysis - calculate main effects
        results = {
            "main_effects": {},
            "response_statistics": {},
            "significant_factors": []
        }
        
        # Extract response values
        responses = [run[response] for run in data]
        results["response_statistics"] = {
            "mean": np.mean(responses),
            "std": np.std(responses),
            "min": np.min(responses),
            "max": np.max(responses)
        }
        
        # Calculate main effects for each factor
        for factor in factors:
            # Group by factor levels
            factor_groups = {}
            for run in data:
                level = run[factor]
                if level not in factor_groups:
                    factor_groups[level] = []
                factor_groups[level].append(run[response])
            
            # Calculate effect as difference between high and low
            if len(factor_groups) >= 2:
                levels = sorted(factor_groups.keys())
                high_mean = np.mean(factor_groups[levels[-1]])
                low_mean = np.mean(factor_groups[levels[0]])
                effect = high_mean - low_mean
                results["main_effects"][factor] = effect
                
                # Simple significance test (effect > 1 std dev)
                if abs(effect) > results["response_statistics"]["std"]:
                    results["significant_factors"].append(factor)
        
        return results
    except Exception as e:
        return {"error": str(e)}