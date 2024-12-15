import random

class Player:
    def __init__(self):
        self.player_class = input("Choose a class (Warrior, Mage, Archer)").strip().title()
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
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

    def gain_experience(self, xp):
        self.experience += xp
        if self.experience >= self.experience_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        self.update_stats()
        print(f"{self.player_class} leveled up to {self.level}!")
# once I start piecing everything together, I'd like this to print the player name rather than class
class Enemy:
    def __init__(self, enemy_class, player_level):
        self.enemy_class = enemy_class
        self.level = player_level
        self.stats = {
                "Strength": 0,
                "Health": 0,
                "Defense": 0,
                "Magic": 0,
                "Agility": 0
                }
        self.experience_value = 0
        self.update_stats()

    def update_stats(self):
        if self.enemy_class == "Ogre":
            self.stats["Strength"] = 12 + 5 * (self.level - 1)
            self.stats["Health"] = 80 + 10 * (self.level - 1)
            self.stats["Defense"] = 12 + 3 * (self.level - 1)
            self.experience_value = 30 + 5 * (self.level - 1)
        elif self.enemy_class == "Goblin":
            self.stats["Strength"] = 10 + 3 * (self.level - 1)
            self.stats["Health"] = 50 + 10 * (self.level - 1)
            self.stats["Defense"] = 5 + 1 * (self.level - 1)
            self.experience_value = 20 + 5 * (self.level - 1)
        elif self.enemy_class == "Orc":
            self.stats["Strength"] = 12 + 3 * (self.level - 1)
            self.stats["Health"] = 65 + 15 * (self.level - 1)
            self.stats["Defense"] = 8 + 2 * (self.level - 1)
            self.experience_value = 25 + 5 * (self.level - 1)

    def level_up(self):
        self.level += 1
        self.update_stats()

class Combat:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
# values for combat system are placeholders, will be refined as system is fleshed out
    def attack(self, attacker, defender):
        hit_chance = 75
        if random.randint(1, 100) <= hit_chance:
            damage = random.randint(5, 15)
            defense = random.randint(0, defender.stats["Defense"])
            actual_damage = max(0, damage - defense)
            defender.stats["Health"] -= actual_damage
            if hasattr(attacker, 'player_class'):
                attacker_type = attacker.player_class
            elif hasattr(attacker, 'enemy_class'):
                attacker_type = attacker.enemy_class
            else:
                attacker_type = 'Unknown'
            if hasattr(defender, 'player_class'):
                defender_type = defender.player_class
            elif hasattr(defender, 'enemy_class'):
                defender_type = defender.enemy_class
            else:
                defender_type = 'Unknown'
            if defender.stats["Health"] <= 0:
                if isinstance(defender, Enemy):
                    self.player.gain_experience(defender.experience_value)
                return f"{attacker_type} defeats {defender_type}!"
            else:
                return f"Hit! {attacker_type} deals {actual_damage} damage to {defender_type}."
        else:
            return "Miss!"

# combat example
player = Player()
enemy = Enemy("Goblin", player.level)
combat = Combat(player, enemy)
result = combat.attack(player, enemy)
print(result)
