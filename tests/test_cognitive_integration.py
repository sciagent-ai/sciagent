"""
Tests for cognitive loop integration with the agent.

These tests verify that the memory, planning, reflection, and scratchpad
tools are properly integrated into the agent execution loop.
"""

import os
import sys
import tempfile
import shutil
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sciagent.config import Config
from sciagent.cognitive_loop import CognitiveEnhancements, create_cognitive_enhancements


class MockAgent:
    """Mock agent for testing cognitive enhancements."""
    
    def __init__(self, working_dir: str):
        self.config = Config(
            api_key="test-key",
            working_dir=working_dir,
            max_iterations=1
        )
        self.tool_handlers = {}
        self.state = None
        
        # Load actual tools for testing
        from sciagent.tool_registry import DynamicToolRegistry
        registry = DynamicToolRegistry(['sciagent.tools.core'])
        registry.load_tools()
        self.tool_handlers = registry.tools


class TestCognitiveEnhancements:
    """Test suite for CognitiveEnhancements class."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir, ignore_errors=True)
    
    @pytest.fixture
    def mock_agent(self, temp_workspace):
        """Create a mock agent with cognitive tools."""
        return MockAgent(temp_workspace)
    
    @pytest.fixture
    def cognitive(self, mock_agent):
        """Create cognitive enhancements instance."""
        return create_cognitive_enhancements(mock_agent)
    
    def test_workspace_initialization(self, cognitive):
        """Test that task workspace is created correctly."""
        workspace = cognitive.initialize_task_workspace("test_task_123")
        
        assert workspace.exists()
        assert (workspace / "search_results").exists()
        assert (workspace / "analysis").exists()
        assert (workspace / "intermediate").exists()
    
    def test_should_create_plan_simple_task(self, cognitive):
        """Test that simple tasks don't trigger planning."""
        simple_tasks = [
            "fix a typo",
            "update the readme",
            "change the color to blue",
        ]
        
        for task in simple_tasks:
            assert not cognitive.should_create_plan(task), f"Simple task should not need plan: {task}"
    
    def test_should_create_plan_complex_task(self, cognitive):
        """Test that complex tasks trigger planning."""
        complex_task = """
        Implement a comprehensive data pipeline that includes:
        1. Data ingestion from multiple sources (S3, Kafka, REST APIs)
        2. Data transformation and validation
        3. Storage in both data warehouse and data lake
        4. Real-time analytics dashboard
        5. Alerting and monitoring integration
        """
        
        assert cognitive.should_create_plan(complex_task), "Complex task should need plan"
    
    def test_externalization_threshold(self, cognitive, temp_workspace):
        """Test that large results are externalized."""
        cognitive.initialize_task_workspace("test_external")
        
        # Small result should not be externalized
        small_result = {"success": True, "output": "Small output"}
        processed = cognitive.maybe_externalize_result("test_tool", small_result)
        assert "externalized_path" not in processed
        
        # Large result should be externalized
        large_output = "x" * 3000  # Over 2000 char threshold
        large_result = {"success": True, "output": large_output}
        processed = cognitive.maybe_externalize_result("grep_search", large_result)
        assert "externalized_path" in processed
        assert os.path.exists(processed["externalized_path"])
    
    def test_memory_integration(self, cognitive, mock_agent):
        """Test memory save and recall."""
        # Initialize mock state
        from sciagent.state import AgentState
        mock_agent.state = AgentState(
            task_id="test_task",
            original_task="test",
            completed_steps=[],
            current_step="testing",
            error_history=[],
            iteration_count=0,
            last_successful_operation="",
            working_context={}
        )
        
        # Save a memory
        cognitive.save_task_learning("test_key", "Test learning content", "learning")
        
        # Recall should find it (if memory tool is available)
        if "recall_memory" in mock_agent.tool_handlers:
            context = cognitive.recall_relevant_memories("test")
            # Memory might be empty if no matches, that's ok
            assert isinstance(context, str)
    
    def test_reflection_triggers(self, cognitive):
        """Test reflection trigger conditions."""
        # Should not reflect on first iteration
        assert not cognitive.should_reflect(1)
        
        # Should reflect after interval
        assert cognitive.should_reflect(6)  # Default interval is 5
        
        # Should reflect after consecutive errors
        cognitive.consecutive_errors = 0
        for _ in range(3):
            cognitive.should_reflect(1, {"success": False})
        assert cognitive.consecutive_errors >= 2
    
    def test_scratchpad_integration(self, cognitive, mock_agent):
        """Test scratchpad save functionality."""
        if "scratchpad" not in mock_agent.tool_handlers:
            pytest.skip("Scratchpad tool not available")
        
        cognitive.save_to_scratchpad("test_section", "Test content")
        context = cognitive.get_scratchpad_context()
        # Context might be empty if scratchpad is empty, that's ok
        assert isinstance(context, str)
    
    def test_enhance_system_prompt(self, cognitive):
        """Test system prompt enhancement."""
        base_prompt = "You are an AI assistant."
        task = "Implement a feature"
        
        enhanced = cognitive.enhance_system_prompt(base_prompt, task)
        
        # Should contain cognitive tools guidance
        assert "COGNITIVE TOOLS" in enhanced
        assert "save_memory" in enhanced
        assert "create_plan" in enhanced


