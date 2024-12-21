import unittest
from unittest.mock import Mock, patch
import time
import os
import json
from base_classes import GameEntity
from characters import (
        Player, NPC, Enemy, Boss, Spell,
        initialize_mage_spells, initialize_healer_spells
        )
from party import Party
from combat import Combat 
from tree import (
        StoryNode, StoryChoice, StoryTree,
        create_example_story, handle_story_progression
        )
from game_loop import Game
from save_states import GameSave
from key_press import KeyboardInput

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.valid_classes = ["Warrior", "Mage", "Archer"]
        self.players = {class_name: Player(class_name) for class_name in self.valid_classes}

    def test_invalid_class(self):
        with self.assertRaises(ValueError):
            invalid_player = Player("InvalidClass")

    def test_stat_ranges(self):
        for player in self.players.values():
            for stat, value in player.stats.items():
                self.assertGreaterEqual(value, 0, f"Negative {stat} value found")
                if stat == "Health":
                    self.assertLessEqual(value, 200, "Health exceeds maximum")
                elif stat in ["Strength", "Magic", "Defense", "Agility"]:
                    self.assertLessEqual(value, 100, f"{stat} exceeds maximum")

    def test_experience_system(self):
        player = self.players["Warrior"]

        player.gain_experience(50)
        self.assertEqual(player.level, 1)
        self.assertEqual(player.experience, 50)

        player.gain_experience(50)
        self.assertEqual(player.level, 2)
        self.assertEqual(player.experience, 0)

        player.gain_experience(200)
        self.assertEqual(player.level, 3)
        self.assertTrue(player.experience > 0)

    def test_mana_system_edge_cases(self):
        mage = self.players["Mage"]

        self.assertGreater(mage.max_mana, 0)
        self.assertEqual(mage.current_mana, mage.max_mana)

        initial_max_mana = mage.max_mana
        mage.gain_experience(100)
        self.assertGreater(mage.max_mana, initial_max_mana)

class TestCombat(unittest.TestCase):
    def setUp(self):
        self.player = Player("Warrior")
        self.mage = Player("Mage")
        self.enemy = Enemy("Goblin", 1)

        mock_party = Mock()
        mock_party.members = []
        self.boss = Boss("Dragon", 1, mock_party)

        self.player_party = Party("player")
        self.enemy_party = Party("enemy")

    def test_combat_initialization_errors(self):
        wrong_party = Party("wrong_type")
        with self.assertRaises(ValueError):
            combat = Combat(wrong_party, self.enemy_party)
            
        with self.assertRaises(ValueError):
            combat = Combat(self.player_party, self.player_party)

    def test_multi_character_combat(self):
        self.player_party.add_member(self.player)
        self.player_party.add_member(self.mage)
        self.enemy_party.add_member(self.enemy)

        combat = Combat(self.player_party, self.enemy_party)

        self.assertEqual(len(combat.initiative_order), 3)

        first_actor = combat.initiative_order[0]
        combat.handle_initiative()
        second_actor = combat.initiative_order[combat.current_turn_index]
        self.assertNotEqual(id(first_actor), id(second_actor))

    def test_combat_resolution_conditions(self):
        self.player_party.add_member(self.player)
        self.enemy_party.add_member(self.enemy)
        combat = Combat(self.player_party, self.enemy_party)
        # test victory
        self.enemy.stats["Health"] = 1
        with patch('random.randint', side_effect=[75, 20, 0]):
            result = combat.attack(0)
        if result.startswith("HIT"):
            self.enemy.stats["Health"] = 0
            result = combat.attack(0)
        self.assertEqual(result, "VICTORY")
        # test defeat
        self.player.stats["Health"] = 1
        self.enemy.stats["Health"] = 100
        combat.is_player_turn = False
        with patch('random.randint', side_effect=[75, 20, 0]):
            result = combat.attack(0)
        if result.startswith("HIT"):
            self.player.stats["Health"] = 0
            result = combat.attack(0)
        self.assertEqual(result, "DEFEAT")

class TestKeyboardInput(unittest.TestCase):
    def setUp(self):
        self.keyboard = KeyboardInput()

    @unittest.skipIf(os.name != 'nt', "windows-only test")
    @patch('msvcrt.kbhit', return_value=True) # windows
    @patch('msvcrt.getch', return_value=b'M')
    def test_windows_key_input(self, mock_getch, mock_kbhit):
        key = self.keyboard.get_key()
        self.assertEqual(key, 'M')

    def test_check_for_key_timeout(self):
        start_time = time.time()
        key = self.keyboard.check_for_key(timeout=0.1)
        end_time = time.time()
        self.assertLess(end_time - start_time, 0.2) # should not take longer than timeout

class TestGameSave(unittest.TestCase):
    def setUp(self):
        self.game_save = GameSave(save_directory="test_saves")
        self.test_player = Player("Warrior")

    def tearDown(self):
        if os.path.exists("test_saves"):
            import shutil
            shutil.rmtree("test_saves")

    def test_save_creation(self):
        filepath = self.game_save.save_game(self.test_player, "town")
        self.assertTrue(os.path.exists(filepath))

    def test_multiple_save_slots(self):
        # create max num saves
        for i in range(self.game_save.max_slots):
            filepath = self.game_save.save_game(self.test_player, "town", slot=i+1)
            self.assertTrue(os.path.exists(filepath))
        # try to create one more
        with self.assertRaises(ValueError):
            self.game_save.save_game(self.test_player, "town", slot=self.game_save.max_slots + 1)

    def test_auto_save(self):
        filepath = self.game_save.save_game(
                self.test_player,
                "dungeon",
                auto_save=True
                )
        self.assertTrue(os.path.exists(filepath))
        basename = os.path.basename(filepath)
        self.assertEqual(basename, "autosave.json")

    def test_save_load_data_integrity(self):
        # save game
        filepath = self.game_save.save_game(self.test_player, "town", slot=1)
        # modify player
        original_level = self.test_player.level
        self.test_player.level += 1
        # load game
        save_data = self.game_save.load_game("save_slot_1.json")
        # verify data
        self.assertEqual(save_data["player"]["level"], original_level)

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def test_game_initialization(self):
        required_attributes = ['player', 'player_party', 'current_location', 'story']
        for attr in required_attributes:
            self.assertTrue(hasattr(self.game, attr), f"Game missing required attribute: {attr}")

    def test_save_load_system(self):
        # start new game
        with patch('builtins.input', return_value='1'):
            self.game.start_new_game()
        self.game.player.gain_experience(50)
        original_xp = self.game.player.experience

        self.game.game_save.save_game(self.game.player, "town")
        with patch('builtins.input', return_value=1):
            self.game.player = Player("Warrior")
        self.game.player.experience = original_xp

        with patch('builtins.input', side_effect=['2', '1']):
            self.game.load_game()
        self.assertEqual(self.game.player.experience, original_xp)

    @patch('builtins.input', side_effect=['5', 'invalid', '1']) # test invalid inputs before valid
    def test_input_validation(self, mock_input):
        self.game.start_new_game() # should handle invalid inputs and eventually succeed
        self.assertIsNotNone(self.game.player)
        self.assertEqual(self.game.player.player_class, "Warrior")

    def test_story_integration(self):
        with patch('builtins.input', return_value='1'):
            self.game.start_new_game()
        # verify story initialized
        self.assertIsNotNone(self.game.story.current_node)
        # test choice availability
        choices = self.game.story.get_available_choices(self.game.player_party)
        self.assertGreater(len(choices), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2) # increased verbosity for more detailed output
