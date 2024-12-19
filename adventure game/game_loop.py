# Game flow control
import math
import random
from characters import Player, NPC, Enemy, Boss, Spell
from party import Party
from combat import Combat, Spell
from Story import StoryNode, StoryChoice, StoryTree, handle_story_progression, create_example_story # these are filler for now

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
