# Game flow control
from math import inf
import random
from characters import Player, NPC, Enemy, Boss, Spell
from party import Party
from combat import Combat, Spell
from Story import StoryNode, StoryChoice, StoryTree, handle_story_progression, create_example_story # these are filler for now
from save_states import GameSave

class Game:
    def __init__(self):
        self.game_save = GameSave()
        self.player = None
        self.player_party = None
        self.current_location = "town"
        self.playing = True
        self.story = create_example_story() # initialize story

    def start_new_game(self):
        try:
            self.player = Player()
            self.player_party = Party("player")
            self.player_party.add_member(self.player)
            print(f"\nWelcome, level {self.player.level} {self.player.player_class}!")
            self.story.start_story("start")
        except ValueError as e:
            print(f"\nError creating character: {e}")
            return False

    def handle_story_node(self):
        result = handle_story_progression(self.story, self.player_party)
        if result:
            if result["type"] == "narrative":
                # display story text
                print("\n" + "="*50))
                print(result["content"]["text"])
                print(result["content"]["description"])

                print("\nChoices:")
                for i, choice in enumerate(result["choices"], 1):
                    print(f"{i}. {choice.text}")
                # get player choice
                while True:
                    try:
                        choice_num = int(input("\nEnter your choice: ")) - 1
                        if 0 <= choice_num < len(result["choices"]):
                            chosen = result["choices"][choice_num]
                            self.story.current_node = self.story.nodes[chosen.next_node_id]
                            break
                    except ValueError:
                        print("Please enter a valid number.")
            elif result["type"] == "combat":
                combat_result = self.handle_combat(result["combat"])
            elif result["type"] == "recruitment":
                self.handle_recruitment(result["content"])

    def main_game_loop(self):
        self.playing = True
        while self.playing:
            self.handle_story_node()
            # could add location based menus triggered by progression
            if self.current_location == "town":
                self.town_menu()
            elif self.current_location == "dungeon":
                self.dungeon_menu()
            else:
                print("Error: Invalid location!")
                self.current_location = "town"
    # i still need to write an actual story, these menus are placeholder concepts only
    def town_menu(self):
        while self.current_location == "town":
            print("\n" + "="*50)
            print("TOWN")
            print("="*50)
            print(f"Level {self.player.level} {self.player.player_class}")
            print(f"HP: {self.player.stats['Health']}")
            if self.player.player_class in ["Mage", "Healer"]:
                print(f"Mana: {self.player.current_mana}/{self.player.max_mana}")
            print("\nWhat would you like to do?")
            print("1. Enter Dungeon")
            print("2. Rest (Restore HP/Mana)")
            print("3. Game Menu")
            print("4. Quit to Main Menu")

            choice = input("\nEnter your choice: ")
            if choice =="1":
                self.current_location = "dungeon"
            elif choice =="2":
                self.rest()
            elif choice =="3":
                self.game_menu()
            elif choice =="4":
                self.playing = False
                break

    def dungeon_menu(self):
        while self.current_location == "dungeon":
            print("\n" + "="*50)
            print("DUNGEON")
            print("="*50)
            print(f"Level {self.player.level} {self.player.player_class}")
            print(f"HP: {self.player.stats['Health']}")
            if self.player.player_class in ["Mage", "Healer"]:
                print(f"Mana: {self.player.current_mana}/{self.player.max_mana}")
            print("\nWhat would you like to do?")
            print("1. Fight Enemy")
            print("2. Fight Boss")
            print("3. Return to Town")
            print("4. Game Menu")

            choice = input("\nEnter your choice: ")
            if choice =="1":
                self.start_combat()
            elif choice =="2":
                self.start_boss_combat()
            elif choice =="3":
                self.current_location = "town"
                break
            elif choice =="4":
                self.game_menu()

    def game_menu(self):
        while True:
            print("\n" + "="*50)
            print("GAME MENU")
            print("="*50)
            print("1. Save Game")
            print("2. Load Game")
            print("3. Character Stats")
            print("4. Return to Game")

            choice = input("\nEnter your choice: ")
            if choice =="1":
                self.game_save.handle_save_menu(self.player, self.current_location)
            elif choice =="2":
                save_data = self.game_save.handle_save_menu(None, None)
                if save_data:
                    self.load_game()
            elif choice =="3":
                self.show_character_stats()
            elif choice =="4":
                break

    def show_character_stats(self):
        print("\n" + "="*50)
        print("CHARACTER STATS")
        print("="*50)
        print(f"Class: {self.player.player_class}")
        print(f"Level: {self.player.level}")
        print(f"Experience: {self.player.experience}/{self.player.experience_to_next_level}")
        print("\nStats:")
        for stat, value in self.player.stats.items():
            print(f"{stat}: {value}")
        input("\nPress Enter to continue...")

    def rest(self):
        print("\nResting...")
        time.sleep(1)
        self.player.stats["Health"] = 100 # placeholder until I can figure out how to get this to reference Health
        if hasattr(self.player, "current_mana"):
            self.player.current_mana = self.player.max_mana
        print("HP and Mana restored!")
        time.sleep(1)

    def start_combat(self):

    def handle_combat_encounter(player_party, enemy_party):
        combat = Combat(player_party, enemy_party)
        while True:
            party_status, enemy_status = combat.get_combat_status()
            print("\nCurrent Combat Status:")
            print("Player Party:")
            for status in party_status:
                print(f"- {status}")
            print("Enemy Party:")
            for status in enemy_status:
                print(f"- {status}")

            if combat.is_player_turn:
                active_combatant = combat.get_active_combatant()
                if isinstance(active_combatant, Player):
                    print(f"\n{active_combatant.player_class}'s turn!")
                    print("1. Attack")
                    # add more actions here like use item, cast spell, etc

                    while True:
                        try:
                            action = int(input("Choose your action (1-1):")) # adjust as more choices are added
                            if action == 1: # attack
                                print("Choose target:")
                                for i, status, in enumerate(enemy_status):
                                    print(f"{i + 1}. {status}")
                                target = int(input(f"\nSelect target (1-{len(enemy_status)}): ")) - 1
                                if 0 <= target < len(enemy_status):
                                    result = combat.attack(target)
                                    handle_combat_result(result)
                                    break
                                else:
                                    print("Invalid target!")
                            else:
                                print("Invalid action!")
                        except ValueError:
                            print("Please enter a valid number!")
                else:
                    # NPC automatic attack
                    result = combat.attack()
                    handle_combat_result(result)
            else:
                # enemy turn
                result = combat.attack()
                handle_combat_result(result)
            # check for combat end
            if result in ["VICTORY", "DEFEAT"]:
                return result == "VICTORY"

    def handle_combat_result(result):
        if result.startswith("HIT"):
            damage = result.split("_")[1]
            print(f"Hit! Dealt {damage} damage!")
        elif result == "MISS":
            print("Attack missed!")
        elif result.startswith("DEFEAT_"):
            defeated_type = result.split("_")[1]
            print(f"{defeated_type} was defeated!")
        elif result == "VICTORY":
            print("Victory! All enemies defeated!")
        elif result == "DEFEAT":
            print("Defeat! Your party has fallen!")
