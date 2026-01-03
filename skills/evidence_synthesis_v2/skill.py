"""
Evidence Synthesis Skill v2

Scientific evidence gathering with proper citations and references.
Uses "Search Once, Fetch Deep" strategy for rate-limit-safe operation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from pathlib import Path
from enum import Enum

if TYPE_CHECKING:
    from sciagent.core_agent import CoreAgent

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


@dataclass
class Source:
    """Tracked source for citations."""
    id: int
    title: str
    url: str
    authors: List[str] = field(default_factory=list)
    year: Optional[str] = None
    source_type: str = "web"  # peer_reviewed, preprint, government, web
    journal: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    key_claims: List[str] = field(default_factory=list)
    quality_score: float = 0.5  # 0-1
    
    @property
    def quality_emoji(self) -> str:
        """Return quality indicator emoji."""
        return {
            'peer_reviewed': '📗',
            'preprint': '📙',
            'government': '📘',
            'repository': '📂',
            'encyclopedia': '📖',
            'blog': '📝',
            'web': '🌐',
        }.get(self.source_type, '🌐')
    
    def format_citation(self) -> str:
        """Format as a citation string."""
        parts = []
        
        if self.authors:
            if len(self.authors) > 3:
                parts.append(f"{self.authors[0]} et al.")
            else:
                parts.append(", ".join(self.authors))
        
        parts.append(f'"{self.title}"')
        
        if self.journal:
            parts.append(f"*{self.journal}*")
        
        if self.year:
            parts.append(f"({self.year})")
        
        if self.doi:
            parts.append(f"DOI: {self.doi}")
        
        return " ".join(parts)
    
    def format_reference(self) -> str:
        """Format as a full reference entry."""
        lines = [
            f"[{self.id}] {self.quality_emoji} {self.format_citation()}",
            f"    URL: {self.url}",
        ]
        if self.doi:
            lines.append(f"    DOI: {self.doi}")
        lines.append(f"    Type: {self.source_type}")
        return "\n".join(lines)


class EvidenceSynthesisSkill(Skill):
    """
    Evidence Synthesis Skill with Citation Tracking.
    
    Key features:
    - Domain detection for source prioritization
    - "Search Once, Fetch Deep" strategy
    - Automatic citation tracking
    - Structured output with references
    """
    
    # Domain detection patterns
    DOMAIN_PATTERNS = {
        Domain.CHEMISTRY: [
            r'\b(molecule|compound|reaction|synthesis|catalyst|chemical|organic|inorganic)\b',
            r'\b(SMILES|InChI|reagent|solvent|yield|purity|spectroscopy)\b',
        ],
        Domain.BIOLOGY: [
            r'\b(protein|gene|DNA|RNA|cell|organism|species|CRISPR|genome)\b',
            r'\b(mutation|expression|pathway|sequencing|enzyme)\b',
        ],
        Domain.MEDICINE: [
            r'\b(patient|treatment|therapy|clinical|disease|diagnosis|drug)\b',
            r'\b(efficacy|adverse|trial|placebo|dosage|symptom)\b',
        ],
        Domain.PHYSICS: [
            r'\b(quantum|particle|wave|field|energy|force|photon)\b',
            r'\b(relativity|thermodynamic|electromagnetic)\b',
        ],
        Domain.MATERIALS: [
            r'\b(material|alloy|ceramic|polymer|crystal|battery)\b',
            r'\b(conductivity|strength|hardness|electrolyte)\b',
        ],
        Domain.DATA_SCIENCE: [
            r'\b(machine learning|deep learning|neural network|AI|model|LLM)\b',
            r'\b(accuracy|precision|recall|training|dataset|benchmark)\b',
        ],
        Domain.ENGINEERING: [
            r'\b(design|system|component|structure|mechanism|robot)\b',
            r'\b(efficiency|performance|optimization)\b',
        ],
        Domain.ENVIRONMENTAL: [
            r'\b(climate|environment|ecosystem|pollution|emission)\b',
            r'\b(sustainability|renewable|carbon|biodiversity)\b',
        ],
    }
    
    # Priority sources by domain
    DOMAIN_SOURCES = {
        Domain.CHEMISTRY: ["PubChem", "RSC journals", "ACS publications", "ChemRxiv"],
        Domain.BIOLOGY: ["PubMed", "bioRxiv", "Nature", "Cell", "PNAS"],
        Domain.MEDICINE: ["PubMed", "ClinicalTrials.gov", "Cochrane", "NEJM", "Lancet"],
        Domain.PHYSICS: ["arXiv", "Physical Review", "Nature Physics", "Science"],
        Domain.MATERIALS: ["Materials Project", "Acta Materialia", "Nature Materials"],
        Domain.DATA_SCIENCE: ["arXiv cs.LG", "Papers With Code", "NeurIPS", "ICML"],
        Domain.ENGINEERING: ["IEEE Xplore", "ASME", "technical standards"],
        Domain.ENVIRONMENTAL: ["IPCC", "Nature Climate Change", "EPA"],
        Domain.GENERAL: ["Google Scholar", "Semantic Scholar", "Wikipedia"],
    }

    def __init__(self, skill_path: Path):
        super().__init__(skill_path)
        self.sources: List[Source] = []
        self.detected_domain: Domain = Domain.GENERAL
    
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
    
    def build_comprehensive_query(self, task: str, domain: Domain) -> str:
        """Build a single comprehensive search query."""
        # Extract key terms from task
        # Remove common words and instructions
        stop_patterns = [
            r'\b(create|make|generate|write|build|analyze|research|find|search)\b',
            r'\b(please|could|would|should|need|want)\b',
            r'\b(the|a|an|is|are|was|were|be|been|being)\b',
            r'\b(and|or|but|if|then|else|when|where|how|what|why)\b',
            r'\b(file|output|csv|markdown|md|report|document)\b',
        ]
        
        query = task.lower()
        for pattern in stop_patterns:
            query = re.sub(pattern, ' ', query, flags=re.IGNORECASE)
        
        # Clean up whitespace
        query = ' '.join(query.split())
        
        # Limit length and add useful terms
        words = query.split()[:12]  # Max 12 key words
        
        # Add domain-specific boost terms
        boost_terms = {
            Domain.CHEMISTRY: ["mechanism", "synthesis"],
            Domain.BIOLOGY: ["pathway", "mechanism"],
            Domain.MEDICINE: ["clinical", "efficacy"],
            Domain.PHYSICS: ["theory", "experimental"],
            Domain.MATERIALS: ["properties", "performance"],
            Domain.DATA_SCIENCE: ["benchmark", "comparison"],
            Domain.ENGINEERING: ["design", "analysis"],
            Domain.ENVIRONMENTAL: ["impact", "assessment"],
            Domain.GENERAL: ["review", "comparison"],
        }
        
        # Add one boost term if not already present
        domain_boosts = boost_terms.get(domain, [])
        for boost in domain_boosts:
            if boost not in words:
                words.append(boost)
                break
        
        # Add year for recency
        if "2024" not in words and "2023" not in words:
            words.append("2024")
        
        return ' '.join(words)
    
    def get_search_guidance(self, domain: Domain) -> str:
        """Get domain-specific search guidance."""
        priority_sources = self.DOMAIN_SOURCES.get(domain, self.DOMAIN_SOURCES[Domain.GENERAL])
        
        return f"""
