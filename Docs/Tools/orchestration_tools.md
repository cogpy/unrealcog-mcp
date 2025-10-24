# OpenCog Multi-Agent Orchestration Tools

This document describes the OpenCog-inspired multi-agent orchestration tools for coordinating concurrent AI assistant clients (Cursor, Windsurf, Claude Desktop) in controlling Unreal Engine through the Model Context Protocol (MCP).

## Overview

The orchestration workbench enables multiple AI agents to:
- Register and manage concurrent sessions
- Share knowledge through a distributed atomspace
- Coordinate complex workflows through task delegation
- Avoid conflicts through shared state awareness
- Execute multi-step operations cooperatively

## Architecture

The orchestration system consists of three main components:

### 1. Agent Management
Tracks active AI client sessions, their capabilities, and activity status.

### 2. Knowledge AtomSpace
OpenCog-inspired shared knowledge base where agents can store and retrieve information about actors, blueprints, workflows, and best practices.

### 3. Workflow Coordination
Task queue and delegation system for coordinating multi-agent operations with priority-based execution.

## Tool Reference

### Agent Management Tools

#### `register_agent`
Register a new AI agent session in the orchestration workbench.

**Parameters:**
- `agent_id` (str): Unique identifier for this agent session (e.g., "cursor-session-1")
- `agent_type` (str): Type of AI client - 'cursor', 'windsurf', 'claude_desktop', or 'custom'
- `capabilities` (str): Comma-separated list of capabilities (e.g., "blueprint_creation,actor_spawning")

**Returns:**
```json
{
  "status": "success",
  "message": "Agent cursor-main registered successfully",
  "agent": {
    "id": "cursor-main",
    "type": "cursor",
    "capabilities": ["blueprint_creation", "level_design"],
    "created_at": "2024-10-24T18:30:00.000Z"
  }
}
```

**Example:**
```python
register_agent("cursor-main", "cursor", "blueprint_creation,level_design")
```

#### `list_active_agents`
List all active AI agent sessions.

**Returns:**
```json
{
  "status": "success",
  "total_agents": 2,
  "agents": [
    {
      "id": "cursor-main",
      "type": "cursor",
      "status": "active",
      "capabilities": ["blueprint_creation", "level_design"],
      "task_count": 5,
      "created_at": "2024-10-24T18:30:00.000Z",
      "last_active": "2024-10-24T18:35:00.000Z"
    }
  ]
}
```

#### `deregister_agent`
Deregister an agent session.

**Parameters:**
- `agent_id` (str): Agent identifier to deregister

**Example:**
```python
deregister_agent("cursor-main")
```

#### `get_orchestration_status`
Get comprehensive orchestration workbench status.

**Returns:**
```json
{
  "status": "success",
  "orchestration": {
    "active_agents": 3,
    "total_agents": 5,
    "pending_tasks": 10,
    "claimed_tasks": 2,
    "completed_tasks": 45,
    "knowledge_atoms": 128
  }
}
```

### Knowledge Sharing Tools (AtomSpace)

The knowledge atomspace is inspired by OpenCog's AtomSpace - a hypergraph database for knowledge representation. Agents can share typed knowledge atoms that other agents can query.

#### `share_knowledge`
Share knowledge in the orchestration atomspace.

**Parameters:**
- `knowledge_type` (str): Type of knowledge ('actor', 'blueprint', 'workflow', 'scene_state', 'best_practice', etc.)
- `knowledge_content` (str): Knowledge content as JSON string
- `source_agent` (str): ID of the agent sharing knowledge (optional)
- `metadata` (str): Additional metadata as JSON string (optional)

**Returns:**
```json
{
  "status": "success",
  "atom_id": "actor_1729792800000",
  "knowledge_type": "actor",
  "created_at": "2024-10-24T18:40:00.000Z"
}
```

**Example:**
```python
share_knowledge(
  "actor",
  '{"name": "PlayerCube", "location": [0, 0, 100], "purpose": "player_controller"}',
  "cursor-main",
  '{"level": "MainLevel", "ready_for_use": true}'
)
```

#### `query_knowledge`
Query the shared knowledge atomspace.

**Parameters:**
- `knowledge_type` (str): Filter by type (optional, "" = all types)
- `source_agent` (str): Filter by source agent (optional, "" = all agents)
- `limit` (int): Max results to return (default: 10)

**Returns:**
```json
{
  "status": "success",
  "total_results": 3,
  "atoms": [
    {
      "atom_id": "actor_1729792800000",
      "type": "actor",
      "content": {
        "name": "PlayerCube",
        "location": [0, 0, 100],
        "purpose": "player_controller"
      },
      "source_agent": "cursor-main",
      "created_at": "2024-10-24T18:40:00.000Z",
      "access_count": 5
    }
  ]
}
```

**Example:**
```python
# Query all actor knowledge
query_knowledge("actor", "", 10)

# Query knowledge from specific agent
query_knowledge("", "cursor-main", 20)
```

