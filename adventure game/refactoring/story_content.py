def get_story_content():
    return {
            "start": {
                "type": "narrative",
                "content": {
                    "text": "You stand at the entrance of the ancient forest...",
                    "description": "A peaceful morning greets you..."
                    },
                "choices": [
                    {
                        "id": "choice_solo",
                        "text": "Take the narrow path through the dense forest",
                        "next_node": "solo_path",
                        "requirements": {"party_size": {"max": 1}}
                        },
                    {
                        "id": "choice_village",
                        "text": "Visit the nearby village to seek companions",
                        "next_node": "village_path",
                        "requirements": {"party_size": {"max": 3}}
                        }
                    ]
                },
            "village_healer": {
                "type": "recruitment",
                "content": {
                    "npc_class": "Healer",
                    "name": "Elena",
                    "description": """You find a skilled healer tending to villagers in a small shrine,
                                   'I've heard rumors of dark forces gathering in the forest,' she says,
                                   'Perhaps our paths align?'""",
                    "requirements": {
                        "min_level": 2,
                        "max_party_size": 3,
                        "class_not_in_party": "Healer",
                        "items_required": "Health Potion"
                        },
                    "consequences": {
                        "accept": {
                            "items_gained": [
                                {"name": "Healing Staff", "quantity": 1},
                                {"name": "Mana Potion", "quantity": 2}
                                ],
                            "items consumed": [
                                {"name": "Health Potion", "quantity": 1}
                                ]
                            },
                        "reject": {
                            "next_node": "forest_entrance",
                            "reputation_change": -5
                            }
                        },
                    "next_node_accept": "village_square",
                    "next_node_reject": "forest_entrance"
                    }
                },
            "solo_path": {
                "type": "combat",
                "content": {
                    "enemies": [("Goblin", 1)],
                    "description": "A goblin jumps out from behind a tree!",
                    "victory_node": "post_solo_combat",
                    "defeat_node": "game over"
                    }
                },
            # more story nodes
            }
