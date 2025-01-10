import os
import sys
import unittest
from unittest.mock import Mock, patch
import time
import json
from pathlib import Path

test_dir = Path(__file__).parent
project_dir = test_dir.parent
sys.path.append(str(project_dir))

from base_classes import GameEntity
from characters import (
        Player, NPC, Enemy, Boss, Spell, Inventory,
        initialize_common_items, initialize_mage_spells, initialize_healer_spells
        )
from combat import Combat
from tree import StoryTree, create_story, StoryNode, StoryChoice, handle_story_progression
from story_content import get_story_content
from game_loop import Game
from party import Party
from save_states import GameSave
from key_press import KeyboardInput

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.player = Player("Warrior")
        self.inventory = self.player.inventory

    def test_inventory_initialization(self):
        self.assertIn("Health Potion", self.inventory.items)
        self.assertEqual(self.inventory.get_item_count("Health Potion"), 3)

    def test_inventory_size_limit(self):
        self.inventory.items.clear()

        for i in range(self.inventory.max_size):
            item_name = f"Test Item {i}"
            success, _ = self.inventory.add_item(item_name)
            self.assertTrue(success)

        success, message = self.inventory.add_item("Extra Item")
        self.assertFalse(success)
        self.assertIn("full", message.lower())

    def test_item_usage(self):
        initial_health = self.player.stats["Health"]
        self.player.stats["Health"] = initial_health // 2
        success, message = self.player.use_item("Health Potion")
        self.assertTrue(success)
        self.assertGreater(self.player.stats["Health"], initial_health // 2)

        success, message = self.player.use_item("Nonexistent Item")
        self.assertFalse(success)
        self.assertIn("Invalid", message)

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
        
    def test_inventory_integration(self):
        player = Player("Warrior")
        mage = Player("Mage")
        
        self.assertIsNotNone(player.inventory)
        self.assertIsNotNone(player.available_items)
        self.assertEqual(player.inventory.get_item_count("Health Potion"), 3)

        self.assertEqual(mage.inventory.get_item_count("Mana Potion"), 2)

        success, _ = player.inventory.add_item("Strength Elixir")
        self.assertTrue(success)

        initial_strength = player.stats["Strength"]
        success, _ = player.use_item("Strength Elixir")
        self.assertTrue(success)
        self.assertGreater(player.stats["Strength"], initial_strength)

        player.update_buffs()
        self.assertEqual(player.stats["Strength"], initial_strength)

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

        with patch('random.randint') as mock_rand:
            mock_rand.side_effect = [20, 10, 5]
            combat.setup_initiative()

        self.assertEqual(len(combat.initiative_order), 3)

        first_actor = combat.get_active_combatant()

        combat.handle_initiative()
        combat.current_turn_index = (combat.current_turn_index + 1) % len(combat.initiative_order)

        second_actor = combat.get_active_combatant()

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
            self.assertFalse(combat.player_party.is_party_alive())
            result = combat.attack(0)
        self.assertEqual(result, "DEFEAT")

    def test_combat_actions(self):
        self.player_party.add_member(self.player)
        self.enemy_party.add_member(self.enemy)
        combat = Combat(self.player_party, self.enemy_party)

        mage = Player("Mage")
        self.player_party.add_member(mage)
        spells = combat.get_available_spells(mage)
        self.assertTrue(len(spells) > 0)
        spell_name = list(spells.keys())[0]
        result = combat.cast_spell(mage, spell_name, self.enemy)
        self.assertTrue(result.startswith("Spell hit") or result.startswith("DEFEAT"))

        with patch('random.randint', return_value=25):
            combat.is_player_turn = True
            result = combat.handle_combat_action(mage, "flee")
            self.assertEqual(result, "FLED")

        with patch('random.randint', side_effect=[75,
                                                  75,
                                                  20,
                                                  5]):
            combat.is_player_turn = True
            result = combat.handle_combat_action(mage, "flee")
            self.assertEqual(result, "FAILED_FLEE")

            result = combat.handle_combat_action(mage, "attack", target_index=0)
            self.assertTrue(result.startswith("HIT_") or
                            result == "VICTORY" or
                            result == "DEFEAT")
            
    def test_item_usage_in_combat(self):
        player = Player("Warrior")
        enemy = Enemy("Goblin", 1)
        player_party = Party("player")
        enemy_party = Party("enemy")

        player_party.add_member(player)
        enemy_party.add_member(enemy)

        combat = Combat(player_party, enemy_party)

        initial_health = player.stats["Health"]
        player.stats["Health"] = initial_health // 2

        with patch('builtins.input', return_value='1'):
            result = combat.handle_combat_action(player, "use_item", target_index=None, item_name="Health Potion")

        self.assertTrue(result.startswith("ITEM_USED_"))
        self.assertGreater(player.stats["Health"], initial_health // 2)
        
    def test_spell_casting(self):
        mage = Player("Mage")
        enemy = Enemy("Goblin", 1)

        combat = Combat(self.player_party, self.enemy_party)

        spells = combat.get_available_spells(mage)
        self.assertTrue(len(spells) > 0)

        spell_name = list(spells.keys())[0]
        initial_mana = mage.current_mana
        result = combat.cast_spell(mage, spell_name, enemy)

        self.assertLess(mage.current_mana, initial_mana)
        self.assertTrue(result.startswith("Spell hit") or result.startswith("DEFEAT"))

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

class TestRecruitment(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        with patch('builtins.input', return_value='1'):
            self.game.start_new_game()

        self.test_recruitment_content = {
                "npc_class": "Healer",
                "name": "Elena",
                "description": "Test description",
                "requirements": {
                    "min_level": 2,
                    "max_party_size": 3,
                    "class_not_in_party": "Healer",
                    "items_required": ["Health Potion"]
                    },
                "consequences": {
                    "accept": {
                        "items_gained": [
                            {"name": "Healing Staff", "quantity": 1},
                            {"name": "Mana Potion", "quantity": 2}
                            ],
                        "items_consumed": [
                            {"name": "Health Potion", "quantity": 1}
                            ]
                        },
                    "reject": {
                        "reputation_change": -5
                        }
                    },
                "next_node_accept": "village_square",
                "next_node_reject": "forest_entrance",
                }

    def test_recruitment_requirements(self):
        # test level requirement
        meets_req, reason = self.game.check_recruitment_requirements(
                {"min_level": 3}
                )
        self.assertFalse(meets_req)
        self.assertIn("level", reason.lower())
        # test max party size
        meets_req, reason = self.game.check_recruitment_requirements(
                {"max_party_size": 4}
                )
        self.assertTrue(meets_req)
        # test class restriction
        npc = NPC("Healer", self.game.player.level)
        self.game.player_party.add_member(npc)
        meets_req, reason = self.game.check_recruitment_requirements(
                {"class_not_in_party": "Healer"}
                )
        self.assertFalse(meets_req)
        self.assertIn("already have", reason.lower())

    def test_recruitment_consequences(self):
        # test item gains
        initial_count = self.game.player.inventory.get_item_count("Health Potion")
        consequences = {
                "accept": {
                    "items_gained": [
                        {"name": "Health Potion", "quantity": 1}
                        ]
                    }
                }
        self.game.handle_recruitment_consequences(consequences, accepted=True)
        new_count = self.game.player.inventory.get_item_count("Health Potion")
        self.assertEqual(new_count, initial_count + 1)

        # test item consumption
        consequences = {
                "accept": {
                    "items_consumed": [
                        {"name": "Health Potion", "quantity": 1}
                        ]
                    }
                }
        initial_count = self.game.player.inventory.get_item_count("Health Potion")
        self.game.handle_recruitment_consequences(consequences, accepted=True)
        new_count = self.game.player.inventory.get_item_count("Health Potion")
        self.assertEqual(new_count, initial_count - 1)

    def test_full_recruitment_flow(self):
        self.game.story.nodes["test_recruit"] = StoryNode("test_recruit", "recruitment")
        self.game.story.nodes["test_recruit"].content = self.test_recruitment_content
        self.game.story.nodes["village_square"] = StoryNode("village_square", "narrative")
        self.game.story.nodes["forest_entrance"] = StoryNode("forest_entrance", "narrative")
        self.game.story.current_node = self.game.story.nodes["test_recruit"]
        # level player to meet requirements
        self.game.player.level = 2

        print(f"\nCurrent player level: {self.game.player.level}")
        print(f"Required level: {self.test_recruitment_content['requirements']['min_level']}")
        print(f"Current party size: {len(self.game.player_party.members)}")
        print(f"Max party size: {self.test_recruitment_content['requirements']['max_party_size']}")
        print(f"Health Potions: {self.game.player.inventory.get_item_count('Health Potion')}")

        if self.game.player.inventory.get_item_count("Health Potion") == 0:
            self.game.player.inventory.add_item("Health Potion", 1)
            print("Added Health Potion to inventory")

        current_node = self.game.story.current_node
        print(f"Current node type: {current_node.node_type}")
        print(f"Current node content: {current_node.content}")

        with patch('builtins.input', return_value='y'):
            result = self.game.handle_recruitment(self.test_recruitment_content)
            print(f"Recruitment result: {result}")

            self.assertTrue(result)
            self.assertEqual(len(self.game.player_party.members), 2)
            self.assertTrue(any(
                isinstance(member, NPC) and member.npc_class == "Healer"
                for member in self.game.player_party.members
                ))

        self.game = Game()
        with patch('builtins.input', return_value='1'):
            self.game.start_new_game()
            self.game.player.level = 2
            self.game.story.nodes["test_recruit"] = StoryNode("test_recruit", "recruitment")
            self.game.story.nodes["village_square"] = StoryNode("village_square", "narrative")
            self.game.story.nodes["forest_entrance"] = StoryNode("forest_entrance", "narrative")
            self.game.story.current_node = self.game.story.nodes["test_recruit"]

        with patch('builtins.input', return_value='n'):
            result = self.game.handle_recruitment(self.test_recruitment_content)
            self.assertFalse(result)

class TestStory(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        with patch('builtins.input', return_value='1'):
            self.game.start_new_game()

        self.test_story_content = {
            "start": {
                "type": "narrative",
                "content": {
                    "text": "Test start",
                    "description": "Test description"
                },
                "choices": [
                    {
                        "id": "choice_solo",
                        "text": "Go alone",
                        "next_node": "solo_path",
                        "requirements": {"party_size": {"max": 1}}
                    },
                    {
                        "id": "choice_recruit",
                        "text": "Seek allies",
                        "next_node": "village_healer",
                        "requirements": {"party_size": {"max": 3}}
                    }
                ]
            },
            "village_healer": {
                "type": "recruitment",
                "content": {
                    "npc_class": "Healer",
                    "name": "Elena",
                    "description": "Test recruitment",
                    "requirements": {
                        "min_level": 2,
                        "max_party_size": 3
                    },
                    "next_node_accept": "village_square",
                    "next_node_reject": "forest_entrance"
                }
            }
        }

        self.game.story.nodes["village_square"] = StoryNode("village_square", "narrative")
        self.game.story.nodes["forest_entrance"] = StoryNode("forest_entrance", "narrative")

        with patch('story_content.get_story_content', return_value=self.test_story_content):
            self.story = create_story()

        self.player_party = Party("player")
        self.player_party.add_member(Player("Warrior"))
        
    def test_recruitment_node_handling(self):
        self.story.current_node = self.story.nodes["village_healer"]
        result = handle_story_progression(self.story, self.player_party)

        self.assertEqual(result["type"], "recruitment")
        self.assertEqual(result["content"]["npc_class"], "Healer")
        self.assertTrue("requirements" in result["content"])
        
    def test_story_creation(self):
        self.assertIn("start", self.story.nodes)
        self.assertIn("solo_path", self.story.nodes)
        
        # Verify exact content matches
        start_node = self.story.nodes["start"]
        self.assertEqual(start_node.content["text"], "You stand at the entrance of the ancient forest...")
        self.assertEqual(start_node.content["description"], "A peaceful morning greets you...")
        self.assertEqual(len(start_node.choices), 2)

    def test_story_navigation(self):
        test_party = Party("player")
        test_party.add_member(Player("Warrior"))
        
        self.story.start_story("start")
        available_choices = self.story.get_available_choices(test_party)
        
        self.assertEqual(len(available_choices), 2)
        choice_ids = [choice.choice_id for choice in available_choices]
        self.assertIn("choice_solo", choice_ids)
        self.assertIn("choice_village", choice_ids)

class TestGame(unittest.TestCase):
    def setUp(self):
        test_story_content = {
                "start": {
                    "type": "narrative",
                    "content": {
                        "text": "Test game start",
                        "description": "Test game"
                        },
                    "choices": []
                    }
                }
        with patch('story_content.get_story_content', return_value=test_story_content):
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
        self.game.player.experience = 0

        with patch('builtins.input', side_effect=['2', '1']):
            loaded = self.game.load_game()
            self.assertTrue(loaded)
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
        self.assertEqual(self.game.story.current_node.node_id, "start")
        # test choice availability
        choices = self.game.story.get_available_choices(self.game.player_party)
        self.assertIsNotNone(choices)

if __name__ == '__main__':
    unittest.main(verbosity=2) # increased verbosity for more detailed output
