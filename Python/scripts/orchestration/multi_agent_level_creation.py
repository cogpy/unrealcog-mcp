#!/usr/bin/env python
"""
Multi-Agent Level Creation Example

This example demonstrates a realistic scenario where three AI agents collaborate
to create a complete game level in Unreal Engine:

1. Blueprint Specialist (Cursor) - Creates game character blueprints
2. Level Designer (Windsurf) - Sets up the level layout and lighting
3. UI Designer (Claude Desktop) - Creates the game HUD and menus

The agents coordinate through the orchestration system, sharing knowledge
and managing workflow tasks to create a cohesive game level.
"""

import sys
import os
import time
import socket
import json
import logging
from typing import Dict, Any, Optional, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(name)s] %(message)s')
logger = logging.getLogger("MultiAgentLevel")

def send_command(command: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Send a command to the Unreal MCP server."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", 55557))
        
        try:
            command_obj = {"type": command, "params": params}
            sock.sendall(json.dumps(command_obj).encode('utf-8'))
            
            chunks = []
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
                try:
                    json.loads(b''.join(chunks).decode('utf-8'))
                    break
                except json.JSONDecodeError:
                    continue
            
            return json.loads(b''.join(chunks).decode('utf-8'))
        finally:
            sock.close()
    except Exception as e:
        logger.error(f"Command error: {e}")
        return None

