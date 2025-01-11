# having the classes segregated will give me a chance to flesh out the enemy classes
# i may implement similar magic/inventory system, or some other sort of buff system
class Enemy:
    def __init__(self, enemy_class, level):
        self.enemy_class = enemy_class
        self.experience_value = 0
        self.level = level
        self.stats = {
                "Strength": 0,
                "Health": 0,
                "Defense": 0,
                "Magic": 0,
                "Agility": 0
                } # using the same stats as player/npc for now, may change since they are unique now
        self.update_stats()
        self.initialize_class_features()

    @property
    def max_health(self):
        return self.stats["Health"]

    def update_stats(self):
        pass

    def initialize_class_features(self):
        pass

class Ogre(Enemy):
    def __init__(self, level):
        super().__init__("Ogre", level)

    def update_stats(self):
        self.stats["Strength"] = 12 + 5 * (self.level - 1)
        self.stats["Health"] = 75 + 10 * (self.level - 1)
        self.stats["Defense"] = 12 + 3 * (self.level - 1)

    @property
    def max_health(self):
        return self.stats["Health"]

    def initialize_class_features(self):
        self.experience_value = 30 + 5 * (self.level - 1)

class Goblin(Enemy):
    def __init__(self, level):
        super().__init__("Goblin", level)

    def update_stats(self):
        self.stats["Strength"] = 10 + 3 * (self.level - 1)
        self.stats["Health"] = 50 + 10 * (self.level - 1)
        self.stats["Defense"] = 5 + 1 * (self.level - 1)
        self.stats["Agility"] = 5 + 2 * (self.level - 1)

    @property
    def max_health(self):
        return self.stats["Health"]

    def initialize_class_features(self):
        self.experience_value = 20 + 5 * (self.level - 1)

class Orc(Enemy):
    def __init__(self, level):
        super().__init__("Orc", level)

    def update_stats(self):
        self.stats["Strength"] = 12 + 3 * (self.level - 1)
        self.stats["Health"] = 65 + 15 * (self.level - 1)
        self.stats["Defense"] = 8 + 2 * (self.level - 1)

    @property
    def max_health(self):
        return self.stats["Health"]

    def initialize_class_features(self):
        self.experience_value = 25 + 5 * (self.level - 1)
