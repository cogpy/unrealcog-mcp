#!/usr/bin/env python
"""
Multi-Agent Orchestration Demo

This script demonstrates the OpenCog-inspired multi-agent orchestration capabilities
for coordinating multiple AI clients working together on Unreal Engine projects.

The demo shows:
- Agent registration and management
- Knowledge sharing through the atomspace
- Workflow task coordination
- Multi-agent collaborative work patterns
"""

import sys
import os
import time
import socket
import json
import logging
from typing import Dict, Any, Optional

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OrchestrationDemo")

def send_command(command: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Send a command to the Unreal MCP server and get the response."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", 55557))
        
        try:
            command_obj = {
                "type": command,
                "params": params
            }
            
            command_json = json.dumps(command_obj)
            logger.info(f"Sending command: {command}")
            sock.sendall(command_json.encode('utf-8'))
            
            # Receive response
            chunks = []
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
                
                try:
                    data = b''.join(chunks)
                    json.loads(data.decode('utf-8'))
                    break
                except json.JSONDecodeError:
                    continue
            
            data = b''.join(chunks)
            response = json.loads(data.decode('utf-8'))
            logger.info(f"Response status: {response.get('status', 'unknown')}")
            return response
            
        finally:
            sock.close()
            
    except Exception as e:
        logger.error(f"Error sending command: {e}")
        return None

def demo_agent_registration():
    """Demonstrate agent registration and management."""
    logger.info("\n=== DEMO 1: Agent Registration ===")
    
    # Register multiple agents with different capabilities
    agents = [
        ("cursor-blueprint-specialist", "cursor", "blueprint_creation,node_graphs"),
        ("windsurf-level-designer", "windsurf", "level_design,actor_spawning,lighting"),
        ("claude-ui-designer", "claude_desktop", "umg_widgets,ui_design"),
    ]
    
    for agent_id, agent_type, capabilities in agents:
        result = send_command("register_agent", {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "capabilities": capabilities
        })
        if result and result.get("status") == "success":
            logger.info(f"✓ Registered {agent_id}")
        else:
            logger.error(f"✗ Failed to register {agent_id}")
    
    # List active agents
    time.sleep(0.5)
    result = send_command("list_active_agents", {})
    if result and result.get("status") == "success":
        logger.info(f"\nActive agents: {result.get('total_agents', 0)}")
        for agent in result.get("agents", []):
            logger.info(f"  - {agent['id']} ({agent['type']}): {', '.join(agent['capabilities'])}")

def demo_knowledge_sharing():
    """Demonstrate knowledge sharing through the atomspace."""
    logger.info("\n=== DEMO 2: Knowledge Sharing ===")
    
    # Agent 1 shares blueprint knowledge
    knowledge_items = [
        {
            "type": "blueprint",
            "content": json.dumps({
                "name": "PlayerCharacter",
                "path": "/Game/Blueprints/PlayerCharacter",
                "status": "completed",
                "components": ["SkeletalMesh", "Camera", "Movement"]
            }),
            "agent": "cursor-blueprint-specialist"
        },
        {
            "type": "actor",
            "content": json.dumps({
                "name": "MainLight",
                "type": "DirectionalLight",
                "location": [0, 0, 500],
                "intensity": 5.0
            }),
            "agent": "windsurf-level-designer"
        },
        {
            "type": "best_practice",
            "content": json.dumps({
                "topic": "blueprint_naming",
                "recommendation": "Use BP_ prefix for all blueprints",
                "reason": "Improves organization and searchability"
            }),
            "agent": "cursor-blueprint-specialist"
        }
    ]
    
    for item in knowledge_items:
        result = send_command("share_knowledge", {
            "knowledge_type": item["type"],
            "knowledge_content": item["content"],
            "source_agent": item["agent"],
            "metadata": json.dumps({"demo": True})
        })
        if result and result.get("status") == "success":
            logger.info(f"✓ Shared {item['type']} knowledge from {item['agent']}")
    
    # Query knowledge
    time.sleep(0.5)
    logger.info("\nQuerying blueprint knowledge:")
    result = send_command("query_knowledge", {
        "knowledge_type": "blueprint",
        "source_agent": "",
        "limit": 10
    })
    if result and result.get("status") == "success":
        for atom in result.get("atoms", []):
            logger.info(f"  - {atom['type']}: {atom['content'].get('name', 'N/A')} (by {atom['source_agent']})")
    
    # Query all knowledge
    time.sleep(0.5)
    logger.info("\nQuerying all knowledge:")
    result = send_command("query_knowledge", {
        "knowledge_type": "",
        "source_agent": "",
        "limit": 20
    })
    if result and result.get("status") == "success":
        logger.info(f"Total knowledge atoms: {result.get('total_results', 0)}")

