# Tree Node for the story system
from math import inf
from base_classes import GameEntity
from characters import (
        Player, NPC, Boss, Enemy, Spell,
        initialize_mage_spells, initialize_healer_spells
        )
from combat import Combat
from party import Party

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
        self.requirements = requirements or {}

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
                if party_size < req_value.get("min", 0) or \
                        party_size > req_value.get("max", float('inf')):
                            return False
            elif req_type == "has_class":
                if not any(hasattr(member, "player_class") and
                           member.player_class == req_value
                           for member in party.members):
                    return False
            elif req_type == "min_level":
                if party.get_average_level() < req_value:
                    return False
        return True

# example usage, does not reflect the actual story that will be used
def create_example_story():
    story = StoryTree()

    # Starting narrative node
    start = StoryNode("start", "narrative")
    start.content = {
            "text": "You stand at the entrance of the ancient forest. The path ahead splits in two directions.",
            "description": "A peaceful morning greets you as you prepare for adventure."
            }

    # Solo path choice
    solo_choice = StoryChoice(
            "solo_path",
            "Take the narrow path through the dense forest",
            "solo_combat",
            {"party_size": {"max": 1}}
            )

    # Party path choice
    party_choice = StoryChoice(
            "party_path",
            "Visit the nearby village to seek companions",
            "village_recruitment",
            {"party_size": {"max": 3}}
            )

    start.choices = [solo_choice, party_choice]

    # Solo combat node
    solo_combat = StoryNode("solo_combat", "combat")
    solo_combat.content = {
            "enemies": [("Goblin", 1)],
            "description": "A goblin jumps out from behind a tree!",
            "victory_node": "post_solo_combat",
            "defeat_node": "game_over"
            }

    # Recruitment node
    recruitment = StoryNode("village_recruitment", "recruitment")
    recruitment.content = {
            "available_npcs": [
                {"class": "Fighter", "name": "Roland"},
                {"class": "Healer", "name": "Elena"},
                {"class": "Rogue", "name": "Thresh"}
                ],
            "max_recruits": 2,
            "next_node": "village_quest"
            }

    # Village quest node with party size requirement
    village_quest = StoryNode("village_quest", "choice")
    village_quest.content = {
            "text": "The village elder speaks of a dragon threatening their lands.",
            "description": "You notice your companions grip their weapons tightly."
            }

    # Add choices based on party composition
    quest_choice1 = StoryChoice(
            "accept_quest",
            "Accept the quest to slay the dragon",
            "dragon_path",
            {"party_size": {"min": 2}, "min_level": 3}
            )

    quest_choice2 = StoryChoice(
            "training_first",
            "Suggest training together before taking on the dragon",
            "training_grounds",
            {"party_size": {"min": 1}}
            )

    village_quest.choices = [quest_choice1, quest_choice2]

    # Add all nodes to the story
    story.add_node(start)
    story.add_node(solo_combat)
    story.add_node(recruitment)
    story.add_node(village_quest)

    return story

def handle_story_progression(story, party, choice=None):
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
        combat_result = handle_combat_encounter(party, enemy_party)
        next_node = current_node.content["victory_node"] if combat_result else current_node.content["defeat_node"]
        story.current_node = story.nodes[next_node]
        return {"type": "combat_result", "victory": combat_results}
    elif current_node.node_type == "recruitment":
        return {
            "type": "recruitment",
            "content": current_node.content
            }
    return None
