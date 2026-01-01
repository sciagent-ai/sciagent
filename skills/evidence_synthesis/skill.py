"""
Evidence Synthesis Skill Implementation

Custom skill class that adds:
- Domain detection from query
- Multi-source search orchestration
- Contradiction detection
- Uncertainty quantification
- Hypothesis generation
- Experimental design templates
"""

from __future__ import annotations

import re
import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
from enum import Enum

if TYPE_CHECKING:
    from sciagent.core_agent import CoreAgent

# Import base skill if available, otherwise define locally
try:
    from sciagent.skill import Skill, SkillMetadata
except ImportError:
    from skill import Skill, SkillMetadata


class Domain(Enum):
    """Scientific domains for source prioritization."""
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    MEDICINE = "medicine"
    PHYSICS = "physics"
    MATERIALS = "materials"
    DATA_SCIENCE = "data_science"
    ENGINEERING = "engineering"
    ENVIRONMENTAL = "environmental"
    GENERAL = "general"


class QueryType(Enum):
    """Types of research queries."""
    FACTUAL = "factual"           # What is X?
    COMPARATIVE = "comparative"    # X vs Y?
    PREDICTIVE = "predictive"      # What will happen?
    MECHANISTIC = "mechanistic"    # How/why does X work?
    METHODOLOGICAL = "methodological"  # How to do X?
    EXPLORATORY = "exploratory"    # What's the state of X?


@dataclass
class EvidenceItem:
    """Single piece of evidence from a source."""
    source_title: str
    source_url: str
    source_type: str  # peer_reviewed, preprint, dataset, blog, etc.
    year: Optional[int]
    claim: str
    confidence: float  # 0-1
    sample_size: Optional[int] = None
    effect_size: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    methodology: Optional[str] = None
    limitations: List[str] = field(default_factory=list)


@dataclass
class Contradiction:
    """Identified contradiction between sources."""
    claim_topic: str
    source_a: str
    position_a: str
    source_b: str
    position_b: str
    possible_reasons: List[str]
    resolution_confidence: float  # 0-1, how confident we are in resolving


@dataclass
class Hypothesis:
    """Generated hypothesis with supporting information."""
    statement: str
    evidence_base: List[str]
    prediction: str
    contradicting_evidence: str
    confidence: str  # Low/Medium/High
    novelty_score: int  # 1-10
    testability_score: int  # 1-10
    impact_score: int  # 1-10
    
    @property
    def composite_score(self) -> float:
        """Combined score for ranking."""
        return (self.novelty_score + self.testability_score + self.impact_score) / 3


