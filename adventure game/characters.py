from party import Party

class Spell:
    def __init__(self, name, mana_cost, base_damage, scaling_factor=0.5):
        self.name = name
        self.mana_cost = mana_cost
        self.base_damage = base_damage
        self.scaling_factor = scaling_factor

    def initialize_mage_spells():
        return {
                "Fireball": Spell("Fireball", mana_cost=20, base_damage=25, scaling_factor=0.6),
                "Ice Shard": Spell("Ice Shard", mana_cost=15, base_damage=20, scaling_factor=0.4),
                "Lightning Bolt": Spell("Lightning Bolt", mana_cost=25, base_damage=30, scaling_factor=0.7)
                }
    def initialize_healer_spells():
        return {
                "Heal": Spell("Heal", mana_cost=15, base_damage=20, scaling_factor=0.5),
                "Smite": Spell("Smite", mana_cost=10, base_damage=15, scaling_factor=0.3),
                "Blessing": Spell("Blessing", mana_cost=20, base_damage=15, scaling_factor=0.4)
                }

class Player:
    def __init__(self):
        self.player_class = input("Choose a class (Warrior, Mage, Archer)").strip().title()
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100   
#       self.max_level = N  -- if I wanted to impose a level cap
        self.stats = {
                "Strength": 0,
                "Health": 0,
                "Defense": 0,
                "Magic": 0,
                "Agility": 0
                }
        self.spells = {}
        self.current_mana = 0
        self.max_mana = 0
        self.update_stats()
        self.initialize_class_features()

    def initialize_class_features(self):
        if self.player_class in ["Mage", "Healer"]:
            if self.player_class == "Mage":
                self.spells = initialize_mage_spells()
            else:
                self.spells = initialize_healer_spells()

            self.max_mana = self.stats["Magic"] * 5 + (self.level * 10)
            self.current_mana = self.max_mana

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

        if self.player_class in ["Mage", "Healer"]:
            old_max_mana = self.max_mana
            self.max_mana = self.stats["Magic"] * 5 + (self.max_mana * 10)
            if old_max_mana > 0:
                self.current_mana = int((self.current_mana / old_max_mana) * self.max_mana)
            else:
                self.current_mana = self.max_mana

    def gain_experience(self, xp):
#       if self.level == self.max_level:
#           break    -- handles the edge case if I were to impose a level cap
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
class NPC:
    def __init__(self, npc_class, player_level):
        self.npc_class = npc_class
        self.level = player_level
#       self.max_level = N  -- if I wanted to impose a level cap
        self.stats = {
                "Strength": 0,
                "Health": 0,
                "Defense": 0,
                "Magic": 0,
                "Agility": 0
                }
        self.spells = {}
        self.current_mana = 0
        self.max_mana = 0
        self.update_stats()
        self.initialize_class_features()

    def initialize_class_features(self):
        if self.npc_class in ["Mage", "Healer"]:
            if self.npc_class == "Mage":
                self.spells = initialize_mage_spells()
            else:
                self.spells = initialize_healer_spells()

            self.max_mana = self.stats["Magic"] * 5 + (self.level * 10)
            self.current_mana = self.max_mana

    def update_stats(self):
        if self.npc_class == "Fighter":
            self.stats["Strength"] = 20 + 5 * (self.level - 1)
            self.stats["Health"] = 100 + 20 * (self.level - 1)
            self.stats["Defense"] = 15 + 3 * (self.level - 1)
        elif self.npc_class == "Healer":
            self.stats["Strength"] = 10 + 2 * (self.level - 1)
            self.stats["Health"] = 60 + 10 * (self.level - 1)
            self.stats["Defense"] = 5 + 1 * (self.level - 1)
            self.stats["Magic"] = 30 + 5 * (self.level - 1)
        elif self.npc_class == "Rogue":
            self.stats["Strength"] = 15 + 3 * (self.level - 1)
            self.stats["Health"] = 80 + 15 * (self.level - 1)
            self.stats["Defense"] = 10 + 2 * (self.level - 1)
            self.stats["Agility"] = 25 + 5 * (self.level - 1)

        if self.npc_class in ["Mage", "Healer"]:
            old_max_mana = self.max_mana
            self.max_mana = self.stats["Magic"] * 5 + (self.max_mana * 10)
            if old_max_mana > 0:
                self.current_mana = int((self.current_mana / old_max_mana) * self.max_mana)
            else:
                self.current_mana = self.max_mana

    def synchronize_level(self, npc_level):
        self.level = npc_level
        self.update_stats()

class Enemy:
    def __init__(self, enemy_class, player_level):
        self.enemy_class = enemy_class
        if player_level <= 2:
            self.level = 1
        elif player_level == 3:
            self.level = player_level - 1
        else:
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
            self.stats["Health"] = 75 + 10 * (self.level - 1)
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

class Boss:
    def __init__(self, boss_class, player_level, player_party):
        self.boss_class = boss_class
        player_party_size = len([member for member in player_party.members if isinstance(member, (Player, NPC))])
        self.level = player_level + (player_party_size + 1)
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
        if self.boss_class == "Dragon":
            self.stats["Strength"] = 50 + 10 * (self.level - 1)
            self.stats["Health"] = 300 + 50 * (self.level - 1)
            self.stats["Defense"] = 20 + 5 * (self.level - 1)
            self.experience_value = 100 + 20 * (self.level - 1)
        elif self.boss_class == "Troll":
            self.stats["Strength"] = 30 + 10 * (self.level - 1)
            self.stats["Health"] = 200 + 30 * (self.level - 1)
            self.stats["Defense"] = 15 + 5 * (self.level - 1)
            self.experience_value = 75 + 15 * (self.level - 1)
        elif self.boss_class == "Giant":
            self.stats["Strength"] = 25 + 12 * (self.level - 1)
            self.stats["Health"] = 100 + 20 * (self.level - 1)
            self.stats["Defense"] = 15 + 4 * (self.level - 1)
            self.experience_value = 55 + 10 * (self.level - 1)


