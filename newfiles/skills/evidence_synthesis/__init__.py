"""
Evidence Synthesis Skill

A horizontal (cross-domain) skill for scientific evidence gathering,
synthesis, and hypothesis generation.

Components:
- Domain detection and query classification
- Multi-source search orchestration
- Contradiction identification
- Uncertainty quantification
- Hypothesis generation with ranking
- Experimental design templates
"""

from pathlib import Path
from .skill import EvidenceSynthesisSkill, Domain, QueryType

__all__ = [
    'EvidenceSynthesisSkill',
    'Domain',
    'QueryType',
    'get_skill',
]


def get_skill(skill_path: Path = None):
    """Factory function for skill registry discovery."""
    if skill_path is None:
        skill_path = Path(__file__).parent
    return EvidenceSynthesisSkill(skill_path)
