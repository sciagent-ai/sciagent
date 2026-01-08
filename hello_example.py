#!/usr/bin/env python3
"""Simple example showing how to run SciAgent with a basic task."""

from sciagent.agent import SCIAgent
from sciagent.config import Config

def main():
    # Create simple config
    config = Config(
        working_dir=".",
        max_iterations=5,
        debug_mode=True,
        progress_tracking=True
    )
    
    # Create agent
    agent = SCIAgent(config)
    
    # Run simple task
    task = "Create a simple hello.txt file that says 'Hello there from SciAgent!'"
    
    print("🤖 Running SciAgent with task:", task)
    print("📁 Progress and trajectories will be stored in:")
    print("   - Session data: .sciagent_sessions/")
    print("   - Workspace: .sciagent_workspace/")
    print("   - Progress file: progress.md")
    
    result = agent.execute_task(task)
    
    print("\n📊 Results:")
    print(f"✅ Success: {result['success']}")
    print(f"🔄 Iterations: {result['iterations']}")
    print(f"🆔 Task ID: {result['task_id']}")
    
    return result

if __name__ == "__main__":
    main()