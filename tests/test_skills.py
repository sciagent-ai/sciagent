#!/usr/bin/env python3
"""Test the skill system functionality."""

from sciagent.skill_registry import SkillRegistry
from pathlib import Path

def test_skill_loading():
    """Test that skills can be loaded from the skills directory."""
    print("🧪 Testing skill loading...")
    
    # Create registry and load skills
    registry = SkillRegistry(Path("skills"))
    registry.load_skills()
    
    # Check that skills were loaded
    assert len(registry.skills) > 0, "Should have loaded some skills"
    
    # Check specific skills
    expected_skills = ["software_engineering", "experiment_design", "literature_search"]
    loaded_skills = list(registry.skills.keys())
    
    print(f"✅ Loaded skills: {loaded_skills}")
    
    for skill_name in expected_skills:
        assert skill_name in loaded_skills, f"Should have loaded {skill_name} skill"
    
    print("✅ All expected skills loaded successfully")

def test_skill_triggering():
    """Test that skills are triggered correctly based on task content."""
    print("\n🧪 Testing skill triggering...")
    
    registry = SkillRegistry(Path("skills"))
    registry.load_skills()
    
    # Test software engineering triggers
    swe_task = "Fix the bug in the Python function and add unit tests"
    matching_skills = registry.find_matching_skills(swe_task)
    swe_skill_names = [s.metadata.name for s in matching_skills]
    
    assert "software_engineering" in swe_skill_names, "Should trigger software engineering skill"
    print(f"✅ SWE task triggered: {swe_skill_names}")
    
    # Test experiment design triggers
    experiment_task = "Design a Bayesian optimization experiment to optimize parameters"
    matching_skills = registry.find_matching_skills(experiment_task)
    exp_skill_names = [s.metadata.name for s in matching_skills]
    
    assert "experiment_design" in exp_skill_names, "Should trigger experiment design skill"
    print(f"✅ Experiment task triggered: {exp_skill_names}")
    
    # Test literature search triggers
    lit_task = "Search for recent papers on machine learning and summarize findings"
    matching_skills = registry.find_matching_skills(lit_task)
    lit_skill_names = [s.metadata.name for s in matching_skills]
    
    assert "literature_search" in lit_skill_names, "Should trigger literature search skill"
    print(f"✅ Literature task triggered: {lit_skill_names}")

def test_skill_metadata():
    """Test that skill metadata is loaded correctly."""
    print("\n🧪 Testing skill metadata...")
    
    registry = SkillRegistry(Path("skills"))
    registry.load_skills()
    
    # Check software engineering skill metadata
    swe_skill = registry.get_skill("software_engineering")
    assert swe_skill is not None, "Should find software engineering skill"
    assert swe_skill.metadata.domain == "software_engineering"
    assert "code" in swe_skill.metadata.triggers
    assert "str_replace_editor" in swe_skill.metadata.allowed_tools
    
    # Check experiment design skill metadata
    exp_skill = registry.get_skill("experiment_design")
    assert exp_skill is not None, "Should find experiment design skill"
    assert exp_skill.metadata.domain == "scientific"
    assert exp_skill.metadata.horizontal == True
    assert "experiment" in exp_skill.metadata.triggers
    
    print("✅ Skill metadata loaded correctly")

def test_mcp_tools():
    """Test that FastMCP tools are loaded correctly."""
    print("\n🧪 Testing MCP tools loading...")
    
    registry = SkillRegistry(Path("skills"))
    registry.load_skills()
    
    # Check experiment design MCP tools
    exp_skill = registry.get_skill("experiment_design")
    mcp_tools = exp_skill.get_mcp_tools()
    
    if mcp_tools is not None:
        print("✅ MCP tools loaded for experiment_design skill")
        # Could test tool functionality here if needed
    else:
        print("⚠️ No MCP tools found for experiment_design skill (dependency missing?)")

def test_skill_listing():
    """Test skill listing functionality."""
    print("\n🧪 Testing skill listing...")
    
    registry = SkillRegistry(Path("skills"))
    registry.load_skills()
    
    skills_list = registry.list_skills()
    assert len(skills_list) > 0, "Should return non-empty skills list"
    
    print(f"✅ Found {len(skills_list)} skills:")
    for skill in skills_list:
        print(f"   📚 {skill['name']} ({skill['domain']}) - {skill['description'][:60]}...")

def main():
    """Run all skill system tests."""
    try:
        test_skill_loading()
        test_skill_triggering()
        test_skill_metadata()
        test_mcp_tools()
        test_skill_listing()
        
        print("\n🎉 All skill system tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)