from base_classes import GameEntity

class Spell:
    def __init__(self, name, mana_cost, base_damage, scaling_factor=0.5):
        self.name = name
        self.mana_cost = mana_cost
        self.base_damage = base_damage
        self.scaling_factor = scaling_factor

    def can_cast(self, caster):
        return hasattr(caster, 'current_mana') and caster.current_mana >= self.mana_cost

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

class Item:
    def __init__(self, name, effect_type, effect_value, description, use_text):
        self.name = name
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.description = description
        self.use_text = use_text

def initialize_common_items():
    return {
            "Health Potion": Item(
                name="Health Potion",
                effect_type="heal",
                effect_value=50,
                description="Restores 50 HP",
                use_text="drinks the health potion and recovers {value} HP!"
                ),
            "Mana Potion": Item(
                name="Mana Potion",
                effect_type="mana",
                effect_value="30",
                description="Restores 30 MP",
                use_text="drinks the mana potion and recovers {value} MP!"
                ),
            "Strength Elixir": Item(
                name="Strength Elixir",
                effect_type="buff_strength",
                effect_value=10,
                description="Temorarily increases Strength by 10",
                use_text="drinks the strength elixir and feels stronger!"
                )
            }

class Inventory:
    def __init__(self, max_size=20, owner=None):
        self.items = {}
        self.max_size = max_size
        self.owner = owner
        self.initialize_items()

    def initialize_items(self):
        self.add_item("Health Potion", 3)
        if self.owner and hasattr(self.owner, 'player_class') and self.owner.player_class in ["Mage", "Healer"]:
            self.add_item("Mana Potion", 2)

    def add_item(self, item_name, quantity=1):
        current_quantity = self.items.get(item_name, 0)
        new_quantity = current_quantity + quantity

        if len(self.items) >= self.max_size and item_name not in self.items:
            return False, "Inventory is full!"

        self.items[item_name] = new_quantity
        return True, f"Added {quantity} {item_name}(s)"

    def remove_item(self, item_name, quantity=1):
        if item_name not in self.items:
            return False, "Item not in inventory"

        if self.items[item_name] < quantity:
            return False, "Not enough items"

        self.items[item_name] -= quantity
        if self.items[item_name] == 0:
            del self.items[item_name]

        return True, f"Removed {quantity} {item_name}(s)"

    def get_item_count(self, item_name):
        return self.items.get(item_name, 0)

class Player(GameEntity):
    VALID_CLASSES = ["Warrior", "Mage", "Archer"]
    def __init__(self, chosen_class):
        if chosen_class not in self.VALID_CLASSES:
            raise ValueError(f"Invalid class. Must be one of: {', '.join(self.VALID_CLASSES)}")

        super().__init__()
        self.player_class = chosen_class
        self.experience = 0
        self.experience_to_next_level = 100   
#       self.max_level = N  -- if I wanted to impose a level cap
        self.spells = {}
        self.current_mana = 0
        self.max_mana = 0

        self.inventory = Inventory(owner=self)
        self.available_items = initialize_common_items()
        self.active_buffs = {}

        self.update_stats()
        self.initialize_class_features()

    @property
    def max_health(self):
        if self.player_class == "Warrior":
            return 100 + 20 * (self.level - 1)
        if self.player_class == "Mage":
            return 60 + 10 * (self.level - 1)
        if self.player_class == "Archer":
            return 80 + 15 * (self.level - 1)

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

    def use_item(self, item_name, target=None):
        if item_name not in self.available_items:
            return False, "Invalid item"

        if self.inventory.get_item_count(item_name) <= 0:
            return False, "Item not in inventory"

        item = self.available_items[item_name]
        success = False
        message = ""

        if target is None:
            target = self

        if item.effect_type == "heal":
            target.stats["Health"] = min(
                    target.stats["Health"] + item.effect_value,
                    target.max_health
                    )
            success = True
            message = f"{target.player_class} {item.use_text.format(value=item.effect_value)}"

        elif item.effect_type == "mana" and hasattr(target, 'current_mana'):
            target.current_mana = min(
                    target.current_mana + item.effect_value,
                    target.max_mana
                    )
            success = True
            message = f"{target.player_class} {item.use_text.format(value=item.effect_value)}"
        elif item.effect_type.startswith("buff_"):
            stat = item.effect_type.split("_")[1].capitalize()
            if stat in target.stats:
                if stat not in self.active_buffs:
                    self.active_buffs[stat] = []
                self.active_buffs[stat].append(item.effect_value)
                target.stats[stat] += item.effect_value
                success = True
                message = f"{target.player_class} {item.use_text}"

        if success:
            self.inventory.remove_item(item_name)

        return success, message

    def update_buffs(self):
        for stat, buffs in list(self.active_buffs.items()):
            if buffs:
                self.stats[stat] -= buffs.pop(0)
            if not buffs:
                del self.active_buffs[stat]

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
class NPC(GameEntity):
    def __init__(self, npc_class, player_level):
        super().__init__()
        self.npc_class = npc_class
        self.level = player_level
#       self.max_level = N  -- if I wanted to impose a level cap
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

class Enemy(GameEntity):
    def __init__(self, enemy_class, player_level):
        super().__init__()
        self.enemy_class = enemy_class
        if player_level <= 2:
            self.level = 1
        elif player_level == 3:
            self.level = player_level - 1
        else:
            self.level = player_level
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

class Boss(GameEntity):
    def __init__(self, boss_class, player_level, player_party):
        super().__init__()
        self.boss_class = boss_class
        if hasattr(player_party, 'members'):
            player_party_size = len([member for member in player_party.members if hasattr(member, 'player_class') or hasattr(member, 'npc_class')])
        else:
            player_party_size = 0
        self.level = player_level + (player_party_size + 1)
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

