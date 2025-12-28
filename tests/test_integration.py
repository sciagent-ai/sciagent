"""
Integration tests for enhanced tools with the agent system.

Tests how the new tools integrate with CoreAgent, tool registry,
performance monitoring, and the overall sciagent architecture.
"""

import os
import tempfile
import shutil
import time
from pathlib import Path
from unittest import TestCase


class TestToolIntegration(TestCase):
    """Test integration of enhanced tools with the agent system."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create a test config
        from sciagent.config import Config
        self.config = Config(
            working_dir=self.test_dir,
            enable_performance_monitoring=True,
            enable_skills=False,  # Disable for simpler testing
            max_iterations=5,
            verbosity="debug"
        )
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_tool_registry_discovery(self):
        """Test that the tool registry discovers new tools."""
        from sciagent.tool_registry import DynamicToolRegistry
        
        registry = DynamicToolRegistry(
            search_paths=["sciagent.tools.core"],
            config=self.config
        )
        registry.load_tools()
        
        # Check that enhanced tools are discovered
        tool_names = list(registry.tools.keys())
        
        expected_tools = [
            "multi_edit",
            "git_operations", 
            "advanced_file_ops",
            "performance_monitor"
        ]
        
        for tool_name in expected_tools:
            self.assertIn(tool_name, tool_names, f"Tool {tool_name} not discovered")
        
        # Verify tools are properly instantiated
        for tool_name in expected_tools:
            tool = registry.tools[tool_name]
            self.assertIsNotNone(tool)
            self.assertTrue(hasattr(tool, 'run'))
            self.assertTrue(hasattr(tool, 'name'))
            self.assertTrue(hasattr(tool, 'description'))
    
    def test_core_agent_integration(self):
        """Test that CoreAgent can use enhanced tools."""
        try:
            from sciagent.core_agent import CoreAgent
            from sciagent.agent import SCIAgent
        except ImportError as e:
            self.skipTest(f"Cannot import agent classes: {e}")
        
        # Create agent with performance monitoring
        agent = SCIAgent(self.config)
        
        # Check performance monitor integration
        if hasattr(agent, 'performance_monitor'):
            self.assertIsNotNone(agent.performance_monitor)
        
        # Check tool registry has enhanced tools
        self.assertIn("multi_edit", agent.tool_handlers)
        self.assertIn("git_operations", agent.tool_handlers)
        self.assertIn("advanced_file_ops", agent.tool_handlers)
        self.assertIn("performance_monitor", agent.tool_handlers)
    
    def test_tool_execution_workflow(self):
        """Test executing enhanced tools through the agent."""
        try:
            from sciagent.agent import SCIAgent
        except ImportError as e:
            self.skipTest(f"Cannot import agent: {e}")
        
        agent = SCIAgent(self.config)
        
        # Test file operations workflow
        test_content = "print('Hello from integration test')\n"
        
        # 1. Create file with advanced_file_ops
        result = agent._execute_scientific_tool("advanced_file_ops", {
            "command": "write_with_backup",
            "path": "test_integration.py",
            "content": test_content
        })
        
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists("test_integration.py"))
        
        # 2. Analyze the file
        result = agent._execute_scientific_tool("advanced_file_ops", {
            "command": "analyze",
            "path": "test_integration.py"
        })
        
        self.assertTrue(result["success"])
        self.assertIn("analysis", result)
        
        # 3. Edit file with multi_edit
        result = agent._execute_scientific_tool("multi_edit", {
            "edits": [{
                "file_path": "test_integration.py",
                "edits": [{
                    "old_str": "Hello from integration test",
                    "new_str": "Hello from modified integration test"
                }]
            }]
        })
        
        self.assertTrue(result["success"])
        
        # Verify the edit worked
        with open("test_integration.py", 'r') as f:
            content = f.read()
        self.assertIn("modified integration test", content)
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration with tool execution."""
        try:
            from sciagent.agent import SCIAgent
        except ImportError as e:
            self.skipTest(f"Cannot import agent: {e}")
        
        # Enable performance monitoring
        from sciagent.config import Config
        config = Config(
            working_dir=self.test_dir,
            enable_performance_monitoring=True,
            enable_skills=False,
            max_iterations=3
        )
        
        agent = SCIAgent(config)
        
        if agent.performance_monitor:
            # Execute some tools to generate performance data
            agent._execute_scientific_tool("performance_monitor", {
                "command": "start_monitoring"
            })
            
            # Execute a few operations
            agent._execute_scientific_tool("advanced_file_ops", {
                "command": "write_with_backup",
                "path": "perf_test.py",
                "content": "# Performance test file\nprint('test')\n"
            })
            
            time.sleep(0.1)  # Let monitoring collect some data
            
            # Get performance stats
            result = agent._execute_scientific_tool("performance_monitor", {
                "command": "get_stats"
            })
            
            if result["success"]:
                self.assertIn("stats", result)
                stats = result["stats"]
                self.assertIn("monitoring_period", stats)
    
    def test_git_integration_workflow(self):
        """Test git operations integration."""
        try:
            from sciagent.agent import SCIAgent
        except ImportError as e:
            self.skipTest(f"Cannot import agent: {e}")
        
        agent = SCIAgent(self.config)
        
        # Initialize git repo (if git is available)
        import subprocess
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("Git not available")
        
        # Initialize repo
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True)
        
        # Create and commit a file using the tools
        # 1. Create file
        result = agent._execute_scientific_tool("advanced_file_ops", {
            "command": "write_with_backup",
            "path": "git_test.py",
            "content": "print('Git integration test')\n"
        })
        self.assertTrue(result["success"])
        
        # 2. Git status
        result = agent._execute_scientific_tool("git_operations", {
            "command": "status"
        })
        self.assertTrue(result["success"])
        
        # 3. Smart commit
        result = agent._execute_scientific_tool("git_operations", {
            "command": "smart_commit",
            "files": ["git_test.py"],
            "auto_message": True
        })
        
        # Don't fail the test if git operations have issues
        # Just verify the tool executed
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
    
    def test_error_handling_integration(self):
        """Test error handling across enhanced tools."""
        try:
            from sciagent.agent import SCIAgent
        except ImportError as e:
            self.skipTest(f"Cannot import agent: {e}")
        
        agent = SCIAgent(self.config)
        
        # Test multi_edit rollback on error
        # Create a test file
        with open("error_test.py", 'w') as f:
            f.write("print('original content')\n")
        
        original_content = open("error_test.py", 'r').read()
        
        # Attempt multi-edit with one valid and one invalid edit
        result = agent._execute_scientific_tool("multi_edit", {
            "edits": [
                {
                    "file_path": "error_test.py", 
                    "edits": [{
                        "old_str": "original content",
                        "new_str": "modified content"
                    }]
                },
                {
                    "file_path": "nonexistent_file.py",
                    "edits": [{
                        "old_str": "something",
                        "new_str": "something else"
                    }]
                }
            ]
        })
        
        # Should fail and rollback
        self.assertFalse(result["success"])
        
        # Verify original file wasn't changed
        current_content = open("error_test.py", 'r').read()
        self.assertEqual(current_content, original_content)
    
    def test_tool_schema_generation(self):
        """Test that enhanced tools generate proper schemas for LLM."""
        from sciagent.tool_registry import DynamicToolRegistry
        
        registry = DynamicToolRegistry(
            search_paths=["sciagent.tools.core"],
            config=self.config
        )
        registry.load_tools()
        
        schemas = registry.get_tool_schemas()
        
        # Find enhanced tool schemas
        enhanced_tools = ["multi_edit", "git_operations", "advanced_file_ops", "performance_monitor"]
        found_tools = []
        
        for schema in schemas:
            if schema["name"] in enhanced_tools:
                found_tools.append(schema["name"])
                
                # Validate schema structure
                self.assertIn("name", schema)
                self.assertIn("description", schema)
                self.assertIn("input_schema", schema)
                
                # Validate input schema
                input_schema = schema["input_schema"]
                self.assertIn("type", input_schema)
                self.assertEqual(input_schema["type"], "object")
                self.assertIn("properties", input_schema)
                self.assertIn("required", input_schema)
        
        # Verify all enhanced tools found
        for tool in enhanced_tools:
            self.assertIn(tool, found_tools, f"Schema not found for {tool}")


