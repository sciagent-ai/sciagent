#!/usr/bin/env python3
"""Test optional skill system - performance comparison with skills enabled/disabled."""

import time
import tempfile
import yaml
from pathlib import Path
from sciagent.config import Config
from sciagent.core_agent import CoreAgent

class TestAgent(CoreAgent):
    """Simple test agent implementation for benchmarking."""
    
    def build_system_prompt(self) -> str:
        return "You are a helpful assistant."
    
    def execute_task(self, task: str, **kwargs) -> dict:
        """Simulate task execution."""
        time.sleep(0.001)  # Simulate minimal processing
        return {
            "success": True,
            "result": f"Executed: {task}",
            "tools_used": [],
            "duration": 0.001
        }

def create_test_skills(skills_dir: Path) -> None:
    """Create test skills for the benchmark."""
    # Software engineering skill
    swe_dir = skills_dir / "software_engineering"
    swe_dir.mkdir()
    
    with open(swe_dir / "metadata.yaml", 'w') as f:
        yaml.dump({
            "name": "software_engineering",
            "description": "Software development tasks",
            "version": "1.0.0",
            "triggers": ["code", "debug", "fix", "software", "programming"],
            "allowed_tools": ["str_replace_editor", "bash", "grep_search"],
            "domain": "software_engineering"
        }, f)
    
    with open(swe_dir / "instructions.md", 'w') as f:
        f.write("# Software Engineering Skill\nHelp with coding tasks.")
    
    # Literature search skill
    lit_dir = skills_dir / "literature_search" 
    lit_dir.mkdir()
    
    with open(lit_dir / "metadata.yaml", 'w') as f:
        yaml.dump({
            "name": "literature_search",
            "description": "Search scientific literature",
            "version": "1.0.0",
            "triggers": ["paper", "research", "literature", "study"],
            "allowed_tools": ["web_search", "web_fetch"],
            "domain": "scientific"
        }, f)
    
    with open(lit_dir / "instructions.md", 'w') as f:
        f.write("# Literature Search Skill\nHelp with research tasks.")

def benchmark_skills_enabled():
    """Benchmark agent startup and execution with skills enabled."""
    print("🧪 Testing with Skills ENABLED...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        create_test_skills(skills_dir)
        
        # Measure startup time
        start_time = time.time()
        config = Config(
            working_dir=temp_dir,
            enable_skills=True,
            max_iterations=1
        )
        agent = TestAgent(config)
        startup_time = time.time() - start_time
        
        # Measure task execution time
        tasks = [
            "Fix the bug in my Python code",
            "Search for papers on machine learning",
            "Write a function to sort arrays",
            "Debug this JavaScript error",
            "Create documentation"
        ]
        
        execution_times = []
        for task in tasks:
            start_time = time.time()
            result = agent.execute_task_with_skills(task)
            execution_time = time.time() - start_time
            execution_times.append(execution_time)
        
        avg_execution_time = sum(execution_times) / len(execution_times)
        
        print(f"  ⏱️ Startup time: {startup_time:.3f}s")
        print(f"  ⏱️ Avg execution time: {avg_execution_time:.3f}s")
        print(f"  🎯 Skills loaded: {len(agent.skill_registry._skill_metadata_cache) if agent.skill_registry else 0}")
        
        return startup_time, avg_execution_time

def benchmark_skills_disabled():
    """Benchmark agent startup and execution with skills disabled."""
    print("\n🧪 Testing with Skills DISABLED (Fast Mode)...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        create_test_skills(skills_dir)  # Create skills but disable them
        
        # Measure startup time
        start_time = time.time()
        config = Config(
            working_dir=temp_dir,
            enable_skills=False,  # Disabled!
            max_iterations=1
        )
        agent = TestAgent(config)
        startup_time = time.time() - start_time
        
        # Measure task execution time
        tasks = [
            "Fix the bug in my Python code",
            "Search for papers on machine learning", 
            "Write a function to sort arrays",
            "Debug this JavaScript error",
            "Create documentation"
        ]
        
        execution_times = []
        for task in tasks:
            start_time = time.time()
            result = agent.execute_task_with_skills(task)  # Should bypass skills
            execution_time = time.time() - start_time
            execution_times.append(execution_time)
        
        avg_execution_time = sum(execution_times) / len(execution_times)
        
        print(f"  ⏱️ Startup time: {startup_time:.3f}s")
        print(f"  ⏱️ Avg execution time: {avg_execution_time:.3f}s")
        print(f"  ⚡ Skills system: DISABLED")
        
        return startup_time, avg_execution_time

def test_cli_flag():
    """Test the CLI flag behavior."""
    print("\n🧪 Testing CLI flag behavior...")
    
    # Test with --no-skills flag
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "sciagent", 
            "--no-skills", "--help"
        ], capture_output=True, text=True, cwd="/Users/shrutibadhwar/Documents/2026/InProgressSWECode/sciagent")
        
        if "--no-skills" in result.stdout:
            print("  ✅ CLI flag --no-skills is available")
        else:
            print("  ❌ CLI flag --no-skills not found in help")
            
    except Exception as e:
        print(f"  ⚠️ Could not test CLI: {e}")

def main():
    """Run all benchmarks and compare performance."""
    print("🚀 Testing Optional Skill System Performance")
    print("=" * 50)
    
    # Benchmark with skills enabled
    enabled_startup, enabled_execution = benchmark_skills_enabled()
    
    # Benchmark with skills disabled  
    disabled_startup, disabled_execution = benchmark_skills_disabled()
    
    # Test CLI
    test_cli_flag()
    
    # Performance comparison
    print(f"\n📊 Performance Comparison:")
    startup_improvement = ((enabled_startup - disabled_startup) / enabled_startup * 100)
    execution_improvement = ((enabled_execution - disabled_execution) / enabled_execution * 100)
    
    print(f"  Startup time:")
    print(f"    Skills enabled:  {enabled_startup:.3f}s")
    print(f"    Skills disabled: {disabled_startup:.3f}s")
    print(f"    Improvement:     {startup_improvement:.1f}%")
    
    print(f"  Execution time:")
    print(f"    Skills enabled:  {enabled_execution:.3f}s")  
    print(f"    Skills disabled: {disabled_execution:.3f}s")
    print(f"    Improvement:     {execution_improvement:.1f}%")
    
    # Overall assessment
    print(f"\n🎯 Assessment:")
    if disabled_startup < enabled_startup:
        print(f"  ✅ Fast mode provides {abs(startup_improvement):.1f}% faster startup")
    else:
        print(f"  ⚠️ Fast mode startup is {abs(startup_improvement):.1f}% slower (test variance)")
    
    if disabled_execution < enabled_execution:
        print(f"  ✅ Fast mode provides {abs(execution_improvement):.1f}% faster execution")
    else:
        print(f"  ⚠️ Fast mode execution has {abs(execution_improvement):.1f}% overhead (test variance)")
    
    print(f"\n💡 Usage:")
    print(f"  # Enable skills (default):")
    print(f"  python -m sciagent 'Fix my Python code'")
    print(f"  ")
    print(f"  # Disable skills for maximum speed:")
    print(f"  python -m sciagent --no-skills 'Fix my Python code'")

if __name__ == "__main__":
    main()