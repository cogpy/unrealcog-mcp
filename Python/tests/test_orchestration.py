"""
Unit tests for OpenCog Multi-Agent Orchestration Tools

Tests the core orchestration functionality including:
- Agent session management
- Knowledge atomspace operations
- Workflow task coordination
- Thread safety and state management
"""

import unittest
import json
import sys
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.orchestration_tools import (
    AgentSession, KnowledgeAtom, WorkflowTask,
    _orchestration_state
)


class TestAgentSession(unittest.TestCase):
    """Test AgentSession class."""
    
    def test_agent_creation(self):
        """Test creating an agent session."""
        agent = AgentSession("test-agent", "cursor", ["capability1", "capability2"])
        
        self.assertEqual(agent.agent_id, "test-agent")
        self.assertEqual(agent.agent_type, "cursor")
        self.assertEqual(agent.capabilities, ["capability1", "capability2"])
        self.assertEqual(agent.status, "active")
        self.assertEqual(agent.task_count, 0)
        self.assertIsNotNone(agent.created_at)
        self.assertIsNotNone(agent.last_active)
    
    def test_agent_default_capabilities(self):
        """Test agent with no capabilities."""
        agent = AgentSession("test-agent", "windsurf")
        
        self.assertEqual(agent.capabilities, [])
    
    def test_agent_metadata(self):
        """Test agent metadata storage."""
        agent = AgentSession("test-agent", "claude_desktop", ["ui_design"])
        agent.metadata["custom_key"] = "custom_value"
        
        self.assertEqual(agent.metadata["custom_key"], "custom_value")


class TestKnowledgeAtom(unittest.TestCase):
    """Test KnowledgeAtom class."""
    
    def test_atom_creation(self):
        """Test creating a knowledge atom."""
        content = {"name": "TestBlueprint", "status": "completed"}
        atom = KnowledgeAtom("blueprint", content, "test-agent")
        
        self.assertEqual(atom.atom_type, "blueprint")
        self.assertEqual(atom.content, content)
        self.assertEqual(atom.source_agent, "test-agent")
        self.assertEqual(atom.access_count, 0)
        self.assertIsNone(atom.last_accessed)
        self.assertIsNotNone(atom.created_at)
    
    def test_atom_without_source(self):
        """Test atom creation without source agent."""
        atom = KnowledgeAtom("scene_state", {"aspect": "lighting"})
        
        self.assertIsNone(atom.source_agent)


class TestWorkflowTask(unittest.TestCase):
    """Test WorkflowTask class."""
    
    def test_task_creation(self):
        """Test creating a workflow task."""
        params = {"blueprint": "BP_Player", "location": [0, 0, 100]}
        task = WorkflowTask("task-1", "create_actor", params, "test-agent", 5)
        
        self.assertEqual(task.task_id, "task-1")
        self.assertEqual(task.task_type, "create_actor")
        self.assertEqual(task.params, params)
        self.assertEqual(task.assigned_agent, "test-agent")
        self.assertEqual(task.priority, 5)
        self.assertEqual(task.status, "pending")
        self.assertIsNone(task.started_at)
        self.assertIsNone(task.completed_at)
        self.assertIsNone(task.result)
    
    def test_task_default_values(self):
        """Test task with default values."""
        task = WorkflowTask("task-2", "test_task", {})
        
        self.assertIsNone(task.assigned_agent)
        self.assertEqual(task.priority, 0)
    
    def test_task_status_updates(self):
        """Test task status lifecycle."""
        task = WorkflowTask("task-3", "test_task", {})
        
        # Initial state
        self.assertEqual(task.status, "pending")
        
        # Claim task
        task.status = "claimed"
        task.started_at = datetime.now().isoformat()
        self.assertEqual(task.status, "claimed")
        self.assertIsNotNone(task.started_at)
        
        # Complete task
        task.status = "completed"
        task.completed_at = datetime.now().isoformat()
        task.result = {"success": True}
        self.assertEqual(task.status, "completed")
        self.assertIsNotNone(task.completed_at)
        self.assertEqual(task.result["success"], True)


