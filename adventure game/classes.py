class Player:
    def __init__(self):
        self.player_class = input("Choose a class (Warrior, Mage, Archer)").strip().title()
        self.level = 1
        self.stats = {
                "Strength": 0,
                "Health": 0,
                "Defense": 0,
                "Magic": 0,
                "Agility": 0
                }
        self.update_stats()

    def update_stats(self):
        if self.player_class == "Warrior":
            self.stats["Strength"] = 20 + 5 * (self.level - 1)
            self.stats["Health"] = 100 + 20 * (self.level - 1)
            self.stats["Defense"] = 15 + 3 * (self.level - 1)
        elif self.player_class == "Mage":
            self.stats["Strength"] = 10 + 2 * (self.level - 1)
            self.stats["Health"] = 60 + 10 * (self.level - 1)
            self.stats["Defense"] = 5 + 1 * (self.level - 1)
            self.stats["Magic"] = 30 + 5 * (self.level - 1)
        elif self.player_class == "Archer":
            self.stats["Strength"] = 15 + 3 * (self.level - 1)
            self.stats["Health"] = 80 + 15 * (self.level - 1)
            self.stats["Defense"] = 10 + 2 * (self.level - 1)
            self.stats["Agility"] = 25 + 5 * (self.level - 1)

    def level_up(self):
        self.level += 1
        self.update_stats()

class Enemy:
    def __init__(self, enemy_class):
        self.enemy_class = enemy_class
        self.level = 1
        self.stats = {
                "Strength": 0,
                "Health": 0,
                "Defense": 0,
                "Magic": 0,
                "Agility": 0
                }
        self.update_stats()
# still need to adjust enemy class stats. This is just copy/paste of player with enemy names in place
    def update_stats(self):
        if self.enemy_class == "Ogre":
            self.stats["Strength"] = 12 + 5 * (self.level - 1)
            self.stats["Health"] = 80 + 20 * (self.level - 1)
            self.stats["Defense"] = 15 + 3 * (self.level - 1)
        elif self.enemy_class == "Goblin":
            self.stats["Strength"] = 8 + 2 * (self.level - 1)
            self.stats["Health"] = 60 + 10 * (self.level - 1)
            self.stats["Defense"] = 5 + 1 * (self.level - 1)
        elif self.enemy_class == "Orc":
            self.stats["Strength"] = 15 + 3 * (self.level - 1)
            self.stats["Health"] = 80 + 15 * (self.level - 1)
            self.stats["Defense"] = 10 + 2 * (self.level - 1)

    def level_up(self):
        self.level += 1
        self.update_stats()
