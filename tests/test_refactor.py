#!/usr/bin/env python3
"""Quick test to verify the refactored SCIAgent works correctly."""

from sciagent.config import Config
from sciagent.agent import SCIAgent

def test_agent_creation():
    """Test that we can create an agent and check basic functionality."""
    # Create a minimal config
    config = Config(
        model="claude-3-haiku-20240307",
        api_key="test-key",  # Won't be used in this test
        max_iterations=1,
        enable_web=False,
        enable_notebooks=False,
        verbosity="minimal"
    )
    
    try:
        # Create the agent
        agent = SCIAgent(config)
        
        # Verify it inherits from CoreAgent
        from sciagent.core_agent import CoreAgent
        assert isinstance(agent, CoreAgent), "Agent should inherit from CoreAgent"
        
        # Verify it has the required abstract methods implemented
        assert hasattr(agent, 'build_system_prompt'), "Should have build_system_prompt method"
        assert hasattr(agent, 'execute_task'), "Should have execute_task method"
        
        # Test system prompt generation
        system_prompt = agent.build_system_prompt()
        assert isinstance(system_prompt, str), "System prompt should be a string"
        assert len(system_prompt) > 100, "System prompt should be substantial"
        
        # Verify tools are loaded
        assert len(agent.tools) > 0, "Should have tools loaded"
        assert len(agent.tool_handlers) > 0, "Should have tool handlers"
        
        # Verify core methods exist (inherited from CoreAgent)
        assert hasattr(agent, '_call_llm'), "Should have _call_llm from CoreAgent"
        assert hasattr(agent, '_save_state'), "Should have _save_state from CoreAgent" 
        assert hasattr(agent, '_load_state'), "Should have _load_state from CoreAgent"
        
        print("✅ All tests passed!")
        print(f"✅ Agent created with {len(agent.tools)} tools")
        print(f"✅ System prompt length: {len(system_prompt)} characters")
        print("✅ Refactor successful - SCIAgent now inherits from CoreAgent")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent_creation()
    exit(0 if success else 1)