# OpenCog Multi-Agent Orchestration Examples

This directory contains example scripts demonstrating the OpenCog-inspired multi-agent orchestration capabilities of Unreal MCP.

## Overview

These scripts showcase how multiple AI assistant clients (Cursor, Windsurf, Claude Desktop) can work together collaboratively on Unreal Engine projects through coordinated workflows, knowledge sharing, and task delegation.

## Prerequisites

1. **Unreal Engine** with UnrealMCP plugin running
2. **Python dependencies** installed (see `../README.md`)
3. **TCP connection** to Unreal Engine on port 55557

## Scripts

### `demo_orchestration.py`
A comprehensive demonstration of all orchestration features:
- Agent registration and management
- Knowledge sharing through the atomspace
- Workflow task creation and coordination
- Multi-agent collaboration patterns
- Orchestration status monitoring

**Usage:**
```bash
python3 demo_orchestration.py
```

**What it demonstrates:**
- Registering 3 different AI agent types (Cursor, Windsurf, Claude Desktop)
- Sharing various types of knowledge (blueprints, actors, best practices)
- Creating and managing workflow tasks with priorities
- Claiming and completing tasks
- Querying orchestration state

### `multi_agent_level_creation.py`
A realistic scenario where three specialized AI agents collaborate to create a complete game level:

1. **Blueprint Specialist (Cursor)** - Creates character blueprints
2. **Level Designer (Windsurf)** - Sets up environment and lighting
3. **UI Designer (Claude Desktop)** - Creates game interface

**Usage:**
```bash
python3 multi_agent_level_creation.py
```

**What it demonstrates:**
- Phased workflow with dependencies
- Knowledge sharing between specialized agents
- Coordinated task execution
- Real-world multi-agent collaboration patterns
- Integration of multiple game systems

## Running the Examples

### Without Unreal Engine (Testing Only)
These scripts will fail to execute actual Unreal commands but you can review the code:
```bash
# Just syntax check
python3 -m py_compile demo_orchestration.py
python3 -m py_compile multi_agent_level_creation.py
```

### With Unreal Engine
1. Start Unreal Engine with the UnrealMCP plugin enabled
2. Ensure the editor is in a valid state (project loaded)
3. Run the example scripts:
```bash
# Run the basic demo
python3 demo_orchestration.py

# Run the level creation example
python3 multi_agent_level_creation.py
```

## Understanding the Output

The scripts produce detailed logging output showing:
- Agent registration and deregistration
- Knowledge atoms being created and queried
- Workflow tasks being created, claimed, and completed
- Final orchestration status

Example output:
```
=== DEMO 1: Agent Registration ===
✓ Registered cursor-blueprint-specialist
✓ Registered windsurf-level-designer
✓ Registered claude-ui-designer

Active agents: 3
  - cursor-blueprint-specialist (cursor): blueprint_creation, node_graphs
  - windsurf-level-designer (windsurf): level_design, actor_spawning, lighting
  - claude-ui-designer (claude_desktop): umg_widgets, ui_design
```

## Key Concepts

### Agent Registration
Each AI client registers with:
- Unique agent ID
- Agent type (cursor, windsurf, claude_desktop, custom)
- List of capabilities

### Knowledge AtomSpace
OpenCog-inspired shared knowledge base where agents store:
- Blueprint information
- Actor configurations
- Scene state
- Best practices
- Any custom knowledge types

### Workflow Tasks
Coordinated tasks with:
- Task type and parameters
- Priority level (higher = more urgent)
- Assignment (specific agent or unassigned)
- Status tracking (pending, claimed, completed, failed)

## Customization

You can customize these examples by:

1. **Adding New Agent Types:**
```python
custom_agent = Agent("my-agent", "custom", ["special_capability"])
```

2. **Creating Custom Knowledge Types:**
```python
agent.share_knowledge(
    "custom_type",
    {"my_field": "my_value"},
    {"metadata": "optional"}
)
```

3. **Adding New Task Types:**
```python
agent.create_task(
    "my_custom_task",
    {"param1": "value1"},
    priority=7
)
```

## Best Practices

1. **Unique Agent IDs**: Use descriptive IDs like "cursor-blueprint-specialist-session1"
2. **Appropriate Capabilities**: Only list capabilities the agent can actually perform
3. **Clean Deregistration**: Always deregister agents when work is complete
4. **Knowledge Sharing**: Share knowledge liberally to help other agents
5. **Task Priorities**: Reserve high priorities (8-10) for critical tasks
6. **Error Handling**: Check command responses and handle failures gracefully

## Troubleshooting

### "Connection refused" error
- Ensure Unreal Engine is running
- Check that the UnrealMCP plugin is enabled
- Verify TCP port 55557 is accessible

### "Agent not found" error
- Ensure agent is registered before claiming tasks
- Check agent ID spelling

### Tasks not being claimed
- Verify tasks are created with appropriate priorities
- Check that agents have matching capabilities
- List tasks with `list_workflow_tasks()` to debug

## Further Reading

- [Orchestration Tools Documentation](../../Docs/Tools/orchestration_tools.md)
- [OpenCog Framework](https://opencog.org/)
- [MCP Protocol](https://modelcontextprotocol.io/)

## Contributing

Feel free to create additional examples demonstrating:
- Different multi-agent collaboration patterns
- Advanced knowledge sharing techniques
- Complex workflow coordination scenarios
- Integration with specific game development workflows