class Agent:
    """Represents an AI agent in the orchestration."""
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.registered = False
    
    def register(self):
        """Register this agent with the orchestration system."""
        result = send_command("register_agent", {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": ",".join(self.capabilities)
        })
        if result and result.get("status") == "success":
            self.registered = True
            logger.info(f"✓ {self.agent_id} registered")
            return True
        return False
    
    def share_knowledge(self, knowledge_type: str, content: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Share knowledge in the atomspace."""
        result = send_command("share_knowledge", {
            "knowledge_type": knowledge_type,
            "knowledge_content": json.dumps(content),
            "source_agent": self.agent_id,
            "metadata": json.dumps(metadata or {})
        })
        if result and result.get("status") == "success":
            logger.info(f"  {self.agent_id}: Shared {knowledge_type} knowledge")
            return result.get("atom_id")
        return None
    
    def create_task(self, task_type: str, params: Dict[str, Any], priority: int = 5):
        """Create a workflow task."""
        result = send_command("create_workflow_task", {
            "task_type": task_type,
            "task_params": json.dumps(params),
            "assigned_agent": self.agent_id,
            "priority": priority
        })
        if result and result.get("status") == "success":
            logger.info(f"  {self.agent_id}: Created task '{task_type}' (priority {priority})")
            return result.get("task_id")
        return None
    
    def claim_task(self, task_id: str = ""):
        """Claim a workflow task."""
        result = send_command("claim_workflow_task", {
            "agent_id": self.agent_id,
            "task_id": task_id
        })
        if result and result.get("status") == "success":
            logger.info(f"  {self.agent_id}: Claimed task '{result.get('task_type')}'")
            return result
        return None
    
    def complete_task(self, task_id: str, result_data: Dict[str, Any], success: bool = True):
        """Mark a task as completed."""
        result = send_command("complete_workflow_task", {
            "task_id": task_id,
            "result": json.dumps(result_data),
            "success": success
        })
        if result and result.get("status") == "success":
            logger.info(f"  {self.agent_id}: Completed task {task_id}")
            return True
        return False
    
    def query_knowledge(self, knowledge_type: str = "", limit: int = 10):
        """Query the knowledge atomspace."""
        result = send_command("query_knowledge", {
            "knowledge_type": knowledge_type,
            "source_agent": "",
            "limit": limit
        })
        if result and result.get("status") == "success":
            return result.get("atoms", [])
        return []
    
    def deregister(self):
        """Deregister this agent."""
        result = send_command("deregister_agent", {"agent_id": self.agent_id})
        if result and result.get("status") == "success":
            self.registered = False
            logger.info(f"✓ {self.agent_id} deregistered")
            return True
        return False

def phase1_blueprint_creation(blueprint_agent: Agent):
    """Phase 1: Blueprint specialist creates character blueprints."""
    logger.info("\n=== PHASE 1: Blueprint Creation ===")
    logger.info("Blueprint Specialist creating game characters...")
    
    # Create player character blueprint
    blueprint_agent.create_task(
        "create_blueprint",
        {
            "name": "BP_PlayerCharacter",
            "parent": "Character",
            "components": ["SkeletalMesh", "Camera", "SpringArm", "CharacterMovement"]
        },
        priority=10
    )
    
    # Simulate blueprint creation work
    time.sleep(0.3)
    
    # Share blueprint knowledge
    blueprint_agent.share_knowledge(
        "blueprint",
        {
            "name": "BP_PlayerCharacter",
            "path": "/Game/Blueprints/BP_PlayerCharacter",
            "type": "Character",
            "status": "completed",
            "features": ["third_person_camera", "wasd_movement", "jump"]
        },
        {"phase": "1", "ready_for_spawning": True}
    )
    
    # Create enemy character
    blueprint_agent.create_task(
        "create_blueprint",
        {
            "name": "BP_EnemyBot",
            "parent": "Character",
            "components": ["SkeletalMesh", "AIController"]
        },
        priority=9
    )
    
    time.sleep(0.3)
    
    blueprint_agent.share_knowledge(
        "blueprint",
        {
            "name": "BP_EnemyBot",
            "path": "/Game/Blueprints/BP_EnemyBot",
            "type": "Character",
            "status": "completed",
            "features": ["ai_navigation", "patrol_behavior"]
        },
        {"phase": "1", "ready_for_spawning": True}
    )
    
    # Share best practice
    blueprint_agent.share_knowledge(
        "best_practice",
        {
            "topic": "character_blueprints",
            "recommendation": "Always use CharacterMovement component for player-controlled characters",
            "reason": "Provides built-in movement replication and network support"
        }
    )
    
    logger.info("✓ Blueprint creation phase completed")

def phase2_level_design(level_agent: Agent):
    """Phase 2: Level designer sets up the environment."""
    logger.info("\n=== PHASE 2: Level Design ===")
    logger.info("Level Designer setting up game environment...")
    
    # Query available blueprints
    blueprints = level_agent.query_knowledge("blueprint", limit=10)
    logger.info(f"  Found {len(blueprints)} blueprints available for spawning")
    
    # Create lighting setup task
    level_agent.create_task(
        "setup_lighting",
        {
            "lights": [
                {"type": "DirectionalLight", "name": "MainSun", "intensity": 5.0, "angle": [45, 0, 0]},
                {"type": "SkyLight", "name": "SkySphere", "intensity": 1.0}
            ]
        },
        priority=8
    )
    
    time.sleep(0.3)
    
    # Share lighting knowledge
    level_agent.share_knowledge(
        "scene_state",
        {
            "aspect": "lighting",
            "status": "configured",
            "lights": ["MainSun", "SkySphere"],
            "quality": "production"
        },
        {"phase": "2"}
    )
    
    # Create spawn points for player and enemies
    level_agent.create_task(
        "create_spawn_points",
        {
            "player_spawn": {"location": [0, 0, 100], "rotation": [0, 0, 0]},
            "enemy_spawns": [
                {"location": [500, 500, 100]},
                {"location": [-500, 500, 100]},
                {"location": [500, -500, 100]},
                {"location": [-500, -500, 100]}
            ]
        },
        priority=7
    )
    
    time.sleep(0.3)
    
    # Share spawn point knowledge
    level_agent.share_knowledge(
        "scene_state",
        {
            "aspect": "spawn_points",
            "status": "configured",
            "player_spawn_ready": True,
            "enemy_spawn_count": 4
        },
        {"phase": "2"}
    )
    
    # Add environment props
    level_agent.create_task(
        "add_environment_props",
        {
            "props": [
                {"type": "StaticMeshActor", "mesh": "Floor", "scale": [10, 10, 1]},
                {"type": "StaticMeshActor", "mesh": "Wall", "count": 4}
            ]
        },
        priority=5
    )
    
    logger.info("✓ Level design phase completed")

def phase3_ui_creation(ui_agent: Agent):
    """Phase 3: UI designer creates game interface."""
    logger.info("\n=== PHASE 3: UI Creation ===")
    logger.info("UI Designer creating game interface...")
    
    # Query scene state to understand what needs UI
    scene_state = ui_agent.query_knowledge("scene_state", limit=10)
    logger.info(f"  Reviewed {len(scene_state)} scene state atoms for context")
    
    # Create main menu task
    ui_agent.create_task(
        "create_main_menu",
        {
            "widget_name": "WBP_MainMenu",
            "elements": [
                {"type": "Button", "text": "Start Game", "action": "start_game"},
                {"type": "Button", "text": "Settings", "action": "open_settings"},
                {"type": "Button", "text": "Quit", "action": "quit_game"}
            ]
        },
        priority=6
    )
    
    time.sleep(0.3)
    
    ui_agent.share_knowledge(
        "ui_widget",
        {
            "name": "WBP_MainMenu",
            "path": "/Game/UI/WBP_MainMenu",
            "type": "menu",
            "status": "completed"
        },
        {"phase": "3"}
    )
    
    # Create gameplay HUD
    ui_agent.create_task(
        "create_gameplay_hud",
        {
            "widget_name": "WBP_GameplayHUD",
            "elements": [
                {"type": "ProgressBar", "name": "HealthBar", "binding": "player_health"},
                {"type": "TextBlock", "name": "AmmoCounter", "binding": "player_ammo"},
                {"type": "Image", "name": "Crosshair", "centered": True}
            ]
        },
        priority=7
    )
    
    time.sleep(0.3)
    
    ui_agent.share_knowledge(
        "ui_widget",
        {
            "name": "WBP_GameplayHUD",
            "path": "/Game/UI/WBP_GameplayHUD",
            "type": "hud",
            "status": "completed",
            "bindings": ["player_health", "player_ammo"]
        },
        {"phase": "3", "ready_for_game": True}
    )
    
    # Share UI best practice
    ui_agent.share_knowledge(
        "best_practice",
        {
            "topic": "hud_performance",
            "recommendation": "Use property bindings sparingly, cache widget references",
            "reason": "Reduces per-frame overhead and improves game performance"
        }
    )
    
    logger.info("✓ UI creation phase completed")

def phase4_integration(all_agents: List[Agent]):
    """Phase 4: Final integration and coordination."""
    logger.info("\n=== PHASE 4: Integration & Coordination ===")
    logger.info("All agents coordinating final integration...")
    
    # Each agent reviews shared knowledge
    for agent in all_agents:
        knowledge = agent.query_knowledge("", limit=50)
        logger.info(f"  {agent.agent_id}: Reviewed {len(knowledge)} knowledge atoms")
    
    # Create integration tasks
    coordinator = all_agents[0]  # Use first agent as coordinator
    
    coordinator.create_task(
        "integrate_gameplay",
        {
            "player_blueprint": "BP_PlayerCharacter",
            "enemy_blueprint": "BP_EnemyBot",
            "hud_widget": "WBP_GameplayHUD",
            "spawn_points": "configured"
        },
        priority=10
    )
    
    time.sleep(0.3)
    
    # Share final integration status
    coordinator.share_knowledge(
        "project_status",
        {
            "phase": "integration",
            "status": "completed",
            "components": {
                "blueprints": "ready",
                "level": "ready",
                "ui": "ready"
            },
            "ready_for_testing": True
        }
    )
    
    logger.info("✓ Integration phase completed")

def show_final_status():
    """Display final orchestration status."""
    logger.info("\n=== FINAL STATUS ===")
    result = send_command("get_orchestration_status", {})
    if result and result.get("status") == "success":
        orch = result.get("orchestration", {})
        logger.info(f"""
Multi-Agent Level Creation Summary:
  Active Agents: {orch.get('active_agents', 0)}
  Total Tasks Created: {orch.get('completed_tasks', 0)}
  Knowledge Atoms Shared: {orch.get('knowledge_atoms', 0)}
  
The agents successfully collaborated to create:
  • Player and enemy character blueprints
  • Complete level lighting and environment
  • Main menu and gameplay HUD
  • Integrated gameplay system
""")
    
    # Show some knowledge highlights
    result = send_command("query_knowledge", {"knowledge_type": "", "source_agent": "", "limit": 5})
    if result and result.get("status") == "success":
        logger.info("Knowledge Highlights:")
        for atom in result.get("atoms", []):
            logger.info(f"  • {atom['type']}: {atom['content'].get('name', atom['content'].get('topic', 'N/A'))}")

def main():
    """Main workflow orchestration."""
    logger.info("=" * 70)
    logger.info("Multi-Agent Level Creation Example")
    logger.info("Demonstrating OpenCog-Inspired AI Collaboration in Unreal Engine")
    logger.info("=" * 70)
    
    try:
        # Create agents
        blueprint_specialist = Agent(
            "cursor-blueprint-specialist",
            "cursor",
            ["blueprint_creation", "node_graphs", "component_setup"]
        )
        
        level_designer = Agent(
            "windsurf-level-designer",
            "windsurf",
            ["level_design", "actor_spawning", "lighting", "environment"]
        )
        
        ui_designer = Agent(
            "claude-ui-designer",
            "claude_desktop",
            ["umg_widgets", "ui_design", "ux"]
        )
        
        all_agents = [blueprint_specialist, level_designer, ui_designer]
        
        # Register all agents
        logger.info("\nRegistering AI agents...")
        for agent in all_agents:
            agent.register()
            time.sleep(0.2)
        
        # Execute phases
        phase1_blueprint_creation(blueprint_specialist)
        time.sleep(0.5)
        
        phase2_level_design(level_designer)
        time.sleep(0.5)
        
        phase3_ui_creation(ui_designer)
        time.sleep(0.5)
        
        phase4_integration(all_agents)
        time.sleep(0.5)
        
        # Show final status
        show_final_status()
        
        # Cleanup
        logger.info("\nCleaning up...")
        for agent in all_agents:
            agent.deregister()
            time.sleep(0.2)
        
        logger.info("\n" + "=" * 70)
        logger.info("Multi-agent collaboration completed successfully!")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Error in workflow: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
