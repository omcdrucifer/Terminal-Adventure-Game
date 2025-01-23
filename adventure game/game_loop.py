# there are likely more revisions to come, for now I have separate combat handlers for enemy and boss
# this is for testing. By the end they should be unified as the only time the player should encounter
# a boss is in a party.

import random
import time
from save_states import GameSave
from tree import create_story, handle_story_progression
from key_press import KeyboardInput
from player_classes import Player, Warrior, Mage, Archer
from party import Party
from enemy_classes import Enemy, Goblin, Orc, Ogre
from boss_classes import Boss, Dragon, Troll, Giant
from combat import Combat

class Game:
    def __init__(self):
        self.game_save = GameSave()
        self.player = Player(name="", player_class="")
        self.player_party = Party("player")
        self.current_location = "town"
        self.playing = True
        self.story = create_story()
        self.keyboard = KeyboardInput()
        
    def main_menu(self):
        while True:
            self.display_main_menu()
            choice = input("Enter your choice: ").strip()
            self.handle_main_menu_choice(choice)

    def display_main_menu(self):
        print("\n" + "=" * 50)
        print("WELCOME TO [GAME NAME]")
        print("=" * 50)
        print("1. New Game")
        print("2. Load Game")
        print("3. Quit")

    def handle_main_menu_choice(self, choice):
        if choice == "1":
            if self.start_new_game():
                self.main_game_loop()
        elif choice == "2":
            if self.load_game():
                self.main_game_loop()
        elif choice == "3":
            print("\nThanks for playing!")
            self.playing = False
            exit(0)

    def start_new_game(self):
        try:
            name = input("Enter your name: ").strip().title()
            self.player = self.choose_player_class(name)
            self.player_party = Party("player")
            self.player_party.add_member(self.player)
            print(f"\nWelcome, {name}! Your adventure begins now!")
            print(f"Level {self.player.level} {self.player.player_class}")
            self.story.start_story("start")
            return True
        except ValueError as e:
            print(f"Error creating character: {e}")
            return False

    def choose_player_class(self, name):
        while True:
            print("\nChoose your class:")
            print("1. Warrior")
            print("2. Mage")
            print("3. Archer")
            choice = input("Enter your choice (1-3): ")
            if choice == "1":
                return Warrior(name)
            elif choice == "2":
                return Mage(name)
            elif choice == "3":
                return Archer(name)
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")

    def load_game(self):
        save_data = self.game_save.handle_save_menu(self.player, self.current_location)
        if save_data:
            self.reconstruct_player(save_data)
            self.current_location = save_data["location"]
            print(f"\nWelcome back, {self.player.level} {self.player.player_class}!")
            return True
        return False

    def reconstruct_player(self, save_data):
        self.player = Player(name=save_data["player"]["name"], player_class=save_data["player"]["class"])
        self.player.level = save_data["player"]["level"]
        self.player.experience = save_data["player"]["experience"]
        self.player.stats = save_data["player"]["stats"]
        if "current_mana" in save_data["player"]:
            self.player.current_mana = save_data["player"]["current_mana"]
            self.player.max_mana = save_data["player"]["max_mana"]
        self.player_party = Party("player")
        self.player_party.add_member(self.player)

    def main_game_loop(self):
        self.playing = True
        while self.playing:
            if self.story.current_node and self.story.current_node.node_id == "start":
                print("\nWhat would you like to do?")
                print("1. Interact with NPCs")
                print("2. Access Town Menu")
                choice = input("\nEnter your choice: ").strip()

                if choice == "1":
                    self.handle_story_node()
                elif choice == "2":
                    self.story.current_node = None
                    self.handle_location_menu()
            elif self.story.current_node:
                self.handle_story_node()
            else:
                self.handle_location_menu()

    def handle_story_node(self):
        result = handle_story_progression(self.story)
        if result:
            if result["type"] == "narrative":
                self.handle_narrative_node(result)
            elif result["type"] == "combat":
                self.handle_combat_node(result)
            elif result["type"] == "recruitment":
                self.handle_recruitment_node(result)
            elif result["type"] == "dialog":
                self.handle_dialog_node(result)
        else:
            self.story.current_node = None

    def handle_narrative_node(self, result):
        narrative_result = result["content"]
        print("\n" + "=" * 50)
        print(narrative_result["text"])
        print(narrative_result["description"])
        self.display_choices(result["choices"])
        choice = self.get_choice(result["choices"])
        if choice:
            print(f"Debug: Next node = {choice['next_node']}")
            self.story.make_choice(choice["id"])

            if choice["next_node"] == "start":
                self.story.current_node = self.story.nodes["start"]
        else:
            print("Invalid choice. Please try again.")

    def handle_dialog_node(self, result):
        dialog_result = result["content"]
        print("\n" + "=" * 50)
        print(dialog_result["text"])
        print(dialog_result["description"])
        self.display_choices(result["choices"])
        choice = self.get_choice(result["choices"])
        if choice:
            print(f"Debug: Next node = {choice['next_node']}")
            if choice["next_node"] == "buy_item":
                pass # need to make a shop menu
            self.story.make_choice(choice["id"])

            if choice["next_node"] == "start":
                self.story.current_node = self.story.nodes["start"]
        else:
            print("Invalid choice. Please try again.")

    def display_choices(self, choices):
        print("\nChoices:")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice['text']}")

    def get_choice(self, choices):
        while True:
            try:
                choice_num = int(input("Enter your choice: ").strip()) - 1
                if 0 <= choice_num < len(choices):
                    return choices[choice_num]
            except ValueError:
                print("Please enter a valid number.")

    def handle_combat_node(self, result):
        enemy_party = Party("enemy")
        enemy_type = result["content"]["enemy"]
        enemy_level = result["content"]["level"]

        if enemy_type in ["Dragon", "Troll", "Giant"]:
            enemy = Boss(enemy_type, enemy_level)
        else:
            enemy = Enemy(enemy_type, enemy_level)

        enemy_party.add_member(enemy)
        combat = Combat(self.player_party, enemy_party)
        
        combat_result = self.handle_combat(combat)

        if combat_result == "VICTORY":
            print(f"\nYou defeated the {enemy_type}!")
            self.player.gain_experience(result["content"]["experience_reward"])
            next_node = result["content"]["victory_node"]
        else:
            print(f"\nYou were defeated by the {enemy_type}!")
            next_node = result["content"]["defeat_node"]

        self.story.current_node = self.story.nodes[next_node]

    def handle_recruitment_node(self, result):
        recruitment_result = result["content"]
        self.handle_recruitment_node(recruitment_result)
        self.story.current_node = self.story.nodes[recruitment_result["next_node"]]

    def handle_location_menu(self):
        if self.current_location == "town":
            self.town_menu()
        elif self.current_location == "dungeon":
            self.dungeon_menu()
        else:
            print("Error: Invalid location.")
            self.current_location = "town"

    def town_menu(self):
        while self.current_location == "town":
            self.display_town_header()
            if not self.valid_player_check():
                return
            self.display_town_options()
            choice = input("\nEnter your choice: ").strip()
            self.handle_town_choice(choice)

    def display_town_header(self):
        print("\n" + "=" * 50)
        print("TOWN")
        print("=" * 50)

    def valid_player_check(self):
        if self.player is None:
            print("Error: Player not found.")
            return False
        return True

    def display_town_options(self):
        print(f"Level {self.player.level} {self.player.player_class}")
        print(f"HP: {self.player.stats['Health']}")
        if self.player.player_class == "Mage":
            print(f"Mana: {self.player.current_mana}/{self.player.max_mana}")
        print("\nTown Options:")
        print("1. Enter Dungeon")
        print("2. Rest (Restore HP/Mana)")
        print("3. Game Menu")
        print("4. Quit to Main Menu")

    def handle_town_choice(self, choice):
        if choice == "1":
            self.current_location = "dungeon"
        elif choice == "2":
            self.rest()
        elif choice == "3":
            self.game_menu()
        elif choice == "4":
            self.story.current_node = None
            self.main_menu()

    def dungeon_menu(self):
        while self.current_location == "dungeon":
            self.display_dungeon_header()
            if not self.valid_player_check():
                return
            self.display_dungeon_options()
            choice = input("\nEnter your choice: ").strip()
            self.handle_dungeon_choice(choice)

    def display_dungeon_header(self):
        print("\n" + "=" * 50)
        print("DUNGEON")
        print("=" * 50)

    def display_dungeon_options(self):
        print(f"Level {self.player.level} {self.player.player_class}")
        print(f"HP: {self.player.stats['Health']}")
        if self.player.player_class == "Mage":
            print(f"Mana: {self.player.current_mana}/{self.player.max_mana}")
        print("\nWhat would you like to do?")
        print("1. Fight Enemy")
        print("2. Fight Boss")
        print("3. Return to Town")
        print("4. Game Menu")

    def handle_dungeon_choice(self, choice):
        if choice == "1":
            self.start_combat()
        elif choice == "2":
            self.start_boss_combat()
        elif choice == "3":
            self.current_location = "town"
        elif choice == "4":
            self.game_menu()

    def game_menu(self):
        while True:
            self.display_game_menu()
            choice = input("\nEnter your choice: ").strip()
            if choice == "4":
                break
            self.handle_game_menu_choice(choice)

    def display_game_menu(self):
        print("\n" + "=" * 50)
        print("GAME MENU")
        print("=" * 50)
        print("1. Save Game")
        print("2. Load Game")
        print("3. Character Stats")
        print("4. Return to Game")

    def handle_game_menu_choice(self, choice):
        if choice == "1":
            self.game_save.handle_save_menu(self.player, self.current_location)
        elif choice == "2":
            self.load_game()
        elif choice == "3":
            self.show_character_stats()

    def show_character_stats(self):
        print("\n" + "=" * 50)
        print("CHARACTER STATS")
        print("=" * 50)
        if self.player:
            print(f"Name: {self.player.name}")
            print(f"Class: {self.player.player_class}")
            print(f"Level: {self.player.level}")
            print("\nStats:")
            for stat, value in self.player.stats.items():
                print(f"{stat}: {value}")
        input("\nPress Enter to continue...")

    def rest(self):
        print("\nResting...")
        time.sleep(1)
        if self.player:
            max_health = self.player.max_health
            if max_health is not None:
                self.player.stats["Health"] = max_health
            if hasattr(self.player, "current_mana") and hasattr(self.player, "max_mana"):
                self.player.current_mana = self.player.max_mana
            print("HP and Mana restored!")
        time.sleep(1)

    def start_combat(self):
        if self.player:
            enemy_level = self.player_party.get_average_level()
            enemies_list = [Goblin(enemy_level), Orc(enemy_level), Ogre(enemy_level)]
            random_enemy = random.choice(enemies_list)
            enemy_party = Party("enemy")
            enemy = random_enemy
            enemy_party.add_member(enemy)
            combat = Combat(self.player_party, enemy_party)
            result = self.handle_combat(combat)
            self.handle_combat_result(result)

    def start_boss_combat(self):
        if self.player:
            enemy_level = self.player_party.get_average_level() + 2
            boss_list = [Dragon(enemy_level), Troll(enemy_level), Giant(enemy_level)]
            random_boss = random.choice(boss_list)
            enemy_party = Party("enemy")
            boss = random_boss
            enemy_party.add_member(boss)
            combat = Combat(self.player_party, enemy_party)
            result = self.handle_combat(combat)
            self.handle_combat_result(result)
    # boss and enemy combat are separated for testing, ideally they should be partied in the game
    # and so one combat system should be enough. I don't see putting the player in any solo boss fights
    def handle_combat(self, combat):
        while True:
            self.display_combat_status(combat)

            if combat.is_player_turn:
                print("\nActions:")
                print("1. Attack")
                if self.player.player_class == "Mage":
                    print("2. Cast Spell")
                print("3. Use Item")
                print("4. Flee")

                choice = input("\nEnter your choice: ").strip()

                if choice == "1":
                    print("\nChoose target:")
                    for i, enemy in enumerate(combat.enemy_party.members, 1):
                        print(f"{i}. {enemy.name} - HP: {enemy.stats['Health']}")
                    target = int(input("Enter target number: ").strip()) - 1
                    result, success = combat.handle_combat_turn("attack", target)

                elif choice == "2" and self.player.player_class == "Mage":
                    print("\nAvailable Spells:")
                    for i, spell in enumerate(self.player.spells, 1):
                        print(f"{i}. {spell}")
                    spell_choice = int(input("Enter spell number: ").strip()) - 1
                    spell_name = list(self.player.spells.keys())[spell_choice]

                    print("\nChoose target:")
                    for i, enemy in enumerate(combat.enemy_party.members, 1):
                        print(f"{i}. {enemy.enemy_class} - HP: {enemy.stats['Health']}")
                    target = int(input("Enter target number: ").strip()) - 1

                    result, success = combat.handle_combat_turn("cast_spell", target, spell_name)

                elif choice == "3":
                    print("\nItems:")
                    for i, item in enumerate(self.player.inventory.items, 1):
                        print(f"{i}. {item}")
                    item_choice = int(input("Enter item number: ").strip()) - 1
                    item_name = self.player.inventory.items[item_choice]
                    target = self.player

                    result, success = combat.handle_combat_turn("use_item", target, item_name)

                elif choice == "4":
                    result, success = combat.handle_combat_turn("flee")
                    if success:
                        print("You fled from the battle!")
                        return "FLED"
            else:
                result, success = combat.handle_combat_turn("attack")
                
                if "_" in result:
                    action, value = result.split("_")
                    if action == "DAMAGE":
                        print(f"\nYou dealt {value} damage to the enemy!")
                    elif action == "MANA_RESTORED":
                        print(f"\nYou restored {value} mana!")

                if result in ["VICTORY", "DEFEAT"]:
                    return result

                input("\nPress Enter to continue...")

    def display_combat_status(self, combat):
        status = combat.get_combat_status()
        print("\n" + "=" * 50)
        print("COMBAT STATUS")
        print("=" * 50)
        print("\nPlayer Party:")
        for member, member_type in status["player_party"]:
            print(f"{member_type} {member.name} - HP: {member.stats['Health']}")
            if hasattr(member, "current_mana"):
                print(f"Mana: {member.current_mana}/{member.max_mana}")
        print("\nEnemy Party:")
        for member, member_type in status["enemy_party"]:
            print(f"{member.enemy_class} - HP: {member.stats['Health']}")

    def handle_combat_result(self, result):
        if result == "VICTORY":
            print("\nYou won the battle!")
        elif result == "DEFEAT":
            print("\nYou were defeated!")
            self.playing = False
            self.main_menu()
        elif result == "FLED":
            self.current_location = "town"

if __name__ == "__main__":
    game = Game()
    game.main_menu()
