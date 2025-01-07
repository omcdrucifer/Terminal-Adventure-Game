import random
from characters import Player, NPC, Boss, Enemy, Spell

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

    def can_cast_spell(self, caster, spell_name):
        available_spells = self.get_available_spells(caster)
        if spell_name not in available_spells:
            return "Invalid Spell"

        spell = available_spells[spell_name]
        if not spell.can_cast(caster):
            return False, "Not enough mana"

        return True, "Can cast spell"

    def cast_spell(self, caster, spell_name, target):
        available_spells = self.get_available_spells(caster)
        if spell_name not in available_spells:
            return "Invalid Spell"
        spell = available_spells[spell_name]
        can_cast, message = self.can_cast_spell(caster, spell_name)
        if not can_cast:
            return message

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
        self.current_turn_index = (self.current_turn_index + 1) % len(self.initiative_order)
        active_combatant = self.get_active_combatant()
        self.is_player_turn = isinstance(active_combatant, (Player, NPC))

    def attack(self, target_index=None):
        if not self.player_party.is_party_alive():
            return "DEFEAT"

        if self.is_player_turn:
            attacker = self.player_party.members[self.active_player_index]
            if target_index is None:
                target_index = self.active_enemy_index
            defender = self.enemy_party.members[target_index]
        else:
            attacker = self.enemy_party.members[self.active_enemy_index]
            active_members = self.player_party.get_active_members()
            if not active_members:
                return "DEFEAT"
            defender = random.choice(active_members)

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
                    if not self.enemy_party.get_active_members():
                        return "VICTORY"
                elif not self.player_party.get_active_members():
                    return "DEFEAT"
            return f"HIT_{actual_damage}"
        else:
            return "MISS"

    def handle_experience(self, attacker, defeated_enemy):
        initial_level = attacker.level
        attacker.gain_experience(defeated_enemy.experience_value)
        if attacker.level > initial_level:
            self.player_party.synchronize_level(attacker.level)

    def get_active_combatant(self):
        return self.initiative_order[self.current_turn_index]

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

    def handle_combat_action(self, combatant, action_type, target_index=None, spell_name=None, item_name=None):
        if action_type == "attack":
            return self.attack(target_index)
        elif action_type == "flee":
            flee_chance = random.randint(1, 100)
            if flee_chance <= 50:
                return "FLED"
            return "FAILED_FLEE"
        elif action_type == "cast_spell":
            if target_index is not None:
                target = self.enemy_party.members[target_index]
                return self.cast_spell(combatant, spell_name, target)
            return "INVALID_TARGET"
        elif action_type == "use_item":
            if not isinstance(combatant, Player):
                return "INVALID_ACTION"

            if item_name is None:
                return "INVALID_ITEM"

            item = combatant.available_items.get(item_name)
            if not item:
                return "INVALID_ITEM"

            if item.effect_type in ["heal", "mana", "buff_strength"]:
                print("\nChoose target:")
                for i, member in enumerate(self.player_party.members):
                    print(f"{i + 1}. {self.get_combatant_type(member)} (HP: {member.stats['Health']})")

                try:
                    target_choice = int(input(f"\nSelect target (1-{len(self.player_party.members)}): ")) - 1
                    if 0 <= target_choice < len(self.player_party.members):
                        target = self.player_party.members[target_choice]
                    else:
                        return "INVALID_TARGET"
                except ValueError:
                    return "INVALID_TARGET"
            else:
                if target_index is not None:
                    target = self.enemy_party.members[target_index]
                else:
                    return "INVALID_TARGET"

            success, message = combatant.use_item(item_name, target)
            if success:
                return f"ITEM_USED_{message}"
            return f"ITEM_FAILED_{message}"

        return "UNKNOWN_ACTION"

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
        elif result.startswith("DEFEAT_"):
            defeated_type = result.split("_")[1]
            print(f"{defeated_type} was defeated!")
        elif result == "FLED":
            print("Returned to town!")
        elif result == "VICTORY":
            print("Victory! All enemies defeated!")
        elif result == "DEFEAT":
            print("Defeat! Your party has fallen!")

    def handle_combat_encounter(self):
        max_iterations = 1  # Set a maximum number of iterations to prevent infinite loop
        iteration_count = 0

        while iteration_count < max_iterations:
            iteration_count += 1
            print(f"Iteration: {iteration_count}")
            print("Checking victory/defeat conditions...")

            if not self.enemy_party.is_party_alive():
                print("Enemy party defeated. Victory!")
                return "VICTORY"
            if not self.player_party.is_party_alive():
                print("Player party defeated. Defeat!")
                return "DEFEAT"

            party_status, enemy_status = self.get_combat_status()
            print("\nCurrent Combat Status:")
            print("Player Party:")
            for status in party_status:
                print(f"- {status}")
            print("Enemy Party:")
            for status in enemy_status:
                print(f"- {status}")

            if self.is_player_turn:
                active_combatant = self.get_active_combatant()
                if isinstance(active_combatant, Player):
                    print(f"\n{active_combatant.player_class}'s turn!")
                    print("1. Attack")
                    print("2. Cast Spell")
                    print("3. Use Item")
                    print("4. Flee")

                    try:
                        action = int(input("Choose your action (1-4): "))
                        if action == 1:  # attack
                            print("Choose target:")
                            for i, status in enumerate(enemy_status):
                                print(f"{i + 1}. {status}")
                            target = int(input(f"\nSelect target (1-{len(enemy_status)}): ")) - 1
                            if 0 <= target < len(enemy_status):
                                result = self.attack(target)
                                self.handle_combat_result(result)
                                if result in ["VICTORY", "DEFEAT"]:
                                    return result
                            self.handle_initiative()
                        elif action == 2:
                            if not active_combatant.spells:
                                print("No spells available!")
                                continue

                            print("\nAvailable Spells:")
                            for spell_name, spell in active_combatant.spells.items():
                                print(f" - {spell_name} (Mana Cost: {spell.mana_cost})")

                            spell_name = input("\nEnter spell name (or 'back'): ")
                            if spell_name.lower() == 'back':
                                continue

                            print("\nChoose target:")
                            for i, status in enumerate(enemy_status):
                                print(f"{i + 1}. {status}")
                            target = int(input(f"\nSelect target (1-{len(enemy_status)}): ")) - 1

                            if 0 <= target < len(enemy_status):
                                result = self.handle_combat_action(active_combatant, "cast_spell", target, spell_name)
                                self.handle_combat_result(result)
                                if result.startswith("DEFEAT"):
                                    return "VICTORY"
                                self.handle_initiative()
                        elif action == 3:
                            if not active_combatant.inventory.items:
                                print("No items in inventory!")
                                continue

                            print("\nAvailable Items:")
                            for item_name, quantity in active_combatant.inventory.items.items():
                                item = active_combatant.available_items[item_name]
                                print(f"- {item_name} (x{quantity}): {item.description}")

                            item_name = input("\nEnter item name (or 'back'): ")
                            if item_name.lower() == 'back':
                                continue

                            if item_name not in active_combatant.inventory.items:
                                print("\nInvalid item!")
                                continue

                            result = self.handle_combat_action(active_combatant, "use_item", None, None, item_name)
                            self.handle_combat_result(result)
                            self.handle_initiative()
                        elif action == 4:  # flee
                            flee_chance = random.randint(1, 100)
                            if flee_chance <= 50:
                                print("Successfully fled!")
                                return "FLED"
                            print("Failed to flee!")
                            self.handle_initiative()
                    except ValueError:
                        print("Please enter a valid number!")
                        continue
                else:
                    # NPC automatic attack
                    result = self.attack()
                    self.handle_combat_result(result)
                    if result in ["VICTORY", "DEFEAT"]:
                        return result
                    self.handle_initiative()
            else:
                # Enemy attack
                result = self.attack()
                self.handle_combat_result(result)
                if result in ["VICTORY", "DEFEAT"]:
                    return result
                self.handle_initiative()

        print("Reached maximum iterations. Possible infinite loop detected.")
        return "INFINITE_LOOP_DETECTED"
