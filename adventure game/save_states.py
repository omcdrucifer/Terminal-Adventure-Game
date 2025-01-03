# save system
from typing import Optional, Dict, Any
import json
from characters import Player
import os
from datetime import datetime

class GameSave:
    def __init__(self, save_directory="saves"):
        self.save_directory = save_directory
        self.max_slots = 5
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

    def save_game(self, player: Optional['Player'], current_location: str = "town", slot: Optional[int] = None, auto_save: bool = False) -> str:
        if player is None:
            raise ValueError("Cannot save game without a player")
        # save to a JSON
        save_data = {
                "player": {
                    "class": player.player_class,
                    "level": player.level,
                    "experience": player.experience,
                    "stats": player.stats,
                    "current_mana": getattr(player, 'current_mana', 0),
                    "max_mana": getattr(player, 'max_mana', 0)
                    },
                "location": current_location,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        if auto_save:
            filename = "autosave.json"
        elif slot is not None:
            if slot > self.max_slots:
                raise ValueError(f"Save slot cannot exceed {self.max_slots}")
            filename = f"save_slot_{slot}.json"
        else:
            filename = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.save_directory, filename)
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=4)
        return filepath  
        
    def load_game(self, filename):
        # load from JSON
        filepath = os.path.join(self.save_directory, filename)
        try:
            with open(filepath, 'r') as f:
                save_data = json.load(f)
            return save_data
        except FileNotFoundError:
            return None

    def list_saves(self):
        saves = []
        for filename in os.listdir(self.save_directory):
            if filename.endswith('.json'):
                filepath = os.path.join(self.save_directory, filename)
                with open(filepath, 'r') as f:
                    save_data = json.load(f)
                saves.append({
                    "filename": filename,
                    "timestamp": save_data["timestamp"],
                    "player_class": save_data["player"]["class"],
                    "player_level": save_data["player"]["level"],
                    "location": save_data["location"]
                    })
        return saves

    def handle_save_menu(self, player: Optional[Player], current_location: Optional[str]) -> Optional[Dict[str, Any]]:
        while True:
            print("\nSave Game Menu:")
            print("1. Create New Save")
            print("2. Load Save")
            print("3. List Saves")
            print("4. Return to Game")

            choice = input("\nEnter your choice (1-4): ")
            if choice == "1":
                if player is None:
                    print("\nNo active game to save!")
                    continue
                if current_location is None:
                    current_location = "town"
                filepath = self.save_game(player, current_location)
                print(f"\nGame saved successfully to {filepath}")
                return None
            elif choice == "2":
                saves = self.list_saves()
                if not saves:
                    print("\nNo save files found!")
                    continue
                print("\nAvailable Saves:")
                for i, save in enumerate(saves, 1):
                    print(f"{i}. {save['timestamp']} - Level {save['player_level']} {save['player_class']}")
                try:
                    save_choice = int(input("\nEnter save number to load (0 to cancel): "))
                    if save_choice == 0:
                        continue
                    if 1 <= save_choice <= len(saves):
                        save_data = self.load_game(saves[save_choice-1]["filename"])
                        return save_data
                    print("\nInvalid save number!")
                except ValueError:
                    print("\nPlease enter a valid number!")
            elif choice == "3":
                saves = self.list_saves()
                if not saves:
                    print("\nNo save files found!")
                    continue
                print("\nAvailable Saves:")
                for i, save in enumerate(saves, 1):
                    print(f"Save {i}:")
                    print(f"Timestamp: {save['timestamp']}")
                    print(f"Character: Level {save['player_level']} {save['player_class']}")
                    print(f"Location: {save['location']}")
            elif choice == "4":
                return None
            else:
                print("\nInvalid choice!")
