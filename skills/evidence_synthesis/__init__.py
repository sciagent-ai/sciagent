"""
Evidence Synthesis Skill v2

Scientific evidence gathering with proper citations and references.
Uses "Search Once, Fetch Deep" strategy for reliable operation.
"""

from pathlib import Path
from .skill import EvidenceSynthesisSkill, Domain, Source, get_skill

__all__ = [
    'EvidenceSynthesisSkill',
    'Domain', 
    'Source',
    'get_skill',
]
