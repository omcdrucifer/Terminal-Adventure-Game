# i am going to at least put magic into the bosses for the dragon if nothing else
# still deciding if I want to add anything else to enemy mechanics
class Boss:
    def __init__(self, boss_class, level):
        self.boss_class = boss_class
        self.experience_value = 0
        self.level = level
        self.stats = {
                "Strength": 0,
                "Health": 0,
                "Defense": 0,
                "Magic": 0,
                "Agility": 0
                } # sticking to one template for now, may change later
        self.update_stats()
        self.initialize_class_features()

    @property
    def max_health(self):
        return self.stats["Health"]

    def update_stats(self):
        pass

    def initialize_class_features(self):
        pass

class Dragon(Boss):
    def _init__(self, level):
        super().__init__("Dragon", level)
        self.current_mana = 0
        self.max_mana = 0
        self.spells = []

    def update_stats(self):
        self.stats["Strength"] = 50 + 10 * (self.level - 1)
        self.stats["Health"] = 250 + 10 * (self.level - 1)
        self.stats["Defense"] = 20 + 5 * (self.level - 1)
        self.stats["Magic"] = 10 + 5 * (self.level - 1)
        old_max_mana = self.max_mana
        self.max_mana = 10 + 5 * (self.level - 1)
        if old_max_mana is not None:
            self.current_mana += self.max_mana - old_max_mana
        else:
            self.current_mana = self.max_mana

    @property
    def max_health(self):
        return self.stats["Health"]

    def initialize_class_features(self):
        self.experience_value = 100 + 20 * (self.level - 1)
        self.spells = ["Fire Breath", "Tail Whip", "Claw Swipe", "Roar"] # need to define these
        # will structure these spells like player spells but for now these are reference

class Troll(Boss):
    def __init__(self, level):
        super().__init__("Troll", level)
        self.current_mana = 0
        self.max_mana = 0
        self.spells = []

    def update_stats(self):
        self.stats["Strength"] = 30 + 10 * (self.level - 1)
        self.stats["Health"] = 200 + 30 * (self.level - 1)
        self.stats["Defense"] = 15 + 5 * (self.level - 1)
        self.stats["Magic"] = 10 + 5 * (self.level - 1)
        old_max_mana = self.max_mana
        self.max_mana = 10 + 5 * (self.level - 1)
        if old_max_mana is not None:
            self.current_mana += self.max_mana - old_max_mana
        else:
            self.current_mana = self.max_mana

    @property
    def max_health(self):
        return self.stats["Health"]

    def initialize_class_features(self):
        self.experience_value = 75 + 15 * (self.level - 1)
        self.spells = ["Hammer Fist", "Stomp", "Boulder Throw"]
# may rebalance magic and strength since magic is also governing special attacks
class Giant(Boss):
    def __init__(self, level):
        super().__init__("Giant", level)
        self.current_mana = 0
        self.max_mana = 0
        self.spells = []

    def update_stats(self):
        self.stats["Strength"] = 25 + 12 * (self.level - 1)
        self.stats["Health"] = 100 + 20 * (self.level - 1)
        self.stats["Defense"] = 15 + 4 * (self.level - 1)
        self.stats["Magic"] = 10 + 5 * (self.level - 1)
        old_max_mana = self.max_mana
        self.max_mana = 10 + 5 * (self.level - 1)
        if old_max_mana is not None:
            self.current_mana += self.max_mana - old_max_mana
        else:
            self.current_mana = self.max_mana

    @property
    def max_health(self):
        return self.stats["Health"]

    def initialize_class_features(self):
        self.experience_value = 55 + 10 * (self.level - 1)
        self.spells = ["Club Swing", "Stomp", "Boulder Throw"]
