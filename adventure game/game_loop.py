# Game flow control
import time
import random
from characters import Player, NPC, Boss, Enemy, Spell
from party import Party
from combat import Combat 
from tree import create_story, handle_story_progression
from save_states import GameSave
from key_press import KeyboardInput

class Game:
    def __init__(self):
        self.game_save = GameSave()
        self.player = None
        self.player_party = None
        self.current_location = "town"
        self.playing = True
        self.story = create_story() # initialize story
        self.keyboard = KeyboardInput()

    def main_menu(self):
        while True:
            print("\n" + "="*50)
            print("WELCOME TO [GAME NAME]")
            print("="*50)
            print("1. New Game")
            print("2. Load Game")
            print("3. Quit")

            choice = input("\nEnter your choice: ")
            if choice == "1":
                self.start_new_game()
                if self.player: # only starts a game if a player was created
                    self.main_game_loop()
            elif choice == "2":
                if self.load_game():
                    self.main_game_loop()
            elif choice == "3":
                print("\nThanks for playing!")
                break

    def start_new_game(self):
        try:
            print("\nChoose your class:")
            print("1. Warrior")
            print("2. Mage")
            print("3. Archer")

            while True:
                choice = input("\nEnter choice (1-3): ")
                if choice == "1":
                    player_class = "Warrior"
                    break
                elif choice == "2":
                    player_class = "Mage"
                    break
                elif choice == "3":
                    player_class = "Archer"
                    break
                else:
                    print("Invalid choice! Please choose 1-3.")

            self.player = Player(player_class)
            self.player_party = Party("player")
            self.player_party.add_member(self.player)
            print(f"\nWelcome, level {self.player.level} {self.player.player_class}!")

            if not hasattr(self, 'story') or self.story is None:
                self.story = create_story()
            self.story.start_story("start")
            
            return True

        except ValueError as e:
            print(f"\nError creating character: {e}")
            return False
    
    def load_game(self):
        save_data = self.game_save.handle_save_menu(None, None)
        if save_data:
            # reconstruct player from save data
            self.player = Player(save_data["player"]["class"])
            self.player.level = save_data["player"]["level"]
            self.player.experience = save_data["player"]["experience"]
            self.player.stats = save_data["player"]["stats"]
            if "current_mana" in save_data["player"]:
                self.player.current_mana = save_data["player"]["current_mana"]
                self.player.max_mana = save_data["player"]["max_mana"]
            self.player_party = Party("player")
            self.player_party.add_member(self.player)
            self.current_location = save_data["location"]
            print(f"\nWelcome back, level {self.player.level} {self.player.player_class}!")
            return True
        return False

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

    def handle_story_node(self):
        result = handle_story_progression(self.story, self.player_party)
        if result:
            if result["type"] == "narrative":
                # display story text
                print("\n" + "="*50)
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
        self.player.stats["Health"] = self.player.max_health
        if hasattr(self.player, "current_mana"):
            self.player.current_mana = self.player.max_mana
        print("HP and Mana restored!")
        time.sleep(1)

    def start_combat(self):
        enemy_party = Party("enemy")
        enemy = Enemy("Goblin", self.player_level)
        enemy_party.add_member(enemy)
        combat = Combat(self.player_party, enemy_party)
        result = self.handle_combat(combat)

        if result:
            print("\nVictory!")
        else:
            print("\nDefeat!")
            self.current_location = "town"

    def start_boss_combat(self):
        enemy_party = Party("enemy")
        enemy = Boss("Dragon", self.player_level, self.player_party)
        enemy_party.add_member(boss)
        combat = Combat(self.player_party, enemy_party)
        result = self.handle_combat(combat)

        if result:
            print("Boss defeated!")
        else:
            print("\nDefeated by boss!")
            self.current_location = "town"

    def handle_combat(self, combat):
        # auto save before fight
        self.game_save.save_game(self.player, self.current_location, auto_save=True)
        return combat.handle_combat_encounter()

if __name__ == "__main__":
    game = Game()
    game.main_menu()