class TestOrchestrationIntegration(unittest.TestCase):
    """Integration tests for orchestration system."""
    
    def setUp(self):
        """Clear orchestration state before each test."""
        with _orchestration_state["lock"]:
            _orchestration_state["agents"].clear()
            _orchestration_state["knowledge_base"].clear()
            _orchestration_state["task_queue"].clear()
            _orchestration_state["workflow_history"].clear()
    
    def test_multiple_agents(self):
        """Test managing multiple agents."""
        with _orchestration_state["lock"]:
            agent1 = AgentSession("agent-1", "cursor", ["blueprint"])
            agent2 = AgentSession("agent-2", "windsurf", ["level_design"])
            
            _orchestration_state["agents"]["agent-1"] = agent1
            _orchestration_state["agents"]["agent-2"] = agent2
            
            self.assertEqual(len(_orchestration_state["agents"]), 2)
            self.assertIn("agent-1", _orchestration_state["agents"])
            self.assertIn("agent-2", _orchestration_state["agents"])
    
    def test_knowledge_storage(self):
        """Test storing and retrieving knowledge."""
        with _orchestration_state["lock"]:
            atom1 = KnowledgeAtom("blueprint", {"name": "BP_Player"}, "agent-1")
            atom2 = KnowledgeAtom("actor", {"name": "MainLight"}, "agent-2")
            
            _orchestration_state["knowledge_base"]["atom-1"] = atom1
            _orchestration_state["knowledge_base"]["atom-2"] = atom2
            
            self.assertEqual(len(_orchestration_state["knowledge_base"]), 2)
            self.assertEqual(_orchestration_state["knowledge_base"]["atom-1"].atom_type, "blueprint")
            self.assertEqual(_orchestration_state["knowledge_base"]["atom-2"].source_agent, "agent-2")
    
    def test_task_queue_ordering(self):
        """Test task queue priority ordering."""
        with _orchestration_state["lock"]:
            task1 = WorkflowTask("task-1", "low_priority", {}, None, 1)
            task2 = WorkflowTask("task-2", "high_priority", {}, None, 10)
            task3 = WorkflowTask("task-3", "medium_priority", {}, None, 5)
            
            _orchestration_state["task_queue"].extend([task1, task2, task3])
            _orchestration_state["task_queue"].sort(key=lambda t: t.priority, reverse=True)
            
            # Should be ordered by priority (highest first)
            self.assertEqual(_orchestration_state["task_queue"][0].task_id, "task-2")
            self.assertEqual(_orchestration_state["task_queue"][1].task_id, "task-3")
            self.assertEqual(_orchestration_state["task_queue"][2].task_id, "task-1")
    
    def test_workflow_history(self):
        """Test workflow history tracking."""
        with _orchestration_state["lock"]:
            history_entry = {
                "task_id": "task-1",
                "task_type": "test_task",
                "agent": "agent-1",
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result": {"success": True}
            }
            
            _orchestration_state["workflow_history"].append(history_entry)
            
            self.assertEqual(len(_orchestration_state["workflow_history"]), 1)
            self.assertEqual(_orchestration_state["workflow_history"][0]["task_id"], "task-1")


class TestThreadSafety(unittest.TestCase):
    """Test thread safety of orchestration state."""
    
    def test_lock_exists(self):
        """Test that orchestration state has a lock."""
        self.assertIn("lock", _orchestration_state)
        self.assertIsNotNone(_orchestration_state["lock"])
    
    def test_lock_is_reentrant(self):
        """Test that the lock is reentrant (RLock)."""
        import threading
        
        # Should be able to acquire lock multiple times in same thread
        with _orchestration_state["lock"]:
            with _orchestration_state["lock"]:
                # Nested lock acquisition should work
                self.assertTrue(True)


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAgentSession))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeAtom))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowTask))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestrationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestThreadSafety))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    result = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