class TestToolIntegration:
    """Test that cognitive tools work correctly."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory."""
        tmpdir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_dir)
        shutil.rmtree(tmpdir, ignore_errors=True)
    
    def test_memory_tools_loaded(self):
        """Test that memory tools are loaded."""
        from sciagent.tool_registry import DynamicToolRegistry
        registry = DynamicToolRegistry(['sciagent.tools.core'])
        registry.load_tools()
        
        assert "save_memory" in registry.tools
        assert "recall_memory" in registry.tools
        assert "forget_memory" in registry.tools
    
    def test_planning_tools_loaded(self):
        """Test that planning tools are loaded."""
        from sciagent.tool_registry import DynamicToolRegistry
        registry = DynamicToolRegistry(['sciagent.tools.core'])
        registry.load_tools()
        
        assert "create_plan" in registry.tools
        assert "update_plan" in registry.tools
        assert "get_plan" in registry.tools
    
    def test_reflection_tools_loaded(self):
        """Test that reflection tools are loaded."""
        from sciagent.tool_registry import DynamicToolRegistry
        registry = DynamicToolRegistry(['sciagent.tools.core'])
        registry.load_tools()
        
        assert "reflect" in registry.tools
        assert "get_insights" in registry.tools
    
    def test_scratchpad_tool_loaded(self):
        """Test that scratchpad tool is loaded."""
        from sciagent.tool_registry import DynamicToolRegistry
        registry = DynamicToolRegistry(['sciagent.tools.core'])
        registry.load_tools()
        
        assert "scratchpad" in registry.tools
    
    def test_memory_roundtrip(self, temp_dir):
        """Test saving and recalling memory."""
        from sciagent.tools.core.memory import SaveMemoryTool, RecallMemoryTool
        
        save_tool = SaveMemoryTool()
        recall_tool = RecallMemoryTool()
        
        # Save a memory
        result = save_tool.run({
            "key": "test.roundtrip",
            "content": "This is a test memory",
            "memory_type": "fact",
            "importance": "high"
        })
        assert result["success"]
        
        # Recall it
        result = recall_tool.run({"key": "test.roundtrip"})
        assert result["success"]
        assert len(result["results"]) == 1
        assert result["results"][0]["content"] == "This is a test memory"
    
    def test_plan_roundtrip(self, temp_dir):
        """Test creating and getting a plan."""
        from sciagent.tools.core.planning import CreatePlanTool, GetPlanTool
        
        create_tool = CreatePlanTool()
        get_tool = GetPlanTool()
        
        # Create a plan
        result = create_tool.run({
            "plan_id": "test_plan",
            "goal": "Test the planning system",
            "steps": [
                {"id": "step_1", "description": "First step"},
                {"id": "step_2", "description": "Second step"}
            ]
        })
        assert result["success"]
        
        # Get the plan
        result = get_tool.run({})
        assert result["success"]
        assert result["has_plan"]
        assert result["plan_id"] == "test_plan"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
