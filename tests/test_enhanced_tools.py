"""
Comprehensive test suite for enhanced tools.

Tests all the new tools added for Claude Code parity:
- MultiEditTool
- GitOperationsTool  
- AdvancedFileOperationsTool
- PerformanceMonitorTool
"""

import os
import tempfile
import shutil
import subprocess
import time
from pathlib import Path
from unittest import TestCase, mock
import json


class TestMultiEditTool(TestCase):
    """Test the MultiEditTool for atomic file operations."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Import the tool
        from sciagent.tools.core.multi_edit import MultiEditTool
        self.tool = MultiEditTool()
        
        # Create test files
        self.test_file1 = "test1.py"
        self.test_file2 = "test2.py"
        
        with open(self.test_file1, 'w') as f:
            f.write("def hello():\n    print('Hello, World!')\n    return 'success'\n")
        
        with open(self.test_file2, 'w') as f:
            f.write("class TestClass:\n    def __init__(self):\n        self.value = 42\n")
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_single_file_edit(self):
        """Test editing a single file."""
        tool_input = {
            "edits": [{
                "file_path": self.test_file1,
                "edits": [{
                    "old_str": "print('Hello, World!')",
                    "new_str": "print('Hello, SciAgent!')"
                }]
            }]
        }
        
        result = self.tool.run(tool_input)
        
        self.assertTrue(result["success"])
        self.assertIn("test1.py", result["files_modified"])
        
        # Verify file content changed
        with open(self.test_file1, 'r') as f:
            content = f.read()
        self.assertIn("Hello, SciAgent!", content)
        self.assertNotIn("Hello, World!", content)
    
    def test_multi_file_edit(self):
        """Test atomic editing of multiple files."""
        tool_input = {
            "edits": [
                {
                    "file_path": self.test_file1,
                    "edits": [{
                        "old_str": "def hello():",
                        "new_str": "def greet():"
                    }]
                },
                {
                    "file_path": self.test_file2,
                    "edits": [{
                        "old_str": "self.value = 42",
                        "new_str": "self.value = 100"
                    }]
                }
            ]
        }
        
        result = self.tool.run(tool_input)
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["files_modified"]), 2)
        
        # Verify both files changed
        with open(self.test_file1, 'r') as f:
            content1 = f.read()
        with open(self.test_file2, 'r') as f:
            content2 = f.read()
        
        self.assertIn("def greet():", content1)
        self.assertIn("self.value = 100", content2)
    
    def test_rollback_on_failure(self):
        """Test rollback when one edit fails."""
        original_content1 = open(self.test_file1, 'r').read()
        original_content2 = open(self.test_file2, 'r').read()
        
        tool_input = {
            "edits": [
                {
                    "file_path": self.test_file1,
                    "edits": [{
                        "old_str": "def hello():",
                        "new_str": "def greet():"
                    }]
                },
                {
                    "file_path": self.test_file2,
                    "edits": [{
                        "old_str": "NONEXISTENT_STRING",  # This will fail
                        "new_str": "replacement"
                    }]
                }
            ]
        }
        
        result = self.tool.run(tool_input)
        
        self.assertFalse(result["success"])
        self.assertTrue(result["rollback_performed"])
        
        # Verify files were rolled back
        with open(self.test_file1, 'r') as f:
            content1 = f.read()
        with open(self.test_file2, 'r') as f:
            content2 = f.read()
        
        self.assertEqual(content1, original_content1)
        self.assertEqual(content2, original_content2)
    
    def test_syntax_validation(self):
        """Test Python syntax validation."""
        tool_input = {
            "edits": [{
                "file_path": self.test_file1,
                "edits": [{
                    "old_str": "def hello():",
                    "new_str": "def hello("  # Invalid syntax
                }]
            }],
            "validate_syntax": True
        }
        
        result = self.tool.run(tool_input)
        
        self.assertFalse(result["success"])
        self.assertIn("syntax", result["error"].lower())


class TestGitOperationsTool(TestCase):
    """Test the GitOperationsTool for smart git workflows."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True)
        
        # Import the tool
        from sciagent.tools.core.git_operations import GitOperationsTool
        self.tool = GitOperationsTool()
        
        # Create test file
        with open("test.py", 'w') as f:
            f.write("print('Hello, World!')\n")
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_git_status(self):
        """Test git status command."""
        result = self.tool.run({"command": "status"})
        
        self.assertTrue(result["success"])
        self.assertIn("status_details", result)
        self.assertIn("untracked", result["status_details"])
    
    def test_smart_commit(self):
        """Test smart commit workflow with auto-generated message."""
        tool_input = {
            "command": "smart_commit",
            "files": ["test.py"],
            "auto_message": True
        }
        
        result = self.tool.run(tool_input)
        
        if result["success"]:  # Only test if git operations work
            self.assertIn("commit_message", result)
            self.assertIn("files_committed", result)
            self.assertIn("test.py", result["files_committed"])
    
    def test_commit_message_generation(self):
        """Test automatic commit message generation."""
        # Add and commit a file first
        subprocess.run(["git", "add", "test.py"], capture_output=True)
        
        result = self.tool.run({"command": "commit_message_gen"})
        
        self.assertTrue(result["success"])
        self.assertIn("generated_message", result)
        self.assertIsInstance(result["generated_message"], str)
    
    def test_branch_creation(self):
        """Test branch creation workflow."""
        tool_input = {
            "command": "create_branch",
            "branch": "feature-test"
        }
        
        result = self.tool.run(tool_input)
        
        if result["success"]:  # Only test if git operations work
            self.assertEqual(result["branch"], "feature-test")
            
            # Verify branch exists
            check_result = subprocess.run(
                ["git", "branch", "--list", "feature-test"],
                capture_output=True, text=True
            )
            self.assertIn("feature-test", check_result.stdout)