class EvidenceSynthesisSkill(Skill):
    """
    Advanced evidence synthesis skill for scientific research.
    
    Provides:
    - Intelligent domain detection
    - Multi-source search orchestration
    - Contradiction identification
    - Uncertainty quantification
    - Hypothesis generation
    - Experimental design templates
    """
    
    # Domain detection patterns
    DOMAIN_PATTERNS = {
        Domain.CHEMISTRY: [
            r'\b(molecule|compound|reaction|synthesis|catalyst|polymer|chemical|organic|inorganic)\b',
            r'\b(SMILES|InChI|mol|reagent|solvent|yield|purity)\b',
            r'\b(spectroscopy|chromatography|NMR|mass spec)\b',
        ],
        Domain.BIOLOGY: [
            r'\b(protein|gene|DNA|RNA|cell|organism|species|evolution)\b',
            r'\b(mutation|expression|pathway|signaling|receptor)\b',
            r'\b(sequencing|CRISPR|PCR|blot|assay)\b',
        ],
        Domain.MEDICINE: [
            r'\b(patient|treatment|therapy|clinical|disease|diagnosis)\b',
            r'\b(drug|dosage|efficacy|adverse|trial|placebo)\b',
            r'\b(symptom|prognosis|mortality|morbidity)\b',
        ],
        Domain.PHYSICS: [
            r'\b(quantum|particle|wave|field|energy|force|momentum)\b',
            r'\b(relativity|thermodynamic|electromagnetic|photon)\b',
            r'\b(simulation|model|theory|equation)\b',
        ],
        Domain.MATERIALS: [
            r'\b(material|alloy|ceramic|polymer|composite|crystal)\b',
            r'\b(conductivity|strength|hardness|ductility|thermal)\b',
            r'\b(battery|solar|semiconductor|superconductor)\b',
        ],
        Domain.DATA_SCIENCE: [
            r'\b(machine learning|deep learning|neural network|AI|model)\b',
            r'\b(accuracy|precision|recall|F1|AUROC|loss)\b',
            r'\b(training|dataset|benchmark|feature|embedding)\b',
        ],
        Domain.ENGINEERING: [
            r'\b(design|system|component|structure|mechanism)\b',
            r'\b(efficiency|performance|optimization|constraint)\b',
            r'\b(CAD|FEA|CFD|simulation|prototype)\b',
        ],
        Domain.ENVIRONMENTAL: [
            r'\b(climate|environment|ecosystem|pollution|emission)\b',
            r'\b(sustainability|renewable|carbon|biodiversity)\b',
            r'\b(temperature|precipitation|sea level|ice)\b',
        ],
    }
    
    # Query type patterns
    QUERY_TYPE_PATTERNS = {
        QueryType.FACTUAL: [r'^what (is|are)\b', r'\bdefine\b', r'\bmeaning of\b'],
        QueryType.COMPARATIVE: [r'\bvs\.?\b', r'\bcompare\b', r'\bdifference between\b', r'\bversus\b'],
        QueryType.PREDICTIVE: [r'\bpredict\b', r'\bforecast\b', r'\bfuture\b', r'\bwill\b.*\b(happen|be)\b'],
        QueryType.MECHANISTIC: [r'\bhow does\b', r'\bwhy does\b', r'\bmechanism\b', r'\bcause\b'],
        QueryType.METHODOLOGICAL: [r'\bhow to\b', r'\bmethod\b', r'\bprotocol\b', r'\bprocedure\b'],
        QueryType.EXPLORATORY: [r'\bstate of\b', r'\boverview\b', r'\blandscape\b', r'\bcurrent\b'],
    }
    
    # Source type quality scores
    SOURCE_QUALITY = {
        'peer_reviewed': 1.0,
        'meta_analysis': 0.95,
        'systematic_review': 0.95,
        'preprint': 0.7,
        'conference': 0.75,
        'thesis': 0.7,
        'government': 0.85,
        'dataset': 0.8,
        'documentation': 0.75,
        'blog': 0.4,
        'forum': 0.3,
        'unknown': 0.5,
    }

    def __init__(self, skill_path: Path):
        super().__init__(skill_path)
        self.evidence_items: List[EvidenceItem] = []
        self.contradictions: List[Contradiction] = []
        self.hypotheses: List[Hypothesis] = []
        self.detected_domain: Domain = Domain.GENERAL
        self.detected_query_type: QueryType = QueryType.EXPLORATORY
    
    def detect_domain(self, query: str) -> Domain:
        """Detect the scientific domain from query text."""
        query_lower = query.lower()
        scores = {}
        
        for domain, patterns in self.DOMAIN_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower, re.IGNORECASE))
                score += matches
            if score > 0:
                scores[domain] = score
        
        if not scores:
            return Domain.GENERAL
        
        return max(scores, key=scores.get)
    
    def detect_query_type(self, query: str) -> QueryType:
        """Detect the type of research query."""
        query_lower = query.lower()
        
        for query_type, patterns in self.QUERY_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    return query_type
        
        return QueryType.EXPLORATORY
    
    def get_domain_search_queries(self, topic: str, domain: Domain) -> List[str]:
        """Generate domain-specific search queries."""
        base_queries = [
            f"{topic}",
            f"{topic} review",
            f"{topic} 2024",
            f"{topic} meta-analysis",
        ]
        
        domain_queries = {
            Domain.CHEMISTRY: [
                f"{topic} synthesis mechanism",
                f"{topic} spectroscopy characterization",
                f"pubchem {topic}",
            ],
            Domain.BIOLOGY: [
                f"{topic} pathway",
                f"{topic} gene expression",
                f"pubmed {topic}",
                f"biorxiv {topic}",
            ],
            Domain.MEDICINE: [
                f"{topic} clinical trial",
                f"{topic} treatment efficacy",
                f"pubmed {topic} randomized",
                f"{topic} adverse effects",
            ],
            Domain.PHYSICS: [
                f"arxiv {topic}",
                f"{topic} theoretical model",
                f"{topic} experimental validation",
            ],
            Domain.MATERIALS: [
                f"{topic} properties characterization",
                f"materials project {topic}",
                f"{topic} synthesis fabrication",
            ],
            Domain.DATA_SCIENCE: [
                f"arxiv {topic} machine learning",
                f"{topic} benchmark dataset",
                f"papers with code {topic}",
                f"{topic} state of the art",
            ],
            Domain.ENGINEERING: [
                f"{topic} design optimization",
                f"{topic} simulation analysis",
                f"ieee {topic}",
            ],
            Domain.ENVIRONMENTAL: [
                f"{topic} climate impact",
                f"{topic} sustainability",
                f"IPCC {topic}",
            ],
        }
        
        return base_queries + domain_queries.get(domain, [])
    
    def classify_source_type(self, url: str, title: str) -> str:
        """Classify the type and quality of a source."""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Check URL patterns
        if 'pubmed' in url_lower or 'ncbi.nlm.nih' in url_lower:
            return 'peer_reviewed'
        if 'arxiv.org' in url_lower:
            return 'preprint'
        if 'biorxiv.org' in url_lower or 'medrxiv.org' in url_lower:
            return 'preprint'
        if '.gov' in url_lower:
            return 'government'
        if 'ieee' in url_lower:
            return 'peer_reviewed'
        if 'nature.com' in url_lower or 'science.org' in url_lower:
            return 'peer_reviewed'
        if 'github.com' in url_lower:
            return 'dataset' if 'data' in title_lower else 'documentation'
        if 'medium.com' in url_lower or 'blog' in url_lower:
            return 'blog'
        if 'stackoverflow' in url_lower or 'reddit' in url_lower:
            return 'forum'
        
        # Check title patterns
        if 'meta-analysis' in title_lower:
            return 'meta_analysis'
        if 'systematic review' in title_lower:
            return 'systematic_review'
        if 'thesis' in title_lower or 'dissertation' in title_lower:
            return 'thesis'
        
        return 'unknown'
    
    def find_contradictions(self, evidence: List[EvidenceItem]) -> List[Contradiction]:
        """Identify contradictions between evidence items."""
        contradictions = []
        
        # Group evidence by topic/claim keywords
        # This is a simplified version - real implementation would use NLP
        for i, item_a in enumerate(evidence):
            for item_b in evidence[i+1:]:
                # Check for potential contradictions
                # Look for opposing qualifiers
                opposing_patterns = [
                    (r'\bincrease\b', r'\bdecrease\b'),
                    (r'\bpositive\b', r'\bnegative\b'),
                    (r'\beffective\b', r'\bineffective\b'),
                    (r'\bsignificant\b', r'\bnot significant\b'),
                    (r'\bbeneficial\b', r'\bharmful\b'),
                    (r'\bsupports\b', r'\bcontradicts\b'),
                ]
                
                for pattern_a, pattern_b in opposing_patterns:
                    a_has_first = bool(re.search(pattern_a, item_a.claim, re.I))
                    a_has_second = bool(re.search(pattern_b, item_a.claim, re.I))
                    b_has_first = bool(re.search(pattern_a, item_b.claim, re.I))
                    b_has_second = bool(re.search(pattern_b, item_b.claim, re.I))
                    
                    if (a_has_first and b_has_second) or (a_has_second and b_has_first):
                        contradictions.append(Contradiction(
                            claim_topic=self._extract_topic(item_a.claim, item_b.claim),
                            source_a=item_a.source_title,
                            position_a=item_a.claim[:200],
                            source_b=item_b.source_title,
                            position_b=item_b.claim[:200],
                            possible_reasons=[
                                "Different study populations",
                                "Different methodologies",
                                "Different time periods",
                                "Different definitions/measurements",
                            ],
                            resolution_confidence=0.5
                        ))
        
        return contradictions
    
    def _extract_topic(self, claim_a: str, claim_b: str) -> str:
        """Extract common topic from two claims."""
        # Simple word overlap - would use NLP in production
        words_a = set(claim_a.lower().split())
        words_b = set(claim_b.lower().split())
        common = words_a & words_b
        # Remove stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                      'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                      'can', 'of', 'in', 'to', 'for', 'on', 'with', 'at', 'by',
                      'from', 'as', 'into', 'through', 'during', 'before', 'after',
                      'above', 'below', 'between', 'under', 'again', 'further',
                      'then', 'once', 'that', 'this', 'these', 'those', 'and', 'but'}
        common = common - stop_words
        return ' '.join(list(common)[:5]) if common else "general topic"
    
    def calculate_overall_confidence(self, evidence: List[EvidenceItem]) -> Tuple[float, Dict[str, Any]]:
        """Calculate overall confidence in findings with breakdown."""
        if not evidence:
            return 0.0, {"reason": "No evidence collected"}
        
        # Weight by source quality
        weighted_sum = 0
        total_weight = 0
        
        factors = {
            "source_quality_avg": 0,
            "sample_size_factor": 0,
            "recency_factor": 0,
            "agreement_factor": 0,
            "n_sources": len(evidence),
        }
        
        for item in evidence:
            quality = self.SOURCE_QUALITY.get(item.source_type, 0.5)
            weighted_sum += item.confidence * quality
            total_weight += quality
            factors["source_quality_avg"] += quality
        
        factors["source_quality_avg"] /= len(evidence)
        
        # Adjust for sample sizes if available
        sample_sizes = [e.sample_size for e in evidence if e.sample_size]
        if sample_sizes:
            avg_sample = sum(sample_sizes) / len(sample_sizes)
            factors["sample_size_factor"] = min(1.0, avg_sample / 1000)  # 1000 as "good" sample
        
        # Adjust for contradictions
        n_contradictions = len(self.contradictions)
        if n_contradictions > 0:
            factors["agreement_factor"] = max(0.3, 1.0 - (n_contradictions * 0.15))
        else:
            factors["agreement_factor"] = 1.0
        
        base_confidence = weighted_sum / total_weight if total_weight > 0 else 0.5
        
        # Apply adjustment factors
        adjusted_confidence = base_confidence * factors["agreement_factor"]
        
        # More sources = more confidence (with diminishing returns)
        source_bonus = min(0.2, factors["n_sources"] * 0.02)
        adjusted_confidence = min(0.95, adjusted_confidence + source_bonus)
        
        return adjusted_confidence, factors
    
    def generate_search_strategy(self, query: str) -> Dict[str, Any]:
        """Generate a complete search strategy based on query analysis."""
        domain = self.detect_domain(query)
        query_type = self.detect_query_type(query)
        
        # Extract main topic (simplified)
        topic = re.sub(r'^(research|analyze|find|search for|investigate)\s+', '', query, flags=re.I)
        topic = re.sub(r'\s+(and|then|also).*$', '', topic, flags=re.I)
        topic = topic.strip()[:100]  # Limit length
        
        strategy = {
            "domain": domain.value,
            "query_type": query_type.value,
            "topic": topic,
            "search_queries": self.get_domain_search_queries(topic, domain),
            "priority_sources": self._get_priority_sources(domain),
            "expected_evidence_types": self._get_expected_evidence(query_type),
            "time_range": self._determine_time_range(query),
            "analysis_approach": self._get_analysis_approach(query_type),
        }
        
        return strategy
    
    def _get_priority_sources(self, domain: Domain) -> List[str]:
        """Get priority sources for a domain."""
        sources = {
            Domain.CHEMISTRY: ["PubChem", "Materials Project", "RSC journals"],
            Domain.BIOLOGY: ["PubMed", "bioRxiv", "UniProt", "GenBank"],
            Domain.MEDICINE: ["PubMed", "ClinicalTrials.gov", "Cochrane Library"],
            Domain.PHYSICS: ["arXiv", "Physical Review", "IEEE"],
            Domain.MATERIALS: ["Materials Project", "ICSD", "arXiv cond-mat"],
            Domain.DATA_SCIENCE: ["arXiv cs.LG", "Papers With Code", "OpenML"],
            Domain.ENGINEERING: ["IEEE Xplore", "ASME", "technical standards"],
            Domain.ENVIRONMENTAL: ["IPCC", "EPA", "Nature Climate Change"],
            Domain.GENERAL: ["Google Scholar", "Semantic Scholar", "arXiv"],
        }
        return sources.get(domain, sources[Domain.GENERAL])
    
    def _get_expected_evidence(self, query_type: QueryType) -> List[str]:
        """Get expected evidence types for query type."""
        evidence_types = {
            QueryType.FACTUAL: ["definitions", "measurements", "established facts"],
            QueryType.COMPARATIVE: ["benchmarks", "head-to-head studies", "meta-analyses"],
            QueryType.PREDICTIVE: ["time series data", "models", "forecasts"],
            QueryType.MECHANISTIC: ["pathway studies", "mechanistic models", "experiments"],
            QueryType.METHODOLOGICAL: ["protocols", "tutorials", "best practices"],
            QueryType.EXPLORATORY: ["reviews", "surveys", "state-of-the-art papers"],
        }
        return evidence_types.get(query_type, ["general literature"])
    
    def _determine_time_range(self, query: str) -> str:
        """Determine appropriate time range for search."""
        query_lower = query.lower()
        
        if any(w in query_lower for w in ['recent', 'latest', '2024', '2025', 'current']):
            return "last_2_years"
        if any(w in query_lower for w in ['history', 'historical', 'evolution']):
            return "all_time"
        if any(w in query_lower for w in ['trend', 'over time']):
            return "last_10_years"
        
        # Default based on domain
        if self.detected_domain in [Domain.DATA_SCIENCE]:
            return "last_3_years"  # Fast-moving field
        
        return "last_5_years"
    
    def _get_analysis_approach(self, query_type: QueryType) -> str:
        """Get recommended analysis approach."""
        approaches = {
            QueryType.FACTUAL: "Collect and verify facts from multiple authoritative sources",
            QueryType.COMPARATIVE: "Create comparison matrix with quantitative metrics",
            QueryType.PREDICTIVE: "Build or validate predictive models with uncertainty bounds",
            QueryType.MECHANISTIC: "Map causal pathways and identify key mechanisms",
            QueryType.METHODOLOGICAL: "Compare protocols and identify best practices",
            QueryType.EXPLORATORY: "Synthesize landscape and identify gaps",
        }
        return approaches.get(query_type, "General evidence synthesis")
    
    def execute(self, task: str, agent: 'CoreAgent') -> Dict[str, Any]:
        """Execute the evidence synthesis skill."""
        try:
            # Phase 1: Analyze and plan
            strategy = self.generate_search_strategy(task)
            self.detected_domain = Domain(strategy["domain"])
            self.detected_query_type = QueryType(strategy["query_type"])
            
            # Get skill-specific instructions
            instructions = self.get_instructions()
            
            # Build enhanced prompt with strategy
            base_prompt = agent.build_system_prompt()
            enhanced_prompt = f"""{base_prompt}

ACTIVE SKILL: {self.metadata.name}
SKILL DOMAIN: {self.metadata.domain}

DETECTED RESEARCH CONTEXT:
- Scientific Domain: {strategy['domain']}
- Query Type: {strategy['query_type']}
- Topic: {strategy['topic']}
- Time Range: {strategy['time_range']}
- Analysis Approach: {strategy['analysis_approach']}

PRIORITY SOURCES: {', '.join(strategy['priority_sources'])}

RECOMMENDED SEARCH QUERIES:
{chr(10).join(f'- {q}' for q in strategy['search_queries'][:8])}

EXPECTED EVIDENCE TYPES: {', '.join(strategy['expected_evidence_types'])}

SKILL-SPECIFIC GUIDANCE:
{instructions}

Execute the research task following the evidence synthesis workflow.
Create all required output artifacts (evidence_synthesis.md, hypotheses.md, etc.)
"""
            
            # Execute with enhanced context
            original_prompt_method = agent.build_system_prompt
            agent.build_system_prompt = lambda: enhanced_prompt
            
            try:
                result = agent.execute_task(task)
                
                return {
                    "success": result.get("success", True),
                    "result": result,
                    "tools_used": result.get("tools_used", []),
                    "duration": result.get("duration", 0.0),
                    "errors": result.get("errors", []),
                    "research_context": {
                        "domain": strategy["domain"],
                        "query_type": strategy["query_type"],
                        "topic": strategy["topic"],
                    }
                }
            finally:
                agent.build_system_prompt = original_prompt_method
                
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "tools_used": [],
                "duration": 0.0,
                "errors": [str(e)]
            }


def get_skill(skill_path: Path) -> Skill:
    """Factory function for skill registry."""
    return EvidenceSynthesisSkill(skill_path)