### Workflow Coordination Tools

#### `create_workflow_task`
Create a coordinated workflow task.

**Parameters:**
- `task_type` (str): Type of task (e.g., 'create_actor', 'create_blueprint')
- `task_params` (str): Task parameters as JSON string
- `assigned_agent` (str): Optional agent to assign task to (optional, "" = unassigned)
- `priority` (int): Task priority, higher = more urgent (default: 0)

**Returns:**
```json
{
  "status": "success",
  "task_id": "task_1729792900000",
  "task_type": "create_actor",
  "priority": 5,
  "assigned_agent": "unassigned"
}
```

**Example:**
```python
create_workflow_task(
  "create_actor",
  '{"name": "TestCube", "type": "StaticMeshActor", "location": [0, 0, 100]}',
  "",
  5
)
```

#### `claim_workflow_task`
Claim a workflow task for execution.

**Parameters:**
- `agent_id` (str): Agent claiming the task
- `task_id` (str): Specific task to claim (optional, "" = auto-select highest priority)

**Returns:**
```json
{
  "status": "success",
  "task_id": "task_1729792900000",
  "task_type": "create_actor",
  "params": {
    "name": "TestCube",
    "type": "StaticMeshActor",
    "location": [0, 0, 100]
  },
  "priority": 5
}
```

**Example:**
```python
# Auto-claim highest priority task
claim_workflow_task("cursor-main", "")

# Claim specific task
claim_workflow_task("windsurf-session-1", "task_1729792900000")
```

#### `complete_workflow_task`
Mark a task as completed.

**Parameters:**
- `task_id` (str): Task identifier
- `result` (str): Task result as JSON string
- `success` (bool): Whether task succeeded (default: True)

**Example:**
```python
complete_workflow_task(
  "task_1729792900000",
  '{"actor_name": "TestCube", "spawned": true}',
  True
)
```

#### `list_workflow_tasks`
List workflow tasks with filtering.

**Parameters:**
- `status` (str): Filter by status ('pending', 'claimed', 'completed', 'failed', "" = all)
- `assigned_agent` (str): Filter by agent (optional, "" = all)

**Returns:**
```json
{
  "status": "success",
  "total_tasks": 5,
  "tasks": [
    {
      "task_id": "task_1729792900000",
      "task_type": "create_actor",
      "status": "pending",
      "assigned_agent": "unassigned",
      "priority": 5,
      "created_at": "2024-10-24T18:45:00.000Z",
      "params": {...}
    }
  ]
}
```

#### `clear_orchestration_state`
Clear all orchestration state.

**Parameters:**
- `confirm` (bool): Must be True to execute

**Warning:** This removes all agents, tasks, and knowledge atoms.

## Usage Patterns

### Pattern 1: Single Agent Session
```python
# 1. Register agent
register_agent("cursor-main", "cursor", "blueprint_creation,actor_spawning")

# 2. Share knowledge about work
share_knowledge("blueprint", '{"name": "PlayerCharacter", "status": "completed"}', "cursor-main")

# 3. Deregister when done
deregister_agent("cursor-main")
```

### Pattern 2: Coordinated Multi-Agent Workflow
```python
# Agent 1 (Cursor) - Blueprint specialist
register_agent("cursor-bp", "cursor", "blueprint_creation")
create_workflow_task("create_blueprint", '{"name": "PlayerCharacter"}', "cursor-bp", 10)

# Agent 2 (Windsurf) - Level designer
register_agent("windsurf-level", "windsurf", "level_design,actor_spawning")
create_workflow_task("setup_level", '{"actors": ["Light", "Camera"]}', "windsurf-level", 5)

# Agent 3 (Claude Desktop) - Coordinator
register_agent("claude-coord", "claude_desktop", "coordination,testing")
status = get_orchestration_status()
# ... coordinate work based on status
```

### Pattern 3: Knowledge Sharing Between Agents
```python
# Agent 1 creates a blueprint
register_agent("agent-1", "cursor", "blueprint_creation")
# ... creates blueprint ...
share_knowledge("blueprint", '{"name": "PlayerCube", "path": "/Game/Blueprints/PlayerCube"}', "agent-1")

# Agent 2 queries and uses the blueprint
register_agent("agent-2", "windsurf", "level_design")
blueprints = query_knowledge("blueprint", "", 10)
# ... spawns blueprint instances in level ...
```

### Pattern 4: Priority-Based Task Queue
```python
# Create tasks with different priorities
create_workflow_task("create_camera", '{"name": "MainCamera"}', "", 10)  # High priority
create_workflow_task("add_lighting", '{"type": "DirectionalLight"}', "", 5)  # Medium
create_workflow_task("add_props", '{"count": 10}', "", 1)  # Low priority

# Agent claims highest priority task first
register_agent("worker-1", "cursor", "all")
task = claim_workflow_task("worker-1", "")  # Gets camera task first
```

## Best Practices

