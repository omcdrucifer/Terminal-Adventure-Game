class Spell:
    def __init__(self, name, mana_cost, base_damage, scaling_factor=0.5):
        self.name = name
        self.mana_cost = mana_cost
        self.base_damage = base_damage
        self.scaling_factor = scaling_factor

    def can_cast(self, caster):
        return caster.current_mana >= self.mana_cost
# as I expand the spell library to support character leveling, this will likely be moved to a separate file and imported
def initialize_healer_spells():
    return {
            "Heal": Spell(
                name="Heal",
                mana_cost=15,
                base_damage=20,
                scaling_factor=0.4
                ),
            "Smite": Spell(
                name="Smite",
                mana_cost=10,
                base_damage=15,
                scaling_factor=0.3
                ),
            "Blessing": Spell(
                name="Blessing",
                mana_cost=20,
                base_damage=15,
                scaling_factor=0.4
                )
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
                description="Restores 50 health points",
                use_text="You drink the potion and feel refreshed"
                ),
            "Mana Potion": Item(
                name="Mana Potion",
                effect_type="mana",
                effect_value=30,
                description="Restores 30 mana points",
                use_text="You drink the potion and feel restored"
                ),
            "Strength Elixir": Item(
                name="Strength Elixir",
                effect_type="buff_strength",
                effect_value=10,
                description="Temporarily increases strength by 10",
                use_text="You drink the elixir and feel stronger!"
                ),
            "Agility Elixir": Item(
                name="Agility Elixir",
                effect_type="buff_agility",
                effect_value=10,
                description="Temporarily increases agility by 10",
                use_text="You drink the elixir and feel faster!"
                )
            }

class Inventory:
    def __init__(self, owner, max_size=20):
        self.items = {}
        self.owner = owner
        self.max_size = max_size
        self.initialize_items()

    def initialize_items(self):
        self.add_item("Health Potion", 3)
        if self.owner.npc_class == "Healer":
            self.add_item("Mana Potion", 2)
        if self.owner.npc_class == "Fighter":
            self.add_item("Strength Elixir", 1)
        if self.owner.npc_class == "Rogue":
            self.add_item("Agility Elixir", 1)

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

class NPC:
    def __init__(self, name, npc_class, npc_level=1):
        self.name = name
        self.stats = {
                "Strength": 0,
                "Health": 0,
                "Defense": 0,
                "Magic": 0,
                "Agility": 0
                }
        self.level = npc_level
        self.experience = 0
        self.experience_to_next_level = 100
        self.npc_class = npc_class
        self.inventory = Inventory(owner=self)
        self.available_items = initialize_common_items()
        self.active_buffs = {}
        self.max_health = 0
        self.current_mana = 0
        self.max_mana = 0

        self.update_stats()
        self.initialize_class_features()

    def update_stats(self):
        pass

    def initialize_class_features(self):
        pass

    def use_item(self, item_name, target=None):
        if item_name not in self.available_items:
            return False, "Invalid item"

        if self.inventory.get_item_count(item_name) < 0:
            return False, "Item not in inventory"

        item = self.available_items[item_name]
        success = False
        message = ""

        if target is None:
            target = self

        if item.effect_type == "heal":
            if hasattr(target, "max_health") and target.max_health is not None:
                max_hp = target.max_health
                if isinstance(max_hp, (int, float)):
                    target.stats["Health"] = min(
                            target.stats["Health"] + item.effect_value,
                            int(max_hp)
                            )
                else:
                    target.stats["Health"] += item.effect_value
            else:
                target.stats["Health"] += item.effect_value
            success = True
            message = f"{target.name} was healed for {item.effect_value} health points"
        elif item.effect_type == "mana" and hasattr(target, 'current_mana'):
            target.current_mana = min(
                    target.current_mana + item.effect_value,
                    target.max_mana
                    )
            success = True
            message = f"{target.name} restored {item.effect_value} mana points"
        elif item.effect_type.startswith("buff_"):
            stat = item.effect_type.split("_")[1].capitalize()
            if stat in target.stats:
                if stat not in self.active_buffs:
                    self.active_buffs[stat] = []
                self.active_buffs[stat].append(item.effect_value)
                target.stats[stat] += item.effect_value
                success = True
                message = f"{target.name} gained {item.effect_value} {stat}"

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
        self.experience += xp
        if self.experience >= self.experience_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        self.update_stats()
        print(f"{self.name} leveled up to {self.level}!")

class Fighter(NPC):
    def __init__(self, name):
        self.name = name
        super().__init__(name, npc_class="Fighter")

    def update_stats(self):
        self.stats["Strength"] = 20 + 5 * (self.level - 1)
        self.stats["Health"] = 100 + 20 * (self.level - 1)
        self.stats["Defense"] = 15 + 3 * (self.level - 1)
        self.stats["Agility"] = 5 + 5 * (self.level - 1)

    @property
    def max_health(self):
        return 100 + 20 * (self.level - 1)
    
    def initialize_class_features(self):
        self.available_items["Strength Elixir"] = Item(
                name="Strength Elixir",
                effect_type="buff_strength",
                effect_value=10,
                description="Temporarily increases strength by 10",
                use_text="You drink the elixir and feel stronger!"
                )

class Healer(NPC):
    def __init__(self, name):
        self.name = name
        super().__init__(name, npc_class="Healer")
        self.current_mana = 0 
        self.max_mana = 0
        self.spells = initialize_healer_spells()

    def update_stats(self):
        self.stats["Strength"] = 10 + 2 * (self.level - 1)
        self.stats["Health"] = 60 + 10 * (self.level - 1)
        self.stats["Defense"] = 5 + 1 * (self.level - 1)
        self.stats["Magic"] = 30 + 5 * (self.level - 1)
        old_max_mana = self.max_mana
        self.max_mana = 30 + 5 * (self.level - 1)
        if old_max_mana is not None:
            self.current_mana += self.max_mana - old_max_mana
        else:
            self.current_mana = self.max_mana

    def initialize_class_features(self):
        self.available_items["Mana Potion"] = Item(
                name="Mana Potion",
                effect_type="mana",
                effect_value=30,
                description="Restores 30 mana points",
                use_text="You drink the potion and feel restored"
                )

    @property
    def max_health(self):
        return 60 + 10 * (self.level - 1)

class Rogue(NPC):
    def __init__(self, name):
        self.name = name
        super().__init__(name, npc_class="Rogue")

    def update_stats(self):
        self.stats["Strength"] = 15 + 3 * (self.level - 1)
        self.stats["Health"] = 80 + 15 * (self.level - 1)
        self.stats["Defense"] = 10 + 2 * (self.level - 1)
        self.stats["Agility"] = 25 + 5 * (self.level - 1)

    @property
    def max_health(self):
        return 80 + 15 * (self.level - 1)

    def initialize_class_features(self):
        self.available_items["Agility Elixir"] = Item(
                name="Agility Elixir",
                effect_type="buff_agility",
                effect_value=10,
                description="Temporarily increases agility by 10",
                use_text="You drink the elixir and feel faster!"
                )