def demo_workflow_coordination():
    """Demonstrate workflow task coordination."""
    logger.info("\n=== DEMO 3: Workflow Coordination ===")
    
    # Create workflow tasks with different priorities
    tasks = [
        {
            "type": "create_blueprint",
            "params": json.dumps({"name": "PlayerCharacter", "parent": "Character"}),
            "agent": "",  # Unassigned
            "priority": 10
        },
        {
            "type": "create_actor",
            "params": json.dumps({"name": "MainCamera", "type": "CameraActor"}),
            "agent": "windsurf-level-designer",  # Pre-assigned
            "priority": 8
        },
        {
            "type": "create_umg_widget",
            "params": json.dumps({"name": "MainMenu", "parent": "UserWidget"}),
            "agent": "",
            "priority": 5
        },
        {
            "type": "setup_lighting",
            "params": json.dumps({"type": "DirectionalLight", "intensity": 5.0}),
            "agent": "",
            "priority": 3
        }
    ]
    
    for task in tasks:
        result = send_command("create_workflow_task", {
            "task_type": task["type"],
            "task_params": task["params"],
            "assigned_agent": task["agent"],
            "priority": task["priority"]
        })
        if result and result.get("status") == "success":
            logger.info(f"✓ Created task: {task['type']} (priority: {task['priority']})")
    
    # List pending tasks
    time.sleep(0.5)
    logger.info("\nPending workflow tasks:")
    result = send_command("list_workflow_tasks", {
        "status": "pending",
        "assigned_agent": ""
    })
    if result and result.get("status") == "success":
        for task in result.get("tasks", []):
            logger.info(f"  - [{task['priority']}] {task['task_type']} -> {task['assigned_agent']}")
    
    # Agent claims highest priority task
    time.sleep(0.5)
    logger.info("\nAgent claiming highest priority task:")
    result = send_command("claim_workflow_task", {
        "agent_id": "cursor-blueprint-specialist",
        "task_id": ""  # Auto-select
    })
    if result and result.get("status") == "success":
        logger.info(f"✓ Claimed task: {result.get('task_type')} (ID: {result.get('task_id')})")
        
        # Complete the task
        time.sleep(0.5)
        complete_result = send_command("complete_workflow_task", {
            "task_id": result.get("task_id"),
            "result": json.dumps({"status": "blueprint_created", "name": "PlayerCharacter"}),
            "success": True
        })
        if complete_result and complete_result.get("status") == "success":
            logger.info(f"✓ Completed task: {result.get('task_id')}")

def demo_orchestration_status():
    """Demonstrate getting orchestration status."""
    logger.info("\n=== DEMO 4: Orchestration Status ===")
    
    result = send_command("get_orchestration_status", {})
    if result and result.get("status") == "success":
        orch = result.get("orchestration", {})
        logger.info(f"""
Orchestration Workbench Status:
  Active Agents: {orch.get('active_agents', 0)} / {orch.get('total_agents', 0)}
  Pending Tasks: {orch.get('pending_tasks', 0)}
  Claimed Tasks: {orch.get('claimed_tasks', 0)}
  Completed Tasks: {orch.get('completed_tasks', 0)}
  Knowledge Atoms: {orch.get('knowledge_atoms', 0)}
""")

