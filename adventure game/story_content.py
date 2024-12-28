# still just trying to get something in place, not reflective of final story 
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