DOMAIN DETECTED: {domain.value}

PRIORITY SOURCES for {domain.value}:
{chr(10).join(f'  - {s}' for s in priority_sources)}

SOURCE QUALITY RANKING:
  📗 Peer-reviewed journals (Nature, Science, Cell, NEJM, etc.) - HIGHEST
  📙 Preprints (arXiv, bioRxiv, medRxiv) - HIGH (but note "not peer-reviewed")
  📘 Government sources (.gov, WHO, CDC) - HIGH
  📂 Data repositories (GitHub datasets) - MEDIUM
  📖 Encyclopedia (Wikipedia) - LOW (for background only)
  🌐 Web/blogs - LOWEST (avoid for key claims)

CITATION REQUIREMENTS:
  - EVERY factual claim needs a citation [N]
  - Use format: "Finding here [1]" or "Multiple studies [1-3] show..."
  - Track all sources in References section
  - Note source quality in your synthesis
"""
    
    def get_output_template(self) -> str:
        """Get the output structure template."""
        return """
OUTPUT STRUCTURE (create these files):

1. evidence_synthesis.md - Main report with:
   - Executive Summary (2-3 sentences, cited)
   - Methods (search query, date, inclusion criteria)
   - Findings (all claims cited)
   - Evidence Quality Assessment table
   - Contradictions & Uncertainties
   - Knowledge Gaps
   - Hypotheses (with citations)
   - References (numbered list with quality indicators)

