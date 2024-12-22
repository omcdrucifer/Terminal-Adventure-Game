# moved the shared stats to another file after a failed unittest
class GameEntity:
    def __init__(self):
        self.stats = {
                "Strength": 0,
                "Health": 0,
                "Defense": 0,
                "Magic": 0,
                "Agility": 0
                }
        self.level = 1
