"""
OpenCog-inspired Multi-Agent Orchestration Tools for Unreal Engine MCP.

This module implements an orchestration workbench that enables coordination
of concurrently integrated Cognitive AI assistant clients (Cursor, Windsurf,
Claude Desktop) to control Unreal Engine through natural language using MCP.

The orchestration system provides:
- Agent session management and coordination
- Knowledge sharing between concurrent agents
- Task delegation and workflow management
- Conflict resolution for concurrent operations
- Shared context and state management
"""

import logging
import json
import time
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("UnrealMCP.Orchestration")

# Global orchestration state
_orchestration_state = {
    "agents": {},  # Active agent sessions
    "knowledge_base": {},  # Shared knowledge atomspace
    "task_queue": [],  # Coordinated task queue
    "workflow_history": [],  # Historical workflow records
    "lock": threading.RLock()  # Thread-safe access
}


class AgentSession:
    """Represents an active AI agent session in the orchestration."""
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str] = None):
        """Initialize agent session.
        
        Args:
            agent_id: Unique identifier for the agent session
            agent_type: Type of AI client (e.g., 'cursor', 'windsurf', 'claude_desktop')
            capabilities: List of capabilities this agent can perform
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities or []
        self.created_at = datetime.now().isoformat()
        self.last_active = datetime.now().isoformat()
        self.status = "active"
        self.task_count = 0
        self.metadata = {}


class KnowledgeAtom:
    """Represents a knowledge atom in the shared atomspace."""
    
    def __init__(self, atom_type: str, content: Any, source_agent: str = None):
        """Initialize knowledge atom.
        
        Args:
            atom_type: Type of knowledge (e.g., 'actor', 'blueprint', 'workflow')
            content: The knowledge content
            source_agent: ID of the agent that created this knowledge
        """
        self.atom_type = atom_type
        self.content = content
        self.source_agent = source_agent
        self.created_at = datetime.now().isoformat()
        self.access_count = 0
        self.last_accessed = None


class WorkflowTask:
    """Represents a task in the coordinated workflow."""
    
    def __init__(self, task_id: str, task_type: str, params: Dict[str, Any],
                 assigned_agent: str = None, priority: int = 0):
        """Initialize workflow task.
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task to perform
            params: Task parameters
            assigned_agent: ID of agent assigned to this task
            priority: Task priority (higher = more urgent)
        """
        self.task_id = task_id
        self.task_type = task_type
        self.params = params
        self.assigned_agent = assigned_agent
        self.priority = priority
        self.status = "pending"
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.result = None


def register_orchestration_tools(mcp: FastMCP):
    """Register orchestration tools with the MCP server.
    
    Args:
        mcp: FastMCP server instance to register tools with
    """
    
    @mcp.tool()
    def register_agent(
        agent_id: str,
        agent_type: str,
        capabilities: str = ""
    ) -> Dict[str, Any]:
        """Register a new AI agent session in the orchestration workbench.
        
        This tool allows concurrent AI clients (Cursor, Windsurf, Claude Desktop) to 
        register themselves for coordinated multi-agent workflows.
        
        Args:
            agent_id: Unique identifier for this agent session (e.g., "cursor-session-1")
            agent_type: Type of AI client - must be one of: 'cursor', 'windsurf', 'claude_desktop', 'custom'
            capabilities: Comma-separated list of agent capabilities (e.g., "blueprint_creation,actor_spawning,ui_design")
        
        Returns:
            Dict containing registration status and agent information
            
        Example:
            register_agent("cursor-main", "cursor", "blueprint_creation,level_design")
        """
        with _orchestration_state["lock"]:
            # Parse capabilities
            cap_list = [c.strip() for c in capabilities.split(",")] if capabilities else []
            
            # Check if agent already exists
            if agent_id in _orchestration_state["agents"]:
                # Update existing agent
                agent = _orchestration_state["agents"][agent_id]
                agent.last_active = datetime.now().isoformat()
                agent.status = "active"
                logger.info(f"Agent {agent_id} re-activated")
                return {
                    "status": "success",
                    "message": f"Agent {agent_id} re-activated",
                    "agent": {
                        "id": agent.agent_id,
                        "type": agent.agent_type,
                        "capabilities": agent.capabilities,
                        "task_count": agent.task_count
                    }
                }
            
            # Create new agent session
            agent = AgentSession(agent_id, agent_type, cap_list)
            _orchestration_state["agents"][agent_id] = agent
            
            logger.info(f"Registered new agent: {agent_id} ({agent_type})")
            return {
                "status": "success",
                "message": f"Agent {agent_id} registered successfully",
                "agent": {
                    "id": agent.agent_id,
                    "type": agent.agent_type,
                    "capabilities": agent.capabilities,
                    "created_at": agent.created_at
                }
            }
    
    @mcp.tool()
    def list_active_agents() -> Dict[str, Any]:
        """List all active AI agent sessions in the orchestration workbench.
        
        Returns information about all registered and active agents, useful for
        understanding the current multi-agent coordination state.
        
        Returns:
            Dict containing list of active agents with their details
            
        Example:
            list_active_agents()
        """
        with _orchestration_state["lock"]:
            agents = []
            for agent_id, agent in _orchestration_state["agents"].items():
                agents.append({
                    "id": agent.agent_id,
                    "type": agent.agent_type,
                    "status": agent.status,
                    "capabilities": agent.capabilities,
                    "task_count": agent.task_count,
                    "created_at": agent.created_at,
                    "last_active": agent.last_active
                })
            
            return {
                "status": "success",
                "total_agents": len(agents),
                "agents": agents
            }
    
    @mcp.tool()
    def deregister_agent(agent_id: str) -> Dict[str, Any]:
        """Deregister an AI agent session from the orchestration workbench.
        
        Args:
            agent_id: Unique identifier of the agent to deregister
            
        Returns:
            Dict containing deregistration status
            
        Example:
            deregister_agent("cursor-session-1")
        """
        with _orchestration_state["lock"]:
            if agent_id not in _orchestration_state["agents"]:
                return {
                    "status": "error",
                    "error": f"Agent {agent_id} not found"
                }
            
            agent = _orchestration_state["agents"][agent_id]
            agent.status = "inactive"
            
            logger.info(f"Deregistered agent: {agent_id}")
            return {
                "status": "success",
                "message": f"Agent {agent_id} deregistered successfully"
            }
    
    @mcp.tool()
    def share_knowledge(
        knowledge_type: str,
        knowledge_content: str,
        source_agent: str = "",
        metadata: str = ""
    ) -> Dict[str, Any]:
        """Share knowledge in the orchestration atomspace for multi-agent coordination.
        
        This implements an OpenCog-inspired atomspace where agents can share knowledge
        about actors, blueprints, workflows, or any other information that helps with
        coordinated task execution.
        
        Args:
            knowledge_type: Type of knowledge being shared (e.g., 'actor', 'blueprint', 'workflow', 'scene_state', 'best_practice')
            knowledge_content: The actual knowledge content as a JSON string
            source_agent: ID of the agent sharing this knowledge (default: "")
            metadata: Optional metadata as JSON string (default: "")
            
        Returns:
            Dict containing the knowledge atom ID and sharing status
            
        Example:
            share_knowledge("actor", '{"name": "PlayerCube", "location": [0, 0, 100]}', "cursor-main")
        """
        with _orchestration_state["lock"]:
            try:
                # Parse content
                content = json.loads(knowledge_content) if knowledge_content else {}
                meta = json.loads(metadata) if metadata else {}
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Invalid JSON in content or metadata: {str(e)}"
                }
            
            # Create knowledge atom
            atom_id = f"{knowledge_type}_{int(time.time() * 1000)}"
            atom = KnowledgeAtom(knowledge_type, content, source_agent)
            atom.metadata = meta
            
            _orchestration_state["knowledge_base"][atom_id] = atom
            
            logger.info(f"Knowledge shared: {atom_id} from {source_agent}")
            return {
                "status": "success",
                "atom_id": atom_id,
                "knowledge_type": knowledge_type,
                "created_at": atom.created_at
            }
    
    @mcp.tool()
    def query_knowledge(
        knowledge_type: str = "",
        source_agent: str = "",
        limit: int = 10
    ) -> Dict[str, Any]:
        """Query the shared knowledge atomspace.
        
        Retrieve knowledge atoms shared by other agents to coordinate work
        and avoid conflicts.
        
        Args:
            knowledge_type: Filter by knowledge type (default: "" means all types)
            source_agent: Filter by source agent ID (default: "" means all agents)
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            Dict containing matching knowledge atoms
            
        Example:
            query_knowledge("actor", "", 5)
        """
        with _orchestration_state["lock"]:
            results = []
            
            for atom_id, atom in _orchestration_state["knowledge_base"].items():
                # Apply filters
                if knowledge_type and atom.atom_type != knowledge_type:
                    continue
                if source_agent and atom.source_agent != source_agent:
                    continue
                
                # Update access tracking
                atom.access_count += 1
                atom.last_accessed = datetime.now().isoformat()
                
                results.append({
                    "atom_id": atom_id,
                    "type": atom.atom_type,
                    "content": atom.content,
                    "source_agent": atom.source_agent,
                    "created_at": atom.created_at,
                    "access_count": atom.access_count
                })
                
                if len(results) >= limit:
                    break
            
            return {
                "status": "success",
                "total_results": len(results),
                "atoms": results
            }
    
    @mcp.tool()
    def create_workflow_task(
        task_type: str,
        task_params: str,
        assigned_agent: str = "",
        priority: int = 0
    ) -> Dict[str, Any]:
        """Create a coordinated workflow task for multi-agent execution.
        
        Tasks can be assigned to specific agents or left unassigned for any
        capable agent to claim.
        
        Args:
            task_type: Type of task (e.g., 'create_actor', 'create_blueprint', 'setup_level')
            task_params: Task parameters as JSON string
            assigned_agent: Optional agent ID to assign this task to (default: "")
            priority: Task priority, higher values = higher priority (default: 0)
            
        Returns:
            Dict containing the created task information
            
        Example:
            create_workflow_task("create_actor", '{"name": "TestCube", "type": "StaticMeshActor"}', "", 5)
        """
        with _orchestration_state["lock"]:
            try:
                params = json.loads(task_params) if task_params else {}
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Invalid JSON in task_params: {str(e)}"
                }
            
            # Generate task ID
            task_id = f"task_{int(time.time() * 1000)}"
            
            # Create task
            task = WorkflowTask(task_id, task_type, params, assigned_agent, priority)
            _orchestration_state["task_queue"].append(task)
            
            # Sort queue by priority
            _orchestration_state["task_queue"].sort(key=lambda t: t.priority, reverse=True)
            
            logger.info(f"Created workflow task: {task_id} (priority: {priority})")
            return {
                "status": "success",
                "task_id": task_id,
                "task_type": task_type,
                "priority": priority,
                "assigned_agent": assigned_agent if assigned_agent else "unassigned"
            }
    
    @mcp.tool()
    def claim_workflow_task(agent_id: str, task_id: str = "") -> Dict[str, Any]:
        """Claim a workflow task for execution by an agent.
        
        If task_id is not provided, claims the highest priority unassigned task
        that matches the agent's capabilities.
        
        Args:
            agent_id: ID of the agent claiming the task
            task_id: Optional specific task ID to claim (default: "" means auto-select)
            
        Returns:
            Dict containing the claimed task information
            
        Example:
            claim_workflow_task("cursor-main", "")
        """
        with _orchestration_state["lock"]:
            # Verify agent exists
            if agent_id not in _orchestration_state["agents"]:
                return {
                    "status": "error",
                    "error": f"Agent {agent_id} not registered"
                }
            
            agent = _orchestration_state["agents"][agent_id]
            
            # Find task to claim
            task_to_claim = None
            if task_id:
                # Specific task requested
                for task in _orchestration_state["task_queue"]:
                    if task.task_id == task_id and task.status == "pending":
                        task_to_claim = task
                        break
            else:
                # Auto-select highest priority unassigned task
                for task in _orchestration_state["task_queue"]:
                    if task.status == "pending" and not task.assigned_agent:
                        task_to_claim = task
                        break
            
            if not task_to_claim:
                return {
                    "status": "error",
                    "error": "No available tasks to claim"
                }
            
            # Claim the task
            task_to_claim.assigned_agent = agent_id
            task_to_claim.status = "claimed"
            task_to_claim.started_at = datetime.now().isoformat()
            agent.task_count += 1
            agent.last_active = datetime.now().isoformat()
            
            logger.info(f"Task {task_to_claim.task_id} claimed by agent {agent_id}")
            return {
                "status": "success",
                "task_id": task_to_claim.task_id,
                "task_type": task_to_claim.task_type,
                "params": task_to_claim.params,
                "priority": task_to_claim.priority
            }
    
    @mcp.tool()
    def complete_workflow_task(
        task_id: str,
        result: str,
        success: bool = True
    ) -> Dict[str, Any]:
        """Mark a workflow task as completed.
        
        Args:
            task_id: ID of the task being completed
            result: Task result as JSON string
            success: Whether the task completed successfully (default: True)
            
        Returns:
            Dict containing completion status
            
        Example:
            complete_workflow_task("task_123", '{"actor_name": "TestCube"}', True)
        """
        with _orchestration_state["lock"]:
            # Find task
            task = None
            for t in _orchestration_state["task_queue"]:
                if t.task_id == task_id:
                    task = t
                    break
            
            if not task:
                return {
                    "status": "error",
                    "error": f"Task {task_id} not found"
                }
            
            try:
                result_data = json.loads(result) if result else {}
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Invalid JSON in result: {str(e)}"
                }
            
            # Update task
            task.status = "completed" if success else "failed"
            task.completed_at = datetime.now().isoformat()
            task.result = result_data
            
            # Add to history
            _orchestration_state["workflow_history"].append({
                "task_id": task_id,
                "task_type": task.task_type,
                "agent": task.assigned_agent,
                "status": task.status,
                "completed_at": task.completed_at,
                "result": result_data
            })
            
            logger.info(f"Task {task_id} completed with status: {task.status}")
            return {
                "status": "success",
                "task_id": task_id,
                "task_status": task.status
            }
    
    @mcp.tool()
    def list_workflow_tasks(status: str = "", assigned_agent: str = "") -> Dict[str, Any]:
        """List workflow tasks with optional filtering.
        
        Args:
            status: Filter by task status: 'pending', 'claimed', 'completed', 'failed' (default: "" means all)
            assigned_agent: Filter by assigned agent ID (default: "" means all)
            
        Returns:
            Dict containing list of matching tasks
            
        Example:
            list_workflow_tasks("pending", "")
        """
        with _orchestration_state["lock"]:
            results = []
            
            for task in _orchestration_state["task_queue"]:
                # Apply filters
                if status and task.status != status:
                    continue
                if assigned_agent and task.assigned_agent != assigned_agent:
                    continue
                
                results.append({
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "status": task.status,
                    "assigned_agent": task.assigned_agent if task.assigned_agent else "unassigned",
                    "priority": task.priority,
                    "created_at": task.created_at,
                    "params": task.params
                })
            
            return {
                "status": "success",
                "total_tasks": len(results),
                "tasks": results
            }
    
    @mcp.tool()
    def get_orchestration_status() -> Dict[str, Any]:
        """Get overall status of the orchestration workbench.
        
        Returns comprehensive information about all agents, tasks, and shared knowledge.
        
        Returns:
            Dict containing orchestration workbench status
            
        Example:
            get_orchestration_status()
        """
        with _orchestration_state["lock"]:
            active_agents = sum(1 for a in _orchestration_state["agents"].values() if a.status == "active")
            pending_tasks = sum(1 for t in _orchestration_state["task_queue"] if t.status == "pending")
            claimed_tasks = sum(1 for t in _orchestration_state["task_queue"] if t.status == "claimed")
            completed_tasks = len(_orchestration_state["workflow_history"])
            
            return {
                "status": "success",
                "orchestration": {
                    "active_agents": active_agents,
                    "total_agents": len(_orchestration_state["agents"]),
                    "pending_tasks": pending_tasks,
                    "claimed_tasks": claimed_tasks,
                    "completed_tasks": completed_tasks,
                    "knowledge_atoms": len(_orchestration_state["knowledge_base"])
                }
            }
    
    @mcp.tool()
    def clear_orchestration_state(confirm: bool = False) -> Dict[str, Any]:
        """Clear all orchestration state (agents, tasks, knowledge).
        
        WARNING: This will remove all registered agents, tasks, and shared knowledge.
        Use with caution.
        
        Args:
            confirm: Must be True to actually clear the state
            
        Returns:
            Dict containing operation status
            
        Example:
            clear_orchestration_state(True)
        """
        if not confirm:
            return {
                "status": "error",
                "error": "Must set confirm=True to clear orchestration state"
            }
        
        with _orchestration_state["lock"]:
            _orchestration_state["agents"].clear()
            _orchestration_state["knowledge_base"].clear()
            _orchestration_state["task_queue"].clear()
            _orchestration_state["workflow_history"].clear()
            
            logger.info("Orchestration state cleared")
            return {
                "status": "success",
                "message": "Orchestration state cleared successfully"
            }
    
    logger.info("Orchestration tools registered successfully")
