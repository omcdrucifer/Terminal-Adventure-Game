# i am going to at least put magic into the bosses for the dragon if nothing else
# still deciding if I want to add anything else to enemy mechanics
class Spell:
    def __init__(self, name, mana_cost, base_damage, scaling_factor=0.5):
        self.name = name
        self.mana_cost = mana_cost
        self.base_damage = base_damage
        self.scaling_factor = scaling_factor

    def can_cast(self, caster):
        return caster.current_mana >= self.mana_cost

def initialize_dragon_spells():
    return {
            "Fire Breath": Spell(
                name="Fire Breath",
                mana_cost=30,
                base_damage=25,
                scaling_factor=0.7
                ),
            "Tail Whip": Spell(
                name="Tail Whip",
                mana_cost=15,
                base_damage=20,
                scaling_factor=0.4
                ),
            "Claw Swipe": Spell(
                name="Claw Swipe",
                mana_cost=10,
                base_damage=15,
                scaling_factor=0.5
                ),
            "Roar": Spell(
                name="Roar",
                mana_cost=20,
                base_damage=15,
                scaling_factor=0.6
                )
            }

def initialize_troll_spells():
    return {
            "Hammer Fist": Spell(
                name="Hammer Fist",
                mana_cost=30,
                base_damage=25,
                scaling_factor=0.6
                ),
            "Stomp": Spell(
                name="Stomp",
                mana_cost=10,
                base_damage=15,
                scaling_factor=0.5
                ),
            "Boulder Throw": Spell(
                name="Boulder Throw",
                mana_cost=20,
                base_damage=20,
                scaling_factor=0.4
                )
            }

def initialize_giant_spells():
    return {
            "Club Swing": Spell(
                name="Club Swing",
                mana_cost=30,
                base_damage=25,
                scaling_factor=0.6
                ),
            "Stomp": Spell(
                name="Stomp",
                mana_cost=10,
                base_damage=15,
                scaling_factor=0.5
                ),
            "Boulder Throw": Spell(
                name="Boulder Throw",
                mana_cost=20,
                base_damage=20,
                scaling_factor=0.4
                )
            }

class Item:
    def __init__(self, name, effect_type, effect_value, description, use_text, duration=None):
        self.name = name
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.description = description
        self.use_text = use_text
        self.duration = duration

def initialize_common_items():
    return {
            "Mana Potion": Item(
                name="Mana Potion",
                effect_type="mana",
                effect_value=20,
                description="Restores 30 mana points",
                use_text="You drink the potion and feel restored"
                )
            }

class Inventory:
    def __init__(self, owner, max_size=20):
        self.items = {}
        self.owner = owner
        self.max_size = max_size
        self.initialize_items()

    def initialize_items(self):
        self.add_item("Mana Potion", 3)

    def add_item(self, item_name, quantity=1):
        current_quantity = self.items.get(item_name, 0)
        new_quantity = current_quantity + quantity

        if len(self.items) >= self.max_size and item_name not in self.items:
            return False, "Inventory is full!"

        self.items[item_name] = new_quantity
        return True, f"{quantity} {item_name} added to inventory"

    def remove_item(self, item_name, quantity=1):
        if item_name not in self.items:
            return False, "Item not in inventory"

        if self.items[item_name] < quantity:
            return False, "Not enough items"

        self.items[item_name] -= quantity
        if self.items[item_name] == 0:
            del self.items[item_name]

        return True, f"{quantity} {item_name} removed from inventory"

    def get_item_count(self, item_name):
        return self.items.get(item_name, 0)

class Boss:
    def __init__(self, boss_class, level):
        self.boss_class = boss_class
        self.enemy_class = boss_class
        self.experience_value = 0
        self.level = level
        self.stats = {
                "Strength": 0,
                "Health": 0,
                "Defense": 0,
                "Magic": 0,
                "Agility": 0
                } # sticking to one template for now, may change later
        self.current_mana = 0
        self.max_mana = 0
        self.inventory = Inventory(owner=self)
        self.available_items = initialize_common_items()
        self.spells = {}

        self.update_stats()
        self.initialize_class_features()

    @property
    def max_health(self):
        raise NotImplementedError("Subclasses must implement max_health")

    def update_stats(self):
        pass

    def initialize_class_features(self):
        pass

class Dragon(Boss):
    def __init__(self, level):
        super().__init__("Dragon", level)
        self.current_mana = 0
        self.max_mana = 0
        self.spells = initialize_dragon_spells()

    def update_stats(self):
        self.stats["Strength"] = 30 + 10 * (self.level - 1)
        self.stats["Health"] = 200 + 10 * (self.level - 1)
        self.stats["Defense"] = 20 + 5 * (self.level - 1)
        self.stats["Magic"] = 20 + 5 * (self.level - 1)
        old_max_mana = self.max_mana
        self.max_mana = 20 + 5 * (self.level - 1)
        if old_max_mana is not None:
            self.current_mana += self.max_mana - old_max_mana
        else:
            self.current_mana = self.max_mana

    @property
    def max_health(self):
        return 200 + 10 * (self.level - 1)

    def initialize_class_features(self):
        self.experience_value = 100 + 20 * (self.level - 1)

class Troll(Boss):
    def __init__(self, level):
        super().__init__("Troll", level)
        self.current_mana = 0
        self.max_mana = 0
        self.spells = initialize_troll_spells()

    def update_stats(self):
        self.stats["Strength"] = 25 + 10 * (self.level - 1)
        self.stats["Health"] = 150 + 30 * (self.level - 1)
        self.stats["Defense"] = 15 + 5 * (self.level - 1)
        self.stats["Magic"] = 20 + 5 * (self.level - 1)
        old_max_mana = self.max_mana
        self.max_mana = 20 + 5 * (self.level - 1)
        if old_max_mana is not None:
            self.current_mana += self.max_mana - old_max_mana
        else:
            self.current_mana = self.max_mana

    @property
    def max_health(self):
        return 150 + 30 * (self.level - 1)

    def initialize_class_features(self):
        self.experience_value = 75 + 15 * (self.level - 1)

class Giant(Boss):
    def __init__(self, level):
        super().__init__("Giant", level)
        self.current_mana = 0
        self.max_mana = 0
        self.spells = initialize_giant_spells()

    def update_stats(self):
        self.stats["Strength"] = 20 + 12 * (self.level - 1)
        self.stats["Health"] = 100 + 20 * (self.level - 1)
        self.stats["Defense"] = 15 + 4 * (self.level - 1)
        self.stats["Magic"] = 20 + 5 * (self.level - 1)
        old_max_mana = self.max_mana
        self.max_mana = 20 + 5 * (self.level - 1)
        if old_max_mana is not None:
            self.current_mana += self.max_mana - old_max_mana
        else:
            self.current_mana = self.max_mana

    @property
    def max_health(self):
        return 100 + 20 * (self.level - 1)

    def initialize_class_features(self):
        self.experience_value = 55 + 10 * (self.level - 1)