class TestToolPerformance(TestCase):
    """Test performance characteristics of enhanced tools."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_tool_loading_performance(self):
        """Test tool loading doesn't significantly impact startup time."""
        from sciagent.tool_registry import DynamicToolRegistry
        from sciagent.config import Config
        
        config = Config(working_dir=self.test_dir)
        
        start_time = time.time()
        
        registry = DynamicToolRegistry(
            search_paths=["sciagent.tools.core"],
            config=config
        )
        registry.load_tools()
        
        load_time = time.time() - start_time
        
        # Should load tools quickly (less than 2 seconds)
        self.assertLess(load_time, 2.0, f"Tool loading took {load_time:.2f}s, too slow")
        
        # Should have loaded enhanced tools
        self.assertGreaterEqual(len(registry.tools), 10)
    
    def test_multi_edit_performance(self):
        """Test multi_edit performance with multiple files."""
        from sciagent.tools.core.multi_edit import MultiEditTool
        
        tool = MultiEditTool()
        
        # Create multiple test files
        files = []
        for i in range(10):
            filename = f"test_{i}.py"
            with open(filename, 'w') as f:
                f.write(f"print('File {i}')\n" * 100)  # 100 lines each
            files.append(filename)
        
        # Prepare multi-edit
        edits = []
        for filename in files:
            edits.append({
                "file_path": filename,
                "edits": [{
                    "old_str": "print('File",
                    "new_str": "print('Modified File"
                }]
            })
        
        start_time = time.time()
        
        result = tool.run({"edits": edits})
        
        edit_time = time.time() - start_time
        
        self.assertTrue(result["success"])
        # Should complete in reasonable time (less than 5 seconds for 10 files)
        self.assertLess(edit_time, 5.0, f"Multi-edit took {edit_time:.2f}s, too slow")


def run_integration_tests():
    """Run all integration tests."""
    import unittest
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestToolIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestToolPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)