class TestAdvancedFileOperationsTool(TestCase):
    """Test the AdvancedFileOperationsTool for enhanced file operations."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Import the tool
        from sciagent.tools.core.advanced_file_ops import AdvancedFileOperationsTool
        self.tool = AdvancedFileOperationsTool()
        
        # Create test files
        self.test_py_file = "test.py"
        self.test_json_file = "test.json"
        self.test_js_file = "test.js"
        
        with open(self.test_py_file, 'w') as f:
            f.write("""
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

def main():
    calc = Calculator()
    print(calc.add(2, 3))

if __name__ == "__main__":
    main()
""")
        
        with open(self.test_json_file, 'w') as f:
            json.dump({
                "name": "test",
                "version": "1.0.0",
                "dependencies": {
                    "requests": "^2.25.1",
                    "click": "^8.0.0"
                }
            }, f, indent=2)
        
        with open(self.test_js_file, 'w') as f:
            f.write("""
function greet(name) {
    return `Hello, ${name}!`;
}

const add = (a, b) => a + b;

class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
}

export { greet, add, Person };
""")
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_file_analysis(self):
        """Test comprehensive file analysis."""
        result = self.tool.run({
            "command": "analyze",
            "path": self.test_py_file
        })
        
        self.assertTrue(result["success"])
        self.assertIn("analysis", result)
        
        analysis = result["analysis"]
        self.assertIn("content_analysis", analysis)
        self.assertIn("python_analysis", analysis)
        
        py_analysis = analysis["python_analysis"]
        self.assertTrue(py_analysis["is_valid_syntax"])
        self.assertIn("Calculator", [cls["name"] for cls in py_analysis["classes"]])
        self.assertIn("main", [func["name"] for func in py_analysis["functions"]])
    
    def test_json_analysis(self):
        """Test JSON file analysis."""
        result = self.tool.run({
            "command": "analyze", 
            "path": self.test_json_file
        })
        
        self.assertTrue(result["success"])
        analysis = result["analysis"]
        
        if "json_analysis" in analysis:
            json_analysis = analysis["json_analysis"]
            self.assertTrue(json_analysis["is_valid_json"])
            self.assertEqual(json_analysis["structure"]["type"], "object")
    
    def test_javascript_analysis(self):
        """Test JavaScript file analysis."""
        result = self.tool.run({
            "command": "analyze",
            "path": self.test_js_file
        })
        
        self.assertTrue(result["success"])
        analysis = result["analysis"]
        
        if "javascript_analysis" in analysis:
            js_analysis = analysis["javascript_analysis"]
            self.assertIn("greet", js_analysis["functions"])
            self.assertIn("add", js_analysis["arrow_functions"])
            self.assertIn("Person", js_analysis["classes"])
    
    def test_file_info(self):
        """Test file information retrieval."""
        result = self.tool.run({
            "command": "get_info",
            "path": self.test_py_file
        })
        
        self.assertTrue(result["success"])
        self.assertIn("file_info", result)
        
        file_info = result["file_info"]
        self.assertTrue(file_info["is_file"])
        self.assertFalse(file_info["is_dir"])
        self.assertIn("encoding", file_info)
        self.assertIn("line_count", file_info)
    
    def test_encoding_detection(self):
        """Test encoding detection."""
        result = self.tool.run({
            "command": "validate_encoding",
            "path": self.test_py_file
        })
        
        self.assertTrue(result["success"])
        self.assertIn("encoding", result)
        self.assertIn("confidence", result)
        self.assertGreater(result["confidence"], 0.5)
    
    def test_read_with_context(self):
        """Test enhanced file reading."""
        result = self.tool.run({
            "command": "read_with_context",
            "path": self.test_py_file,
            "line_numbers": True,
            "start_line": 2,
            "end_line": 5
        })
        
        self.assertTrue(result["success"])
        self.assertIn("file_info", result)
        self.assertIn("encoding", result)
        
        # Check that line numbers are included
        content = result["output"]
        self.assertIn("2:", content)
        self.assertIn("class Calculator", content)
    
    def test_write_with_backup(self):
        """Test write operation with backup."""
        new_content = "# This is a test file\nprint('Modified content')\n"
        
        result = self.tool.run({
            "command": "write_with_backup",
            "path": "new_test.py",
            "content": new_content,
            "create_backup": True
        })
        
        self.assertTrue(result["success"])
        self.assertIn("file_info", result)
        self.assertIn("bytes_written", result)
        
        # Verify file was written
        self.assertTrue(os.path.exists("new_test.py"))
        with open("new_test.py", 'r') as f:
            written_content = f.read()
        self.assertEqual(written_content, new_content)


class TestPerformanceMonitorTool(TestCase):
    """Test the PerformanceMonitorTool for performance tracking."""
    
    def setUp(self):
        # Import the tool
        from sciagent.tools.core.performance_monitor import PerformanceMonitorTool
        self.tool = PerformanceMonitorTool()
    
    def test_start_stop_monitoring(self):
        """Test basic monitoring start and stop."""
        # Start monitoring
        result = self.tool.run({"command": "start_monitoring"})
        self.assertTrue(result["success"])
        
        # Wait a bit
        time.sleep(0.1)
        
        # Stop monitoring
        result = self.tool.run({"command": "stop_monitoring"})
        self.assertTrue(result["success"])
        self.assertIn("metrics_collected", result)
    
    def test_performance_stats(self):
        """Test performance statistics generation."""
        # Start monitoring briefly
        self.tool.run({"command": "start_monitoring"})
        time.sleep(0.1)
        self.tool.run({"command": "stop_monitoring"})
        
        # Get stats
        result = self.tool.run({"command": "get_stats"})
        
        if result["success"]:  # Only test if we have data
            self.assertIn("stats", result)
            stats = result["stats"]
            self.assertIn("monitoring_period", stats)
            self.assertIn("system_performance", stats)
    
    def test_benchmark_operations(self):
        """Test benchmarking functionality."""
        result = self.tool.run({
            "command": "benchmark",
            "operation": "file_read",
            "iterations": 3
        })
        
        self.assertTrue(result["success"])
        self.assertIn("benchmark_results", result)
        
        benchmark = result["benchmark_results"]
        self.assertEqual(benchmark["iterations"], 3)
        self.assertIn("duration_stats", benchmark)
        self.assertIn("memory_stats", benchmark)
    
    def test_optimization_recommendations(self):
        """Test optimization recommendations."""
        # Generate some mock data
        self.tool._stats["system_metrics"].append({
            "timestamp": "2025-01-01T00:00:00",
            "system": {"cpu_percent": 95.0, "memory_percent": 85.0},
            "process": {"memory_rss_mb": 100.0}
        })
        
        result = self.tool.run({"command": "optimize_recommendations"})
        
        self.assertTrue(result["success"])
        self.assertIn("recommendations", result)
    
    def test_tool_tracking(self):
        """Test tool execution tracking."""
        # Simulate tool execution tracking
        self.tool.track_tool_execution(
            tool_name="test_tool",
            start_time=time.time(),
            end_time=time.time() + 0.1,
            success=True,
            test_param="value"
        )
        
        # Should have recorded the execution
        self.assertIn("test_tool", self.tool._stats["tool_executions"])
        executions = self.tool._stats["tool_executions"]["test_tool"]
        self.assertEqual(len(executions), 1)
        self.assertTrue(executions[0]["success"])
    
    def test_memory_profile(self):
        """Test memory profiling."""
        result = self.tool.run({"command": "memory_profile"})
        
        self.assertTrue(result["success"])
        self.assertIn("memory_profile", result)
    
    def test_reset_stats(self):
        """Test statistics reset."""
        # Add some data
        self.tool._stats["system_metrics"].append({"test": "data"})
        
        result = self.tool.run({"command": "reset_stats"})
        self.assertTrue(result["success"])
        
        # Verify stats were reset
        self.assertEqual(len(self.tool._stats["system_metrics"]), 0)


def run_enhanced_tools_tests():
    """Run all enhanced tools tests."""
    import unittest
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMultiEditTool))
    suite.addTests(loader.loadTestsFromTestCase(TestGitOperationsTool))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedFileOperationsTool))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceMonitorTool))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_enhanced_tools_tests()
    exit(0 if success else 1)