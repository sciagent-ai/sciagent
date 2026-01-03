"""
Workspace Manager - File-Based Working Memory for Complex Research Tasks

Architecture:
- raw/         : Full fetched content (never sent to LLM directly)
- extracted/   : Summaries and key points (LLM reads this)
- analysis/    : Code and results
- output/      : Final deliverables

Key Principle: Fetch once, save forever, read only what you need.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


class WorkspaceManager:
    """Manages file-based working memory for research tasks."""
    
    def __init__(self, base_path: str = "runs/workspace"):
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw"
        self.extracted_path = self.base_path / "extracted"
        self.analysis_path = self.base_path / "analysis"
        self.output_path = self.base_path.parent / "output"
        
        self.manifest_path = self.raw_path / "manifest.json"
        self.manifest: Dict[str, Any] = {"sources": [], "created": None}
        
    def setup(self) -> str:
        """Initialize workspace directories."""
        for path in [self.raw_path, self.extracted_path, self.analysis_path, self.output_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize manifest
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                self.manifest = json.load(f)
        else:
            self.manifest = {
                "sources": [],
                "created": datetime.now().isoformat(),
                "task": None
            }
            self._save_manifest()
        
        # Initialize extracted files
        notes_path = self.extracted_path / "notes.md"
        if not notes_path.exists():
            notes_path.write_text("# Research Notes\n\n")
        
        citations_path = self.extracted_path / "citations.md"
        if not citations_path.exists():
            citations_path.write_text("# Sources & Citations\n\n")
        
        return f"Workspace initialized at {self.base_path}"
    
    def save_raw_content(
        self, 
        content: str, 
        url: str, 
        title: str,
        source_type: str = "web",
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Save raw fetched content to file. Returns source info for citation.
        
        This content is saved but NOT sent to LLM directly.
        Agent should extract key points and save to notes.md instead.
        """
        # Generate source ID
        source_id = len(self.manifest["sources"]) + 1
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        filename = f"source_{source_id:03d}_{content_hash}.md"
        
        # Save raw content
        filepath = self.raw_path / filename
        
        file_content = f"""# Source {source_id}: {title}

**URL:** {url}
**Type:** {source_type}
**Retrieved:** {datetime.now().isoformat()}
**Content Hash:** {content_hash}

---

{content}
"""
        filepath.write_text(file_content)
        
        # Update manifest
        source_entry = {
            "id": source_id,
            "title": title,
            "url": url,
            "type": source_type,
            "filename": filename,
            "retrieved": datetime.now().isoformat(),
            "content_hash": content_hash,
            "char_count": len(content),
            "metadata": metadata or {}
        }
        self.manifest["sources"].append(source_entry)
        self._save_manifest()
        
        return source_entry
    
    def add_extracted_notes(self, source_id: int, notes: str) -> None:
        """Add extracted key points to notes.md (this IS sent to LLM)."""
        notes_path = self.extracted_path / "notes.md"
        
        # Find source info
        source = self.get_source(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")
        
        # Append to notes
        with open(notes_path, 'a') as f:
            f.write(f"\n## [{source_id}] {source['title']}\n")
            f.write(f"*Source: {source['url']}*\n\n")
            f.write(notes)
            f.write("\n")
    
    def add_citation(self, source_id: int, citation_format: str = "standard") -> str:
        """Add source to citations.md and return formatted citation."""
        source = self.get_source(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")
        
        # Format citation
        quality_emoji = {
            'peer_reviewed': '📗',
            'preprint': '📙', 
            'government': '📘',
            'repository': '📂',
            'web': '🌐'
        }.get(source['type'], '🌐')
        
        citation = f"[{source_id}] {quality_emoji} {source['title']}. {source['url']}"
        
        # Append to citations.md
        citations_path = self.extracted_path / "citations.md"
        with open(citations_path, 'a') as f:
            f.write(f"{citation}\n")
        
        return citation
    
    def get_source(self, source_id: int) -> Optional[Dict]:
        """Get source metadata by ID."""
        for source in self.manifest["sources"]:
            if source["id"] == source_id:
                return source
        return None
    
    def read_raw_content(self, source_id: int) -> Optional[str]:
        """Read raw content for a source (use sparingly - only when needed)."""
        source = self.get_source(source_id)
        if not source:
            return None
        
        filepath = self.raw_path / source["filename"]
        if filepath.exists():
            return filepath.read_text()
        return None
    
    def search_raw_content(self, query: str) -> List[Dict]:
        """Search across all raw content for specific terms."""
        results = []
        query_lower = query.lower()
        
        for source in self.manifest["sources"]:
            filepath = self.raw_path / source["filename"]
            if filepath.exists():
                content = filepath.read_text().lower()
                if query_lower in content:
                    # Find relevant snippet
                    idx = content.find(query_lower)
                    start = max(0, idx - 100)
                    end = min(len(content), idx + 200)
                    snippet = content[start:end]
                    
                    results.append({
                        "source_id": source["id"],
                        "title": source["title"],
                        "snippet": f"...{snippet}..."
                    })
        
        return results
    
    def get_notes(self) -> str:
        """Get extracted notes (safe to send to LLM)."""
        notes_path = self.extracted_path / "notes.md"
        if notes_path.exists():
            return notes_path.read_text()
        return ""
    
    def get_citations(self) -> str:
        """Get citations list."""
        citations_path = self.extracted_path / "citations.md"
        if citations_path.exists():
            return citations_path.read_text()
        return ""
    
    def list_sources(self) -> List[Dict]:
        """List all sources (metadata only, not content)."""
        return self.manifest["sources"]
    
    def get_context_for_llm(self, max_chars: int = 4000) -> str:
        """
        Get a context string safe to send to LLM.
        Only includes extracted notes, not raw content.
        """
        notes = self.get_notes()
        
        if len(notes) > max_chars:
            notes = notes[:max_chars] + "\n\n... [truncated, use search for specific content]"
        
        return notes
    
    def _save_manifest(self) -> None:
        """Save manifest to disk."""
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get workspace statistics."""
        total_raw_chars = 0
        for source in self.manifest["sources"]:
            total_raw_chars += source.get("char_count", 0)
        
        notes_chars = len(self.get_notes())
        
        return {
            "num_sources": len(self.manifest["sources"]),
            "total_raw_chars": total_raw_chars,
            "extracted_notes_chars": notes_chars,
            "compression_ratio": f"{notes_chars / max(total_raw_chars, 1):.1%}",
            "sources": [
                {"id": s["id"], "title": s["title"][:50], "type": s["type"]}
                for s in self.manifest["sources"]
            ]
        }


# Convenience functions for agent tools

def setup_workspace(base_path: str = "runs/workspace") -> str:
    """Initialize workspace for a research task."""
    wm = WorkspaceManager(base_path)
    return wm.setup()


def save_source(
    content: str,
    url: str, 
    title: str,
    source_type: str = "web",
    base_path: str = "runs/workspace"
) -> Dict[str, Any]:
    """Save raw content and return source info."""
    wm = WorkspaceManager(base_path)
    return wm.save_raw_content(content, url, title, source_type)


def add_notes(source_id: int, notes: str, base_path: str = "runs/workspace") -> None:
    """Add extracted notes for a source."""
    wm = WorkspaceManager(base_path)
    wm.add_extracted_notes(source_id, notes)


def search_sources(query: str, base_path: str = "runs/workspace") -> List[Dict]:
    """Search across all saved raw content."""
    wm = WorkspaceManager(base_path)
    return wm.search_raw_content(query)


def get_llm_context(base_path: str = "runs/workspace", max_chars: int = 4000) -> str:
    """Get context safe to send to LLM."""
    wm = WorkspaceManager(base_path)
    return wm.get_context_for_llm(max_chars)
