import random
from party import Party
from characters import Player, NPC, Boss, Enemy

class Spell:
    def __init__(self, name, mana_cost, base_damage, scaling_factor=0.5):
        self.name = name
        self.mana_cost = mana_cost
        self.base_damage = base_damage
        self.scaling_factor = scaling_factor

class Combat:
    def __init__(self, player_party, enemy_party):
        if player_party.party_type != "player" or enemy_party.party_type != "enemy":
            raise ValueError("Combat must be between a player party and enemy party")

        self.player_party = player_party
        self.enemy_party = enemy_party
        self.initiative_order = []
        self.current_turn_index = 0
        self.is_player_turn = True
        self.active_player_index = 0
        self.active_enemy_index = 0

        self.spell_lists = {
                "Mage": {
                    "Fireball": Spell("Fireball", mana_cost=20, base_damage=25, scaling_factor=0.6),
                    "Ice Shard": Spell("Ice Shard", mana_cost=15, base_damage=20, scaling_factor=0.4),
                    "Lightning Bolt": Spell("Lightning Bolt", mana_cost=25, base_damage=30, scaling_factor=0.7)
                    },
                "Healer": {
                    "Heal": Spell("Heal", mana_cost=15, base_damage=20, scaling_factor=0.5),
                    "Smite": Spell("Smite", mana_cost=10, base_damage=15, scaling_factor=0.3),
                    "Blessing": Spell("Blessing", mana_cost=20, base_damage=15, scaling_factor=0.4)
                    }
                }

        self.setup_initiative()

    def setup_initiative(self):
        all_combatants = []

        for member in self.player_party.members + self.enemy_party.members:
            base_initiative = random.randint(1, 20)
            agility_bonus = member.stats.get("Agility", 0) * 0.5
            member.initiative = base_initiative + agility_bonus
            all_combatants.append(member)

        self.initiative_order = sorted(
                all_combatants,
                key=lambda x: x.initiative,
                reverse=True
                )

    def get_next_active_player(self):
        active_members = self.player_party.get_active_members()
        if not active_members:
            return False
        current_member = self.player_party.members[self.active_player_index]
        while current_member.stats["Health"] <= 0:
            self.active_player_index = (self.active_player_index + 1) % len(self.player_party.members)
            current_member = self.player_party.members[self.active_player_index]
        return True

    def get_next_active_enemy(self):
        active_members = self.enemy_party.get_active_members()
        if not active_members:
            return False
        current_member = self.enemy_party.members[self.active_enemy_index]
        while current_member.stats["Health"] <= 0:
            self.active_enemy_index = (self.active_enemy_index + 1) % len(self.enemy_party.members)
            current_member = self.enemy_party.members[self.active_enemy_index]
        return True

    def get_available_spells(self, combatant):
        if hasattr(combatant, 'player_class') and combatant.player_class in self.spell_lists:
            return self.spell_lists[combatant.player_class]
        return {}
    
    def can_cast_spell(self, caster, spell):
        return hasattr(caster, 'current_mana') and caster.current_mana >= spell.mana_cost

    def cast_spell(self, caster, spell_name, target):
        available_spells = self.get_available_spells(caster)
        if spell_name not in available_spells:
            return "Invalid Spell"
        spell = available_spells[spell_name]
        if not self.can_cast_spell(caster, spell):
            return "Not enough mana"
        magic_bonus = caster.stats.get("Magic", 0) * spell.scaling_factor
        base_effect = random.randint(spell.base_damage - 5, spell.base_damage + 5)
        total_effect = int(base_effect + magic_bonus)

        caster.current_mana -= spell.mana_cost

        if spell_name in ["Heal", "Blessing"]:
            target.stats["Health"] += total_effect
            return f"Spell heal {total_effect}"
        else:
            if "Magic" in target.stats:
                magic_resist = target.stats["Magic"] * 0.2
                total_effect = max(0, int(total_effect - magic_resist))

            target.stats["Health"] -= total_effect

            if target.stats["Health"] <= 0:
                target.stats["Health"] = 0
                if isinstance(target, (Enemy, Boss)) and hasattr(caster, "player_class"):
                    self.handle_experience(caster, target)
                return f"DEFEAT {self.get_combatant_type(target)}"
            return f"Spell hit {total_effect}"

    def handle_initiative(self):
        if self.is_player_turn:
            if not self.get_next_active_player():
                self.is_player_turn = False
                self.active_enemy_index = 0
                self.get_next_active_enemy()
        else:
            if not self.get_next_active_enemy():
                self.is_player_turn = True
                self.active_player_index = 0
                self.get_next_active_player()

    def attack(self, target_index=None):
        if self.is_player_turn:
            attacker = self.player_party.members[self.active_player_index]
            if target_index is None:
                target_index - self.active_enemy_index
            defender = self.enemy_party.members[target_index]
        else:
            attacker = self.enemy_party.members[self.active_enemy_index]
            active_members = self.player_party.get_active_members()
            if active_members:
                defender = random.choice(active_members)
            else:
                return "DEFEAT"

        hit_chance = 75
        if random.randint(1, 100) <= hit_chance:
            if isinstance(attacker, Boss):
                damage = random.randint(5, attacker.stats["Strength"] // 2)
            else:
                damage = random.randint(5, attacker.stats["Strength"])
            defense = random.randint(0, defender.stats["Defense"])
            actual_damage = max(0, damage - defense)
            defender.stats["Health"] -= actual_damage

            if defender.stats["Health"] <= 0:
                defender.stats["Health"] = 0
                if isinstance(defender, (Enemy, Boss)) and isinstance(attacker, Player):
                    self.handle_experience(attacker, defender)
                    if not self.get_next_active_enemy():
                        return "VICTORY"
                else:
                    if not self.get_next_active_player:
                        return "DEFEAT"
                return f"DEFEAT {self.get_combatant_type(defender)}"
            return f"Hit! {actual_damage}"
        else:
            return "Miss!"

    def handle_experience(self, attacker, defeated_enemy):
        initial_level = attacker.level
        attacker.gain_experience(defeated_enemy.experience_value)
        if attacker.level > initial_level:
            self.player_party.synchronize_level(attacker.level)

    def get_active_combatant(self):
        if self.is_player_turn:
            return self.player_party.members[self.active_player_index]
        return self.enemy_party.members[self.active_enemy_index]

    def get_combat_status(self):
        return (
                self.player_party.get_party_status(),
                self.enemy_party.get_party_status()
                )

    def get_combatant_type(self, combatant):
        for attr in ['player_class', 'npc_class', 'enemy_class', 'boss_class']:
            if hasattr(combatant, attr):
                return getattr(combatant, attr)
        return 'Unknown'

    def handle_combat_action(self, combatant, action_type, target_index=None, spell_name=None):
        if action_type == "attack":
            return self.attack(target_index)
        elif action_type == "cast_spell":
            target = self.enemy_party.members[target_index]
            return self.cast_spell(combatant, spell_name, target)
        return "Invalid action"
