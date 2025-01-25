# I think I got over ambitious with the combat system and forgot I was making
# a text based terminal game, so I am experimenting with a simpler combat system
import random
from player_classes import initialize_mage_spells, Player
from npc_classes import initialize_healer_spells
from boss_classes import initialize_dragon_spells, initialize_troll_spells, initialize_giant_spells

class Combat:
    def __init__(self, player_party, enemy_party):
        self.player_party = player_party
        self.enemy_party = enemy_party
        self.is_player_turn = True
        self.active_player_index = 0
        self.active_enemy_index = 0
        self.fled = False
        self.spells = {
                "Mage": initialize_mage_spells(),
                "Healer": initialize_healer_spells(),
                "Dragon": initialize_dragon_spells(),
                "Troll": initialize_troll_spells(),
                "Giant": initialize_giant_spells()
                }

    def get_next_active_player(self):
        active_members = self.player_party.get_active_members()
        if not active_members:
            return None
        current_member = self.player_party.members[self.active_player_index]
        while current_member.stats["Health"] <= 0:
            self.active_player_index = (self.active_player_index + 1) % len(self.player_party.members)
            current_member = self.player_party.members[self.active_player_index]
        return current_member

    def get_next_active_enemy(self):
        active_members = self.enemy_party.get_active_members()
        if not active_members:
            return None
        return random.choice(active_members)

    def should_use_mana_potion(self, boss):
        if boss.inventory.get_item_count("Mana Potion") == 0:
            return False

        best_spell = None
        best_damage = 0
        for _, spell in boss.spells.items():
            potential_damage = spell.base_damage + (boss.stats["Magic"] * spell.scaling_factor)
            if potential_damage > best_damage:
                best_damage = potential_damage
                best_spell = spell

        if not best_spell:
            return False

        if boss.boss_class == "Dragon":
            return boss.current_mana < best_spell.mana_cost and boss.current_mana < boss.max_mana * 0.4
        elif boss.boss_class == "Troll":
            return boss.current_mana < best_spell.mana_cost and boss.current_mana < boss.max_mana * 0.25
        elif boss.boss_class == "Giant":
            return boss.current_mana < best_spell.mana_cost and boss.current_mana < boss.max_mana * 0.3

        return False

    def choose_boss_action(self, boss):
        if not hasattr(boss, 'boss_class'):
            return "attack", None

        if self.should_use_mana_potion(boss):
            return "use_item", "Mana Potion"

        available_spells = []
        for spell_name, spell in boss.spells.items():
            if spell.can_cast(boss):
                damage = spell.base_damage + (boss.stats["Magic"] * spell.scaling_factor)
                weight = int(damage / 5)
                available_spells.extend([(spell_name, spell)] * weight)

        if available_spells:
            if boss.boss_class == "Dragon":
                if boss.stats["Health"] > boss.max_health * 0.7:
                    spell_name, _ = random.choice(available_spells)
                    return "cast_spell", spell_name
            elif boss.boss_class == "Troll":
                if boss.stats["Health"] < boss.max_health * 0.6:
                    spell_name, _ = random.choice(available_spells)
                    return "cast_spell", spell_name
            elif boss.boss_class == "Giant":
                if random.random() < 0.6:
                    spell_name, _ = random.choice(available_spells)
                    return "cast_spell", spell_name

        return "attack", None

    def use_item(self, user, item_name):
        if hasattr(user, 'use_item'):
            return user.use_item(item_name)

        if not hasattr(user, 'inventory') or not hasattr(user, 'current_mana'):
            return "INVALID_ITEM", False

        if item_name not in user.inventory.items:
            return "NO_ITEM", False 

        item = user.inventory.items[item_name]
        if item.effect_type == "mana":
            old_mana = user.current_mana
            user.current_mana = min(user.max_mana, user.current_mana + item.effect_value)
            mana_restored = user.current_mana - old_mana
            success = user.inventory.remove_item(item_name)
            if success:
                return f"MANA_RESTORED_{mana_restored}", True

        return "INVALID_ITEM", False

    def cast_spell(self, caster, spell_name, target):
        spell = caster.spells[spell_name]
        if not spell:
            return "NOT_ENOUGH_MANA", False

        damage = spell.base_damage + (caster.stats["Magic"] * spell.scaling_factor)
        caster.current_mana -= spell.mana_cost

        target.stats["Health"] -= damage
        if target.stats["Health"] < 0:
            target.stats["Health"] = 0
            if hasattr(caster, 'player_class'):
                caster.gain_experience(target.experience_value)
            return "DEFEAT" if isinstance(target, Player) else "VICTORY", True

        return f"DAMAGE_{int(damage)}", True
    
    def attack(self, target_index=None):
        if self.is_player_turn:
            attacker = self.get_next_active_player()
            if target_index is None or not (0 <= target_index < len(self.enemy_party.members)):
                return "INVALID_TARGET", False
            defender = self.enemy_party.members[target_index]
        else:
            attacker = self.get_next_active_enemy()
            defender = random.choice(self.player_party.get_active_members())

        if not attacker or not defender:
            return "INVALID_COMBATANT", False

        damage = max(1, attacker.stats["Strength"] - (defender.stats["Defense"] // 2))
        defender.stats["Health"] -= damage

        if defender.stats["Health"] < 0:
            defender.stats["Health"] = 0
            if hasattr(attacker, 'player_class'):
                attacker.gain_experience(defender.experience_value)
            return "DEFEAT" if isinstance(defender, Player) else "VICTORY", True
        return f"DAMAGE_{damage}", True

    def handle_combat_turn(self, action_type, target_index=None, spell_name=None):
        if not self.player_party.is_party_alive():
            return "DEFEAT", True
        if not self.enemy_party.is_party_alive():
            return "VICTORY", True

        if self.is_player_turn:
            if action_type == "attack":
                result = self.attack(target_index)
            elif action_type == "cast_spell":
                caster = self.get_next_active_player()
                if target_index is not None:
                    target = self.enemy_party.members[target_index]
                    result = self.cast_spell(caster, spell_name, target)
                else:
                    result = "INVALID_TARGET", False
            elif action_type == "use_item":
                user = self.get_next_active_player()
                result = self.use_item(user, spell_name)
            elif action_type == "flee":
                result = ("FLED", True) if random.random() < 0.4 else ("FAILED_FLEE", False)
            else:
                result = "INVALID_ACTION", False
        else:
            enemy = self.get_next_active_enemy()
            if hasattr(enemy, 'boss_class'):
                action, action_name = self.choose_boss_action(enemy)
                if action == "cast_spell":
                    target = random.choice(self.player_party.get_active_members())
                    result = self.cast_spell(enemy, action_name, target)
                elif action == "use_item":
                    result = self.use_item(enemy, action_name)
                else:
                    result = self.attack()
            else:
                result = self.attack()

        self.is_player_turn = not self.is_player_turn
        return result

    def get_combat_status(self):
        return {
                "player_party": self.player_party.get_party_status(),
                "enemy_party": self.enemy_party.get_party_status(),
                "current_turn": "Player" if  self.is_player_turn else "Enemy"
                }
