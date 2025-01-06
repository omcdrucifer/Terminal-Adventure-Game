# Tree Node for the story system
from typing import Dict, Any, Optional
from characters import Enemy, Boss
from combat import Combat
from party import Party
from story_content import get_story_content

class StoryNode:
    def __init__(self, node_id, node_type):
        self.node_id = node_id
        self.node_type = node_type
        self.content = {}
        self.choices = []
        self.requirements = {}
        self.consequences = {}

class StoryChoice:
    def __init__(self, choice_id: str, text: str, next_node_id: str, requirements: Optional[Dict[str, Any]] = None):
        self.choice_id: str = choice_id
        self.text: str = text
        self.next_node_id: str = next_node_id
        self.requirements: Dict[str, Any] = requirements or {}

class StoryTree:
    def __init__(self):
        self.nodes = {}
        self.current_node = None

    def add_node(self, node):
        self.nodes[node.node_id] = node

    def start_story(self, starting_node_id):
        self.current_node = self.nodes[starting_node_id]

    def get_available_choices(self, party):
        if not self.current_node or not self.current_node.choices:
            return []
        available = []
        for choice in self.current_node.choices:
            if self._check_requirements(choice.requirements, party):
                available.append(choice)
        return available

    def _check_requirements(self, requirements, party):
        if not requirements:
            return True
        for req_type, req_value in requirements.items():
            if req_type == "party_size":
                party_size = len(party.members)
                min_size = req_value.get("min", 0)
                max_size = req_value.get("max", float('inf'))
                if not (min_size <= party_size <= max_size):
                    return False
        return True

def create_story():
    story = StoryTree()
    story_data = get_story_content()
    
    print("\nDebug - Story data nodes:", list(story_data.keys()))

    for node_id, node_data in story_data.items():
        node = StoryNode(node_id, node_data["type"])
        node.content = node_data.get("content", {})
        story.add_node(node)
        print(f"Debug - Created node: {node_id}")

    for node_id, node_data in story_data.items():
        if "choices" in node_data:
            node = story.nodes[node_id]
            for choice_data in node_data["choices"]:
                choice = StoryChoice(
                    choice_data["id"],
                    choice_data["text"],
                    choice_data["next_node"],
                    choice_data.get("requirements", {})
                )
                node.choices.append(choice)
                print(f"Debug - Added choice to {node_id}: {choice.text} with requirements {choice.requirements}")

    story.start_story("start")
    return story

def handle_story_progression(story, party):
    if not story.current_node:
        return None
        
    current_node = story.current_node
    
    if current_node.node_type == "narrative":
        available_choices = story.get_available_choices(party)
        return {
            "type": "narrative",
            "content": current_node.content,
            "choices": available_choices
        }
        
    elif current_node.node_type == "combat":
        enemy_party = Party("enemy")
        for enemy_type, count in current_node.content["enemies"]:
            for _ in range(count):
                if "Boss" in enemy_type:
                    enemy_party.add_member(Boss(enemy_type, party.get_average_level(), party))
                else:
                    enemy_party.add_member(Enemy(enemy_type, party.get_average_level()))
                    
        combat = Combat(party, enemy_party)
        combat_result = combat.handle_combat_encounter()  # Use the function directly
        
        next_node = (current_node.content["victory_node"] 
                    if combat_result == "VICTORY" 
                    else current_node.content["defeat_node"])
        
        story.current_node = story.nodes[next_node]
        return {"type": "combat_result", "victory": combat_result}
        
    elif current_node.node_type == "recruitment":
        return {
            "type": "recruitment",
            "content": current_node.content
        }
        
    return None
