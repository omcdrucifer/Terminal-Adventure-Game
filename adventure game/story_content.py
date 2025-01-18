def get_story_content():
    return {
            "start": {
                "type": "narrative",
                "content": {"text": "You are in a town.", "description": "You see a few NPCs around."},
                "choices": [
                    {"id": "1", "text": "Talk to the merchant", "next_node": "merchant"},
                    {"id": "2", "text": "Explore the town", "next_node": "explore"}
                    ]
                },
            "merchant": {
                "type": "dialog",
                "content": {"text": "Merchant: Hello, traveler! Would you like to buy something?", "description": ""},
                "choices": [
                    {"id": "1", "text": "Buy item", "next_node": "buy_item"},
                    {"id": "2", "text": "Leave", "next_node": "start"}
                    ]
                },
            "explore": {
                "type": "narrative",
                "content": {"text": "You explore the town and find a hidden item.", "description": ""},
                "choices": [
                    {"id": "1", "text": "Return to town center", "next_node": "start"}
                    ]
                },
            "buy_item": {
                "type": "narrative",
                "content": {"text": "You bought an item.", "description": ""},
                "choices": [
                    {"id": "1", "text": "Return to town center", "next_node": "start"}
                    ]
                },
            "goblin_encounter": {
                "type": "combat",
                "content": {
                    "enemy": "Goblin",
                    "level": 1,
                    "victory_node": "post_goblin_victory",
                    "defeat_node": "game_over",
                    "experience_reward": 50
                    }
                },
            # more story nodes
            }
