# Game flow control
import time
from typing import Any, Dict, Optional, Tuple, cast
from characters import Player, NPC, Boss, Enemy
from story_types import CombatResult, NarrativeResult, RecruitmentResult
from party import Party
from combat import Combat 
from tree import StoryTree, create_story, handle_story_progression
from save_states import GameSave
from key_press import KeyboardInput

class Game:
    player: Optional[Player]
    player_party: Optional[Party]
    current_location: str
    playing: bool
    story: StoryTree
    keyboard: KeyboardInput
    game_save: GameSave

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
    
    def load_game(self) -> bool:
        save_data: Optional[Dict[str, Any]] = self.game_save.handle_save_menu(None, self.current_location)
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
                # Type cast the result
                narrative_result = cast(NarrativeResult, result)
                # display story text
                print("\n" + "="*50)
                print(narrative_result["content"]["text"])
                print(narrative_result["content"]["description"])

                print("\nChoices:")
                for i, choice in enumerate(narrative_result["choices"], 1):
                    print(f"{i}. {choice.text}")
                # get player choice
                while True:
                    try:
                        choice_num = int(input("\nEnter your choice: ")) - 1
                        if 0 <= choice_num < len(narrative_result["choices"]):
                            chosen = narrative_result["choices"][choice_num]
                            self.story.current_node = self.story.nodes[chosen.next_node_id]
                            break
                    except ValueError:
                        print("Please enter a valid number.")
            elif result["type"] == "combat":
                # Type cast the result
                combat_result = cast(CombatResult, result)
                result = self.handle_combat(combat_result["combat"])
                if result == "VICTORY":
                    self.story.current_node = self.story.nodes[combat_result["combat"]["victory_node"]]
                elif result == "DEFEAT":
                    self.story.current_node = self.story.nodes[combat_result["combat"]["defeat_node"]]
                elif result == "FLED":
                    self.current_location = "town"
            elif result["type"] == "recruitment":
                # Type cast the result
                recruitment_result = cast(RecruitmentResult, result)
                self.handle_recruitment(recruitment_result["content"])

    # i still need to write an actual story, these menus are placeholder concepts only
    def town_menu(self):
        while self.current_location == "town":
            print("\n" + "="*50)
            print("TOWN")
            print("="*50)
            if self.player is None:
                print("Error: No active player")
                return

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
            if self.player is None:
                print("Error: No active player")
                return

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
        if self.player is None:
                print("Error: No active player")
                return

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
        if self.player is None:
            print("Error: No active player")
            return

        max_health = self.player.max_health
        if max_health is not None:
            self.player.stats["Health"] = max_health

        if hasattr(self.player, "current_mana") and hasattr(self.player, "max_mana"):
            self.player.current_mana = self.player.max_mana

        print("HP and Mana restored!")
        time.sleep(1)

    def start_combat(self):
        if self.player is None:
            print("Error: No active player")
            return
        
        enemy_party = Party("enemy")
        enemy = Enemy("Goblin", self.player.level)
        enemy_party.add_member(enemy)
        combat = Combat(self.player_party, enemy_party)
        result = self.handle_combat(combat)

        if result:
            print("\nVictory!")
        else:
            print("\nDefeat!")
            self.current_location = "town"

    def start_boss_combat(self):
        if self.player is None:
            print("Error: No active player")
            return

        enemy_party = Party("enemy")
        enemy = Boss("Dragon", self.player.level, self.player_party)
        enemy_party.add_member(enemy)
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

    def check_recruitment_requirements(self, requirements: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
        if not requirements:
            return True, ""

        if self.player is None or self.player_party is None:
            return False, "No active player or party"

        if "min_level" in requirements:
            if self.player.level < requirements["min_level"]:
                return False, f"You must be at least level {requirements['min_level']}"

        if "max_party_size" in requirements:
            if len(self.player_party.members) >= requirements["max_party_size"]:
                return False, "Your party is full"

        if "class_not_in_party" in requirements:
            for member in self.player_party.members:
                if (hasattr(member, 'player_class') and
                    member.player_class == requirements["class_not_in_party"] or
                    hasattr(member, 'npc_class') and
                    member.npc_class == requirements["class_not_in_party"]):
                    return False, f"You already have a {requirements['class_not_in_party']} in your party"

        if "items_required" in requirements:
            for item_name in requirements["items_required"]:
                if self.player.inventory.get_item_count(item_name) <= 0:
                    return False, f"You need a {item_name} to recruit this character"

        return True, ""
    
    def handle_recruitment_consequences(self, consequences: Optional[Dict[str, Any]], accepted: bool) -> None:
        if not consequences:
            return

        if self.player is None or self.player_party is None:
            return

        consequence_type = "accept" if accepted else "reject"
        if consequence_type not in consequences:
            return

        result = consequences[consequence_type]

        if "items_gained" in result:
            for item in result["items_gained"]:
                success, message = self.player.inventory.add_item(
                        item["name"],
                        item["quantity"]
                        )
                if success:
                    print(f"\nReceived {item['quantity']} {item['name']}(s)")
                else:
                    print(f"\nCouldn't receive {item['name']}: {message}")

        if "items_consumed" in result:
            for item in result["items_consumed"]:
                success, message = self.player.inventory.remove_item(
                        item["name"],
                        item["quantity"]
                        )
                if not success:
                    print(f"\nWarning: Couldn't consume {item['name']}: {message}")

        if "reputation_change" in result:
            change = result["reputation_change"]
            print(f"\nReputation {'increased' if change > 0 else 'decreased'}")

    def handle_recruitment(self, content: Optional[Dict[str, Any]]) -> bool:
        if not content or 'npc_class' not in content:
            print("Error: Invalid recruitment content")
            return False

        if self.player is None or self.player_party is None:
            print("Error: No active player or party")
            return False

        print(f"\n{content.get('description', 'You encounter a potential ally.')}")

        if len(self.player_party.members) >= 4:
            print("\nYour party is already full!")
            return False

        if 'requirements' in content:
            meets_requirements, failure_reason = self.check_recruitment_requirements(content['requirements'])
            if not meets_requirements:
                print(f"\n{failure_reason}")
                self.story.current_node = self.story.nodes[content['next_node_reject']]
                return False

        while True:
            choice = input("\nWould you like them to join your party? (y/n): ").lower()
            if choice in ('y', 'n'):
                break
            print("Please enter 'y' or 'n'")

        if choice == 'y':
            try:
                new_npc = NPC(content['npc_class'], self.player.level)
                self.player_party.add_member(new_npc)
                print(f"\nThe {content['npc_class']} has joined your party!")

                if 'consequences' in content:
                    self.handle_recruitment_consequences(content['consequences'], accepted=True)

                self.story.current_node = self.story.nodes[content['next_node_accept']]
                return True
            except Exception as e:
                print(f"\nError recruiting NPC: {e}")
                self.story.current_node = self.story.nodes[content['next_node_reject']]
                return False
        else:
            print("\nYou decide not to recruit them")
            if 'consequences' in content:
                self.handle_recruitment_consequences(content['consequences'], accepted=False)
            self.story.current_node = self.story.nodes[content['next_node_reject']]
            return False

if __name__ == "__main__":
    game = Game()
    game.main_menu()
