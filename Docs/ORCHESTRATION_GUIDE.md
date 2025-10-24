# Multi-Agent Orchestration Integration Guide

This guide explains how to use the OpenCog-inspired multi-agent orchestration features with actual AI assistant clients (Cursor, Windsurf, Claude Desktop).

## Overview

The orchestration system allows multiple AI clients to work together on the same Unreal Engine project by coordinating through:
- **Agent Registration**: Each client identifies itself and its capabilities
- **Knowledge Sharing**: Clients share information through a distributed atomspace
- **Workflow Tasks**: Clients coordinate work through a priority-based task queue

## Setup

### Prerequisites
1. Unreal Engine 5.5+ with UnrealMCP plugin enabled
2. Python MCP server running (`unreal_mcp_server.py`)
3. At least one MCP client configured (Cursor, Windsurf, or Claude Desktop)

### MCP Client Configuration

Each client needs to be configured to connect to the Unreal MCP server. See the main README for client-specific configuration locations.

## Natural Language Usage with MCP Clients

### Single Client Usage

When working alone, you can still benefit from orchestration by registering your session:

```
User: Register me as an agent with ID "cursor-main", type "cursor", 
and capabilities "blueprint_creation,level_design"

AI: [Calls register_agent tool]
Registered successfully! You can now share knowledge and create tasks.

User: Create a blueprint called BP_PlayerCharacter

AI: [Uses blueprint_tools to create blueprint]
Created BP_PlayerCharacter successfully.

User: Share knowledge about this blueprint so other agents can use it

AI: [Calls share_knowledge with blueprint details]
Knowledge shared in the atomspace.
```

### Multi-Client Collaboration

#### Example Scenario: Three Agents Creating a Level

**Agent 1 - Blueprint Specialist (Cursor)**
```
User: Register me as "cursor-bp-expert" (cursor) with capability "blueprint_creation"
Then create character blueprints for the game.

AI: Registered as cursor-bp-expert. Creating blueprints...
[Creates BP_Player and BP_Enemy]

User: Share knowledge about the blueprints I created

AI: Sharing knowledge...
- BP_Player blueprint (ready for spawning)
- BP_Enemy blueprint (ready for spawning)
```

**Agent 2 - Level Designer (Windsurf)**  
```
User: Register me as "windsurf-level" (windsurf) with "level_design,lighting"
What blueprints are available?

AI: [Queries knowledge]
Available blueprints:
- BP_Player (created by cursor-bp-expert)
- BP_Enemy (created by cursor-bp-expert)

User: Great! Set up the level lighting and spawn these blueprints

AI: [Creates lighting and spawns actors]
Level setup complete. Sharing scene state knowledge...
```

**Agent 3 - UI Designer (Claude Desktop)**
```
User: Register as "claude-ui" (claude_desktop) with "ui_design"
Check the orchestration status

AI: [Gets status]
Active agents: 3
Knowledge atoms: 8
Completed tasks: 5

User: Create a HUD that shows player health

AI: [Creates UMG widget]
Created WBP_PlayerHUD. Sharing UI widget knowledge...
```

## Best Practices

### Agent Registration
- Register at the start of each work session
- Use descriptive agent IDs
- Accurately list your capabilities
- Deregister when finished

### Knowledge Sharing
- Share after creating important assets
- Include relevant metadata
- Use consistent knowledge types
- Query before creating duplicates

### Task Coordination
- Create tasks for multi-step operations
- Set appropriate priorities
- Claim tasks before starting work
- Always mark tasks as completed

## Common Commands

### Agent Management
```
"Register me as [id] with type [type] and capabilities [caps]"
"List all active agents"
"Deregister my agent"
"Get orchestration status"
```

### Knowledge Sharing
```
"Share knowledge about [asset]"
"Query knowledge of type [type]"
"What knowledge is available from [agent]?"
```

### Workflow Tasks
```
"Create a task to [action] with priority [N]"
"Claim the highest priority task"
"List pending tasks"
"Complete task [id]"
```

## Troubleshooting

### Agent Already Registered
If you reconnect with the same ID, the system will reactivate your existing session.

### Knowledge Not Found
Query with broader filters or check agent IDs and knowledge types.

### No Available Tasks
Create new tasks or check if all tasks are already claimed/completed.

## Example Workflows

See the example scripts in `scripts/orchestration/` for complete working examples.
