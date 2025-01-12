from party import Party
from combat import Combat
from enemy_classes import Enemy
from boss_classes import Boss
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
    def __init__(self, choice_id, text, next_node_id, requirements=None):
        self.choice_id = choice_id
        self.text = text
        self.next_node_id = next_node_id
        self.requirements = requirements

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
            if req_type == "min_level":
                if party.get_average_level() < req_value:
                    return False
            if req_type == "party_size":
                party_size = len(party.members)
                min_size = req_value.get("min", 0)
                max_size = req_value.get("max", float("inf"))
                if not (min_size <= party_size <= max_size):
                    return False
        return True

def create_story():
    story = StoryTree()
    story_data = get_story_content()

    for node_id, node_data in story_data.items():
        node = StoryNode(node_id, node_data["type"])
        node.content = node_data["content"]
        node.requirements = node_data.get("requirements", {})
        node.consequences = node_data.get("consequences", {})
        for choice_id, choice_data in node_data.get("choices", {}).items():
            choice = StoryChoice(
                    choice_id,
                    choice_data["text"],
                    choice_data["next_node_id"],
                    choice_data.get("requirements", {})
                    )
            node.choices.append(choice)
        story.add_node(node)

    if "game_over" not in story.nodes:
        game_over_node = StoryNode("game_over", "narrative")
        game_over_node.content = {"text": "Game Over. You have been defeated.", "description": ""}
        story.add_node(game_over_node)

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
        for enemy_type, count in current_node.content["enemies"].items():
            for _ in range(count):
                if "Boss" in enemy_type:
                    enemy_party.add_member(Boss(enemy_type, party.get_average_level()))
                elif "Enemy" in enemy_type:
                    enemy_party.add_member(Enemy(enemy_type, party.get_average_level()))

        combat  = Combat(party, enemy_party)
        combat_result = combat.handle_combat_encounter()

        next_node = (current_node.content["victory_node"]
                if combat_result == "VICTORY"
                else current_node.content["defeat_node"]
                )
        if next_node not in story.nodes:
            next_node = "game_over"

        story.current_node = story.nodes[next_node]
        return {"type": "combat_result", "victory": combat_result}
    
    elif current_node.node_type == "recruitment":
        return {
                "type": "recruitment",
                "content": current_node.content
                }

    return None
