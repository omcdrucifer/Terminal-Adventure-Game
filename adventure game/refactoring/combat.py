# planning to completely retool the combat system to be more modular and easier to work with
# currently it's mostly the same as it was before, a few lines of code have varied syntax and I removed some of the 
# debugging print statements because I debugged the hell out of this code before I hit that debug loop
import random
from player_classes import Player, initialize_mage_spells
from npc_classes import initialize_healer_spells
from enemy_classes import Enemy
from boss_classes import Boss, initialize_dragon_spells, initialize_troll_spells, initialize_giant_spells

class Combat:
    def __init__(self, player_party, enemy_party):
        self.player_party = player_party
        self.enemy_party = enemy_party
        self.initiative_order = []
        self.current_turn_index = 0
        self.is_player_turn = True
        self.active_player_index = 0
        self.active_enemy_index = 0
        self.fled = False
        self.spells = {
                initialize_mage_spells,
                initialize_healer_spells,
                initialize_dragon_spells,
                initialize_troll_spells,
                initialize_giant_spells
                }

        self.setup_initiative()

    def setup_initiative(self):
        all_combatants = []

        for member in self.player_party.members + self.enemy_party.members:
            base_initiative = random.randint(1, 20)
            agility_bonus = member.stats.get("Agility", 0) * 0.5
            member.initiative = base_initiative + agility_bonus
            all_combatants.append(member)

        self.initiative_order = sorted(all_combatants, key=lambda x: x.initiative, reverse=True)
        print(f"Initiative Order: {[member.name for member in self.initiative_order]}")

    def get_next_active_player(self):
        active_members = self.player_party.get_active_members()
        if not active_members:
            return False
        current_member = self.player_party.members[self.active_player_index]
        while current_member.stats["Health"] <= 0:
            self.active_player_index = (self.active_player_index + 1) % len(self.player_party.members)
            current_member = self.player_party.members[self.active_player_index]
        return current_member # may need to replace with True, need to test

    def get_next_active_enemy(self):
        active_members = self.enemy_party.get_active_members()
        if not active_members:
            return False
        current_member = self.enemy_party.members[self.active_enemy_index]
        while current_member.stats["Health"] <= 0:
            self.active_enemy_index = (self.active_enemy_index + 1) % len(self.enemy_party.members)
            current_member = self.enemy_party.members[self.active_enemy_index]
        return current_member

    def get_available_spells(self, combatant):
        if hasattr(combatant, 'spells'):
            return combatant.spells
        return {}

    def can_cast_spell(self, caster, spell_name):
        available_spells = self.get_available_spells(caster)
        if spell_name not in available_spells:
            return False, "Invalid Spell"
        spell_name = available_spells[spell_name]
        if caster.current_mana < spell_name["mana_cost"]:
            return False, "Not enough mana"

        return True, "Can cast spell"

    def cast_spell(self, caster, spell_name, target):
        available_spells = self.get_available_spells(caster)
        if spell_name not in available_spells:
            return False, "Invalid Spell"
        spell_name = available_spells[spell_name]
        can_cast, message = self.can_cast_spell(caster, spell_name)
        if not can_cast:
            return False, message

        magic_bonus = caster.stats.get("Magic", 0) * spell_name.scaling_factor
        base_effect = random.randint(spell_name.base_damage - 5, spell_name.base_damage + 5)
        total_effect = int(base_effect + magic_bonus)

        caster.current_mana -= spell_name.mana_cost

        if spell_name in ["Heal", "Blessing"]:
            target.stats["Health"] += total_effect
            return f"Spell heal {total_effect} HP", True
        else:
            if "Magic" in target.stats:
                magic_resist = target.stats["Magic"] * 0.2
                total_effect = max(0, total_effect - magic_resist)

            target.stats["Health"] -= total_effect

            if target.stats["Health"] <= 0:
                target.stats["Health"] = 0
                if isinstance(target, (Enemy, Boss)) and hasattr(caster, "player_class"):
                    self.handle_experience(caster, target)
                    if not self.enemy_party.is_party_alive():
                        return "VICTORY", True
                return f"DEFEAT {self.get_combatant_type(target)}", True

            return f"Spell hit {total_effect} HP", True

    def handle_initiative(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.initiative_order)
        active_combatant = self.get_active_combatant()
        self.is_player_turn = isinstance(active_combatant, Player)
        if self.is_player_turn:
            self.active_player_index = self.player_party.members.index(active_combatant)
        else:
            self.active_enemy_index = self.enemy_party.members.index(active_combatant)
        
        print(f"Current Turn Index: {self.current_turn_index}")
        print(f"Active Combatant: {active_combatant.name}")
        print(f"Is Player Turn: {self.is_player_turn}")

    def attack(self, target_index=None):
        if not self.player_party.is_party_alive():
            return "DEFEAT", False

        if self.is_player_turn:
            attacker = self.player_party.members[self.active_player_index]
            if target_index is None or target_index < 0 or target_index >= len(self.enemy_party.members):
                return "INVALID_TARGET", False
            defender = self.enemy_party.members[target_index]
        else:
            attacker = self.enemy_party.members[self.active_enemy_index]
            active_members = self.player_party.get_active_members()
            if not active_members:
                return "DEFEAT", False
            defender = random.choice(active_members)

        hit_chance = 75
        if random.randint(1, 100) <= hit_chance:
            damage = random.randint(5, attacker.stats["Strength"] // 2) if isinstance(attacker, Boss) else random.randint(5, attacker.stats["Strength"])
            defense = random.randint(0, defender.stats["Defense"])
            actual_damage = max(0, damage - defense)
            defender.stats["Health"] -= actual_damage

            if defender.stats["Health"] <= 0:
                defender.stats["Health"] = 0
                if isinstance(defender, (Enemy, Boss)) and isinstance(attacker, Player):
                    self.handle_experience(attacker, defender)
                    if not self.enemy_party.is_party_alive():
                        return "VICTORY", True
                    elif not self.player_party.is_party_alive():
                        return "DEFEAT", True
                return f"HIT_{actual_damage}", True
            else:
                return "MISS", True

    def handle_experience(self, attacker, defeated_enemy):
        initial_experience = attacker.experience
        attacker.gain_experience(defeated_enemy.experience_value)
        print(f"Experience Gained: {defeated_enemy.experience_value}")
        if attacker.experience > initial_experience:
            print(f"Experience Updated: {attacker.experience}")

    def get_active_combatant(self):
        return self.initiative_order[self.current_turn_index]

    def get_combat_status(self):
        return (
                self.player_party.get_party_status(),
                self.enemy_party.get_party_status()
                )

    def get_combatant_type(self, combatant):
        for attr in ["player_class", "npc_class", "enemy_class", "boss_class"]:
            if hasattr(combatant, attr):
                return attr.split("_")[0].capitalize()
        return "Unknown"
    
    def handle_combat_action(self, combatant, action_type, target_index=None, spell_name=None, item_name=None):
        if action_type == "attack":
            return self.attack(target_index)
        elif action_type == "flee":
            flee_chance = random.randint(1, 100)
            if flee_chance <= 50:
                self.fled = True
                return "FLED", True
            return "FAILED_FLEE", False
        elif action_type == "cast_spell":
            if target_index is not None:
                target = self.enemy_party.members[target_index] if self.is_player_turn else self.player_party.members[target_index]
                return self.cast_spell(combatant, spell_name, target)
            return "INVALID_TARGET", False
        elif action_type == "use_item":
            if item_name is None:
                return "INVALID_ITEM", False

            item = combatant.inventory.get_item(item_name)
            if not item:
                return "INVALID_ITEM", False

            if item.effect_type in ["heal", "mana", "buff_strength", "buff_agility"]:
                print("\nChoose target:")
                for i, member in enumerate(self.player_party.get_active_members()):
                    print(f"{i+1}. {member.name} - {member.stats['Health']} HP")

                try:
                    target_choice = int(input(f"\nSelect target (1-{len(self.player_party.get_active_members())}): ")) - 1
                    if 0 <= target_choice < len(self.player_party.members):
                        target = self.player_party.members[target_choice]
                    else:
                        return "INVALID_TARGET", False
                except ValueError:
                    return "INVALID_TARGET", False
            else:
                if target_index is not None:
                    target = self.enemy_party.members[target_index] if self.is_player_turn else self.player_party.members[target_index]
                else:
                    return "INVALID_TARGET", False

            success, message = combatant.use_item(item_name, target)
            if success:
                return f"ITEM_USED_{message}", True
            return f"ITEM_FAILED_{message}", False

        return "UNKNOWN_ACTION", False

    def handle_combat_result(self, result):
        if isinstance(result, str):
            if result.startswith("HIT_"):
                damage = result.split("_")[1]
                print(f"Hit! Dealt {damage} damage!")
            elif result.startswith("ITEM_USED_"):
                message = result.split("ITEM_USED_")[1]
                print(message)
            elif result.startswith("ITEM_FAILED_"):
                message = result.split("ITEM_FAILED_")[1]
                print(f"Failed to use item: {message}")
        elif result == "MISS":
            print("Attack missed!")
        elif result == "VICTORY":
            print("Victory! All enemies defeated!")
        elif result == "DEFEAT":
            print("Defeat! Your party has fallen!")

    def handle_combat_encounter(self):
        if not self.enemy_party.is_party_alive():
            return "VICTORY", True
        if not self.player_party.is_party_alive():
            return "DEFEAT", True

        if self.is_player_turn:
            if not self.get_next_active_player():
                return "DEFEAT", True
            active_combatant = self.get_active_combatant()
            if isinstance(active_combatant, Player):
                try:
                    action = int(input("Choose your action (1-4): "))
                    if action == 1:
                        target = int(input(f"\nSelect target (1-{len(self.enemy_party.get_active_members())}): ")) - 1
                        if 0 <= target < len(self.enemy_party.members):
                            result = self.attack(target)
                            self.handle_combat_result(result)
                            if result in ["VICTORY", "DEFEAT"]:
                                return result, True
                        else:
                            print("Invalid target index: {target}")
                    elif action == 2:
                        if not active_combatant.spells:
                            print("No spells available!")
                            return
                        spell_name = input("\nEnter spell name (or 'back'): ")
                        if spell_name.lower() == "back":
                            return
                        target = int(input(f"\nSelect target (1-{len(self.enemy_party.get_active_members())}): ")) - 1
                        if 0 <= target < len(self.enemy_party.members):
                            result = self.cast_spell(active_combatant, spell_name, self.enemy_party.members[target])
                            self.handle_combat_result(result)
                            if result in ["VICTORY", "DEFEAT"]:
                                return result, True
                        else:
                            print("Invalid target index: {target}")
                    elif action == 3:
                        if not active_combatant.inventory.items:
                            print("No items available!")
                            return
                        item_name = input("\nEnter item name (or 'back'): ")
                        if item_name.lower() == "back":
                            return
                        if item_name not in active_combatant.inventory.items:
                            print("Invalid item name!")
                            return
                        result = self.handle_combat_action(active_combatant, "use_item", item_name=item_name)
                        self.handle_combat_result(result)
                    elif action == 4:
                        if random.randint(1, 100) <= 50:
                            self.fled = True
                            return "FLED", True
                        print("Failed to flee!")
                except (ValueError, StopIteration):
                    print("Please enter a valid number!")
                    return
            else:
                result = self.attack()
                self.handle_combat_result(result)
                if result in ["VICTORY", "DEFEAT"]:
                    return result, True
        else:
            if not self.get_next_active_enemy():
                return "VICTORY", True
            result = self.attack()
            self.handle_combat_result(result)
            if result in ["VICTORY", "DEFEAT"]:
                return result, True

        self.handle_initiative()