2. sources.md - Detailed source tracking:
   - Full citation info for each source
   - Key claims extracted from each
   - Quality assessment notes

3. data/extracted_data.csv (if quantitative data found):
   - Columns: source_id, variable, value, unit, sample_size, notes
   - Every row traceable to a source

CITATION FORMAT:
[1] 📗 Author A, Author B. "Title." *Journal*. Year. URL: xxx
[2] 📙 Author C et al. "Title." *bioRxiv*. Year. URL: xxx
"""
    
    def execute(self, task: str, agent: 'CoreAgent') -> Dict[str, Any]:
        """Execute the evidence synthesis skill with citation tracking."""
        try:
            # Detect domain
            domain = self.detect_domain(task)
            self.detected_domain = domain
            
            # Build comprehensive query
            suggested_query = self.build_comprehensive_query(task, domain)
            
            # Get skill instructions
            instructions = self.get_instructions()
            
            # Build enhanced prompt
            base_prompt = agent.build_system_prompt()
            
            enhanced_prompt = f"""{base_prompt}

═══════════════════════════════════════════════════════════════════════════════
ACTIVE SKILL: Evidence Synthesis v2 (with Citations)
═══════════════════════════════════════════════════════════════════════════════

{self.get_search_guidance(domain)}

═══════════════════════════════════════════════════════════════════════════════
SEARCH STRATEGY: Search Once, Fetch Deep
═══════════════════════════════════════════════════════════════════════════════

SUGGESTED COMPREHENSIVE QUERY:
  "{suggested_query}"

SEARCH RULES:
  1. Use MAXIMUM 2 web_search calls for entire task
  2. Combine all key terms into ONE comprehensive query
  3. After search, use web_fetch to get full content from top 3-5 URLs
  4. web_fetch does NOT count against search limit

WORKFLOW:
  1. web_search (comprehensive query) → get URLs
  2. web_fetch (url_1) → full content + metadata
  3. web_fetch (url_2) → full content + metadata  
  4. web_fetch (url_3) → full content + metadata
  5. Synthesize with citations

{self.get_output_template()}

═══════════════════════════════════════════════════════════════════════════════
SKILL INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════

{instructions}

═══════════════════════════════════════════════════════════════════════════════
EXECUTE THE TASK WITH PROPER CITATIONS
═══════════════════════════════════════════════════════════════════════════════
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
                        "domain": domain.value,
                        "suggested_query": suggested_query,
                        "priority_sources": self.DOMAIN_SOURCES.get(domain, []),
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


# Factory function for skill registry
def get_skill(skill_path: Path = None) -> Skill:
    """Factory function for skill registry discovery."""
    if skill_path is None:
        skill_path = Path(__file__).parent
    return EvidenceSynthesisSkill(skill_path)