def demo_multi_agent_collaboration():
    """Demonstrate multiple agents working together."""
    logger.info("\n=== DEMO 5: Multi-Agent Collaboration ===")
    
    # Scenario: Creating a game level with multiple agents
    logger.info("Scenario: Multiple agents collaborate on level creation")
    
    # Agent 1: Blueprint specialist shares completed blueprint
    logger.info("\n[Cursor Blueprint Specialist]")
    result = send_command("share_knowledge", {
        "knowledge_type": "blueprint",
        "knowledge_content": json.dumps({
            "name": "EnemyCharacter",
            "path": "/Game/Blueprints/EnemyCharacter",
            "status": "ready",
            "ai_enabled": True
        }),
        "source_agent": "cursor-blueprint-specialist",
        "metadata": json.dumps({"ready_for_spawning": True})
    })
    logger.info("✓ Shared blueprint: EnemyCharacter")
    
    # Agent 2: Level designer queries blueprints and creates spawn task
    time.sleep(0.5)
    logger.info("\n[Windsurf Level Designer]")
    result = send_command("query_knowledge", {
        "knowledge_type": "blueprint",
        "source_agent": "",
        "limit": 10
    })
    logger.info(f"✓ Queried blueprints, found {result.get('total_results', 0)} available")
    
    result = send_command("create_workflow_task", {
        "task_type": "spawn_blueprint_actors",
        "task_params": json.dumps({
            "blueprint": "EnemyCharacter",
            "count": 5,
            "area": {"min": [-500, -500], "max": [500, 500]}
        }),
        "assigned_agent": "windsurf-level-designer",
        "priority": 7
    })
    logger.info("✓ Created task: Spawn 5 enemy characters")
    
    # Agent 3: UI designer creates HUD task
    time.sleep(0.5)
    logger.info("\n[Claude UI Designer]")
    result = send_command("create_workflow_task", {
        "task_type": "create_hud",
        "task_params": json.dumps({
            "widget_name": "GameplayHUD",
            "elements": ["health_bar", "ammo_counter", "minimap"]
        }),
        "assigned_agent": "claude-ui-designer",
        "priority": 6
    })
    logger.info("✓ Created task: Create gameplay HUD")
    
    # Share best practice
    result = send_command("share_knowledge", {
        "knowledge_type": "best_practice",
        "knowledge_content": json.dumps({
            "topic": "hud_optimization",
            "recommendation": "Use widget pooling for frequently updated elements",
            "impact": "Reduces garbage collection overhead"
        }),
        "source_agent": "claude-ui-designer",
        "metadata": json.dumps({})
    })
    logger.info("✓ Shared best practice: HUD optimization")

def cleanup():
    """Clean up demo state."""
    logger.info("\n=== CLEANUP ===")
    
    # Deregister agents
    agents = [
        "cursor-blueprint-specialist",
        "windsurf-level-designer",
        "claude-ui-designer"
    ]
    
    for agent_id in agents:
        result = send_command("deregister_agent", {"agent_id": agent_id})
        if result and result.get("status") == "success":
            logger.info(f"✓ Deregistered {agent_id}")

def main():
    """Main demo function."""
    logger.info("=" * 60)
    logger.info("OpenCog Multi-Agent Orchestration Demo")
    logger.info("=" * 60)
    
    try:
        # Run demos in sequence
        demo_agent_registration()
        time.sleep(1)
        
        demo_knowledge_sharing()
        time.sleep(1)
        
        demo_workflow_coordination()
        time.sleep(1)
        
        demo_orchestration_status()
        time.sleep(1)
        
        demo_multi_agent_collaboration()
        time.sleep(1)
        
        # Final status
        demo_orchestration_status()
        
        logger.info("\n" + "=" * 60)
        logger.info("Demo completed successfully!")
        logger.info("=" * 60)
        
        # Cleanup
        cleanup()
        
    except Exception as e:
        logger.error(f"Error in demo: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