### Agent Registration
1. **Unique IDs**: Use descriptive, unique agent IDs (e.g., "cursor-blueprint-specialist-1")
2. **Accurate Capabilities**: List only capabilities the agent can actually perform
3. **Clean Deregistration**: Always deregister agents when work is complete
4. **Session Management**: Re-register if agent reconnects with same ID

### Knowledge Sharing
1. **Structured Data**: Use consistent JSON schemas for each knowledge type
2. **Meaningful Types**: Create specific knowledge types (e.g., "blueprint_player_controller" vs just "blueprint")
3. **Complete Information**: Include all relevant details in knowledge atoms
4. **Source Attribution**: Always specify source_agent for accountability
5. **Regular Queries**: Check knowledge base before creating duplicate assets

### Workflow Coordination
1. **Clear Task Types**: Use standardized task type names
2. **Complete Parameters**: Provide all necessary parameters in task params
3. **Appropriate Priorities**: Reserve high priorities (>7) for critical tasks
4. **Task Completion**: Always mark tasks as completed with results
5. **Error Handling**: Mark failed tasks appropriately with error details

### Multi-Agent Coordination
1. **Communication**: Agents should query orchestration status regularly
2. **Conflict Avoidance**: Check knowledge base before creating/modifying assets
3. **Work Distribution**: Use agent capabilities to distribute tasks appropriately
4. **Progress Tracking**: Monitor workflow history to understand team progress
5. **State Management**: Periodically clear old completed tasks and knowledge

## Integration with Existing Tools

The orchestration tools work seamlessly with existing Unreal MCP tools:

```python
# Register agent
register_agent("cursor-main", "cursor", "blueprint_creation")

# Create and share blueprint knowledge
# (using existing blueprint_tools)
create_blueprint("PlayerCharacter", "Character")
share_knowledge(
  "blueprint",
  '{"name": "PlayerCharacter", "type": "Character", "status": "created"}',
  "cursor-main"
)

# Coordinate actor spawning
# (using existing editor_tools)
create_workflow_task("spawn_actor", '{"blueprint": "PlayerCharacter", "location": [0,0,100]}', "", 5)
task = claim_workflow_task("cursor-main", "")
# ... execute spawn_actor using existing tools ...
complete_workflow_task(task["task_id"], '{"success": true}', True)
```

## Advanced Features

### Custom Knowledge Types
You can create domain-specific knowledge types:
- `scene_layout`: Overall scene composition
- `lighting_setup`: Lighting configuration
- `gameplay_mechanic`: Game mechanics implementation
- `best_practice`: Lessons learned and recommendations

### Task Dependencies
While not directly supported, you can implement task dependencies using task status and knowledge sharing:

```python
# Task 1: Create blueprint
create_workflow_task("create_blueprint", '{"name": "Player"}', "", 10)
# ... execute and complete ...

# Share completion as knowledge
share_knowledge("task_completion", '{"task": "create_blueprint", "result": "Player"}', "agent-1")

# Task 2: Agent queries knowledge before proceeding
bp_knowledge = query_knowledge("task_completion", "", 10)
if player_blueprint_ready:
    create_workflow_task("spawn_blueprint", '{"name": "Player"}', "", 9)
```

### Agent Specialization
Organize agents by specialization for efficient work distribution:

- **Blueprint Specialists**: `capabilities: "blueprint_creation,node_graphs"`
- **Level Designers**: `capabilities: "level_design,actor_spawning,lighting"`
- **UI Designers**: `capabilities: "umg_widgets,ui_design"`
- **Coordinators**: `capabilities: "coordination,testing,quality_assurance"`

## Troubleshooting

### Agent Not Found
**Problem**: "Agent X not found" when claiming tasks
**Solution**: Ensure agent is registered with `register_agent()` before operations

### No Available Tasks
**Problem**: `claim_workflow_task()` returns "No available tasks"
**Solution**: 
- Create tasks with `create_workflow_task()`
- Check if tasks are already claimed by other agents
- Verify task filters match your query

### Knowledge Not Found
**Problem**: `query_knowledge()` returns empty results
**Solution**:
- Verify knowledge was shared with correct type
- Check filters (knowledge_type, source_agent)
- Increase limit parameter

### Concurrent Modifications
**Problem**: Multiple agents modifying same asset
**Solution**:
- Use knowledge sharing to communicate intent
- Implement task-based coordination
- Query knowledge before modifying assets
- Use workflow tasks for synchronized operations

## Examples

See the `examples/` directory for complete multi-agent orchestration workflows:
- `multi_agent_level_creation.py`: Coordinated level creation with multiple agents
- `knowledge_sharing_demo.py`: Knowledge atomspace usage patterns
- `workflow_coordination_demo.py`: Complex task delegation scenarios

## References

- OpenCog Framework: https://opencog.org/
- AtomSpace Concept: https://wiki.opencog.org/w/AtomSpace
- MCP Protocol: https://modelcontextprotocol.io/
