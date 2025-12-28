#!/usr/bin/env python3
"""Test lazy loading functionality for skill registry."""

import time
import tempfile
import yaml
from pathlib import Path
from sciagent.skill_registry import SkillRegistry

def create_test_skills(skills_dir: Path) -> None:
    """Create test skills for demonstration."""
    
    # Software engineering skill
    swe_dir = skills_dir / "software_engineering"
    swe_dir.mkdir()
    
    with open(swe_dir / "metadata.yaml", 'w') as f:
        yaml.dump({
            "name": "software_engineering",
            "description": "Software development and debugging tasks",
            "version": "1.0.0",
            "triggers": ["code", "debug", "fix", "software", "programming"],
            "allowed_tools": ["str_replace_editor", "bash", "grep_search"],
            "domain": "software_engineering",
            "horizontal": False
        }, f)
    
    with open(swe_dir / "instructions.md", 'w') as f:
        f.write("# Software Engineering Skill\n\nHelp with coding tasks.")
    
    # Literature search skill
    lit_dir = skills_dir / "literature_search"
    lit_dir.mkdir()
    
    with open(lit_dir / "metadata.yaml", 'w') as f:
        yaml.dump({
            "name": "literature_search",
            "description": "Search and analyze scientific literature",
            "version": "1.0.0", 
            "triggers": ["paper", "research", "literature", "study", "publication"],
            "allowed_tools": ["web_search", "web_fetch"],
            "domain": "scientific",
            "horizontal": True
        }, f)
    
    with open(lit_dir / "instructions.md", 'w') as f:
        f.write("# Literature Search Skill\n\nHelp with research tasks.")

    # Data analysis skill
    data_dir = skills_dir / "data_analysis"
    data_dir.mkdir()
    
    with open(data_dir / "metadata.yaml", 'w') as f:
        yaml.dump({
            "name": "data_analysis",
            "description": "Analyze and visualize data",
            "version": "1.0.0",
            "triggers": ["analyze", "data", "plot", "visualize", "statistics"],
            "allowed_tools": ["notebook_edit", "create_summary"],
            "domain": "scientific",
            "horizontal": True
        }, f)
    
    with open(data_dir / "instructions.md", 'w') as f:
        f.write("# Data Analysis Skill\n\nHelp with data analysis tasks.")

def test_eager_loading():
    """Test traditional eager loading."""
    print("🧪 Testing eager loading...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        create_test_skills(skills_dir)
        
        # Create registry with eager loading
        start_time = time.time()
        registry = SkillRegistry(skills_dir, lazy_loading=False)
        registry.load_skills()
        loading_time = time.time() - start_time
        
        # Test skill discovery
        start_time = time.time()
        skills = registry.find_matching_skills("Fix the bug in the Python code")
        match_time = time.time() - start_time
        
        print(f"  ⏱️ Loading time: {loading_time:.3f}s")
        print(f"  ⏱️ Matching time: {match_time:.3f}s")
        print(f"  📚 Skills loaded: {len(registry.skills)}")
        print(f"  🎯 Matching skills: {[s.metadata.name for s in skills]}")
        
        return loading_time, match_time, len(registry.skills)

def test_lazy_loading():
    """Test lazy loading with pre-filtering."""
    print("\n🧪 Testing lazy loading...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        create_test_skills(skills_dir)
        
        # Create registry with lazy loading
        start_time = time.time()
        registry = SkillRegistry(skills_dir, lazy_loading=True)
        registry.load_skills()
        loading_time = time.time() - start_time
        
        # Test skill discovery
        start_time = time.time()
        skills = registry.find_matching_skills("Fix the bug in the Python code")
        match_time = time.time() - start_time
        
        # Get lazy loading stats
        stats = registry.get_lazy_loading_stats()
        
        print(f"  ⏱️ Loading time: {loading_time:.3f}s")
        print(f"  ⏱️ Matching time: {match_time:.3f}s")
        print(f"  📚 Skills discovered: {stats['total_skills_discovered']}")
        print(f"  💾 Skills loaded: {stats['skills_loaded']}")
        print(f"  💡 Memory saved: {stats['memory_saved_percentage']:.1f}%")
        print(f"  🎯 Matching skills: {[s.metadata.name for s in skills]}")
        
        # Test preloading
        registry.preload_frequent_skills(["literature_search"])
        stats_after_preload = registry.get_lazy_loading_stats()
        print(f"  📦 After preload: {stats_after_preload['skills_loaded']} loaded")
        
        return loading_time, match_time, stats['total_skills_discovered']

def test_pre_filtering():
    """Test pre-filtering performance."""
    print("\n🧪 Testing pre-filtering...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        create_test_skills(skills_dir)
        
        registry = SkillRegistry(skills_dir, lazy_loading=True)
        registry.load_skills()
        
        # Test different task types
        test_tasks = [
            "Fix the bug in my Python code",
            "Search for papers on machine learning",
            "Analyze this dataset and create plots",
            "Write documentation for the API",
            "Deploy the application to production"
        ]
        
        print("  🔍 Pre-filtering results:")
        for task in test_tasks:
            candidates = registry._prefilter_skills(task)
            print(f"    '{task[:30]}...' → {candidates}")

def main():
    """Run all tests and compare performance."""
    print("🚀 Testing Lazy Skill Loading Implementation")
    print("=" * 50)
    
    # Test eager loading
    eager_load_time, eager_match_time, eager_skills = test_eager_loading()
    
    # Test lazy loading  
    lazy_load_time, lazy_match_time, lazy_skills = test_lazy_loading()
    
    # Test pre-filtering
    test_pre_filtering()
    
    # Performance comparison
    print(f"\n📊 Performance Comparison:")
    print(f"  Loading time improvement: {((eager_load_time - lazy_load_time) / eager_load_time * 100):.1f}%")
    print(f"  Matching time difference: {((lazy_match_time - eager_match_time) / eager_match_time * 100):.1f}%")
    print(f"  Skills discovered: {lazy_skills} (same as eager: {eager_skills})")
    
    if lazy_load_time < eager_load_time:
        print("  ✅ Lazy loading is faster!")
    else:
        print("  ⚠️ Lazy loading is slower (overhead may be due to small test size)")

if __name__ == "__main__":
    main()