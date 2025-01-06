# write a revised test after clearing lsp errors
import pytest
import os
import json
from game_loop import Game
from save_states import GameSave
from key_press import KeyboardInput
from combat import Combat 
from tree import StoryNode, StoryChoice, StoryTree, create_story, handle_story_progression
from characters import Spell, Item, Inventory, Player, NPC, Enemy, Boss
from base_classes import GameEntity
from party import Party
import tempfile
import shutil

class TestGameEntity:
    def test_game_entity_initialization(self):
        entity = GameEntity()
        assert isinstance(entity, GameEntity)
        assert entity.level == 1
        assert isinstance(entity.stats, dict)
        assert len(entity.stats) == 5

        expected_stats = {
            "Strength": 0,
            "Health": 0,
            "Defense": 0,
            "Magic": 0,
            "Agility": 0
        }
        assert entity.stats == expected_stats

    def test_game_entity_stats_modification(self):
        entity = GameEntity()
        entity.stats["Strength"] = 10
        assert entity.stats["Strength"] == 10

        entity.stats["Health"] = 100
        assert entity.stats["Health"] == 100

    def test_game_entity_level_modification(self):
        entity = GameEntity()
        entity.level = 5
        assert entity.level == 5

    def test_game_entity_invalid_stat_access(self):
        entity = GameEntity()
        with pytest.raises(KeyError):
            _ = entity.stats["InvalidStat"]

    def test_game_entity_stats_independence(self):
        entity1 = GameEntity()
        entity2 = GameEntity()

        entity1.stats["Strength"] = 20
        assert entity2.stats["Strength"] == 0

        entity2.stats["Health"] = 50
        assert entity1.stats["Health"] == 0

    def test_game_entity_negative_stats(self):
        entity = GameEntity()
        entity.stats["Strength"] = -10
        assert entity.stats["Strength"] == -10

    def test_game_entity_zero_level(self):
        entity = GameEntity()
        entity.level = 0
        assert entity.level == 0

    def test_game_entity_large_numbers(self):
        entity = GameEntity()
        large_number = 1000000
        entity.stats["Health"] = large_number
        assert entity.stats["Health"] == large_number

    def test_game_entity_stat_deletion(self):
        entity = GameEntity()
        entity.stats = entity.stats.copy()
        with pytest.raises(KeyError):
            del entity.stats["NonexistentStat"]

class TestSpell:
    def setup_method(self):
        self.basic_spell = Spell("Test Spell", 10, 20, 0.5)
        self.test_caster = Player("Mage")
        self.test_caster.current_mana = 100

    def test_spell_initialization(self):
        assert self.basic_spell.name == "Test Spell"
        assert self.basic_spell.mana_cost == 10
        assert self.basic_spell.base_damage == 20
        assert self.basic_spell.scaling_factor == 0.5

    def test_spell_can_cast_with_sufficient_mana(self):
        assert self.basic_spell.can_cast(self.test_caster) == True

    def test_spell_cannot_cast_with_insufficient_mana(self):
        self.test_caster.current_mana = 5
        assert self.basic_spell.can_cast(self.test_caster) == False

    def test_spell_cannot_cast_without_mana_attribute(self):
        entity_without_mana = Player("Warrior")
        assert self.basic_spell.can_cast(entity_without_mana) == False

class TestItem:
    def setup_method(self):
        self.health_potion = Item(
            name="Health Potion",
            effect_type="heal",
            effect_value=50,
            description="Restores 50 HP",
            use_text="drinks the health potion and recovers {value} HP!"
        )

    def test_item_initialization(self):
        assert self.health_potion.name == "Health Potion"
        assert self.health_potion.effect_type == "heal"
        assert self.health_potion.effect_value == 50
        assert self.health_potion.description == "Restores 50 HP"
        assert "drinks the health potion" in self.health_potion.use_text

    def test_item_use_text_formatting(self):
        formatted_text = self.health_potion.use_text.format(value=50)
        assert formatted_text == "drinks the health potion and recovers 50 HP!"

class TestInventory:
    def setup_method(self):
        self.warrior = Player("Warrior")
        self.inventory = Inventory(max_size=20, owner=self.warrior)
        self.common_items = {
            "Health Potion": Item(
                name="Health Potion",
                effect_type="heal",
                effect_value=50,
                description="Restores 50 HP",
                use_text="drinks the health potion and recovers {value} HP!"
            )
        }

    def test_inventory_initialization(self):
        assert self.inventory.max_size == 20
        assert isinstance(self.inventory.items, dict)
        assert "Health Potion" in self.inventory.items
        assert self.inventory.items["Health Potion"] == 3

    def test_inventory_add_item_success(self):
        success, message = self.inventory.add_item("Health Potion", 2)
        assert success == True
        assert self.inventory.items["Health Potion"] == 5
        assert "Added 2" in message

    def test_inventory_add_item_full(self):
        for i in range(20):
            self.inventory.add_item(f"Test Item {i}")
        success, message = self.inventory.add_item("New Item")
        assert success == False
        assert "full" in message.lower()

    def test_inventory_remove_item_success(self):
        self.inventory.items["Health Potion"] = 5
        success, message = self.inventory.remove_item("Health Potion", 2)
        assert success == True
        assert self.inventory.items["Health Potion"] == 3
        assert "Removed 2" in message

    def test_inventory_remove_item_not_enough(self):
        self.inventory.items["Health Potion"] = 1
        success, message = self.inventory.remove_item("Health Potion", 2)
        assert success == False
        assert "Not enough" in message

    def test_inventory_remove_nonexistent_item(self):
        success, message = self.inventory.remove_item("Nonexistent Item")
        assert success == False
        assert "not in inventory" in message.lower()

    def test_inventory_get_item_count(self):
        self.inventory.items["Health Potion"] = 5
        assert self.inventory.get_item_count("Health Potion") == 5
        assert self.inventory.get_item_count("Nonexistent Item") == 0

    def test_inventory_mage_initialization(self):
        mage = Player("Mage")
        mage_inventory = Inventory(max_size=20, owner=mage)
        assert "Mana Potion" in mage_inventory.items
        assert mage_inventory.items["Mana Potion"] == 2

class TestPlayer:
    def setup_method(self):
        self.warrior = Player("Warrior")
        self.mage = Player("Mage")
        self.archer = Player("Archer")

    def test_player_invalid_class(self):
        with pytest.raises(ValueError) as exc_info:
            Player("InvalidClass")
        assert "Invalid class" in str(exc_info.value)

    def test_player_initial_stats(self):
        assert self.warrior.stats["Strength"] == 20
        assert self.warrior.stats["Health"] == 100
        assert self.warrior.stats["Defense"] == 15

        assert self.mage.stats["Magic"] == 30
        assert self.mage.stats["Health"] == 60
        assert self.mage.current_mana == self.mage.max_mana

        assert self.archer.stats["Agility"] == 25
        assert self.archer.stats["Health"] == 80
        assert self.archer.stats["Defense"] == 10

    def test_player_level_up_stats(self):
        initial_health = self.warrior.stats["Health"]
        initial_strength = self.warrior.stats["Strength"]

        self.warrior.gain_experience(100)
        assert self.warrior.level == 2
        assert self.warrior.stats["Health"] > initial_health
        assert self.warrior.stats["Strength"] > initial_strength

    def test_player_experience_system(self):
        assert self.warrior.experience == 0
        assert self.warrior.experience_to_next_level == 100

        self.warrior.gain_experience(50)
        assert self.warrior.experience == 50
        assert self.warrior.level == 1

        self.warrior.gain_experience(50)
        assert self.warrior.level == 2
        assert self.warrior.experience == 0
        assert self.warrior.experience_to_next_level == 150

    def test_mage_spell_system(self):
        assert hasattr(self.mage, "spells")
        assert "Fireball" in self.mage.spells
        assert "Ice Shard" in self.mage.spells
        assert "Lightning Bolt" in self.mage.spells

        initial_mana = self.mage.current_mana
        self.mage.current_mana = 0
        assert all(not spell.can_cast(self.mage) for spell in self.mage.spells.values())

        self.mage.current_mana = initial_mana
        assert all(spell.can_cast(self.mage) for spell in self.mage.spells.values())

    def test_max_health_property(self):
        assert self.warrior.max_health == 100
        assert self.mage.max_health == 60
        assert self.archer.max_health == 80

        self.warrior.level = 2
        self.mage.level = 2
        self.archer.level = 2

        assert self.warrior.max_health == 120
        assert self.mage.max_health == 70
        assert self.archer.max_health == 95

    def test_use_item_mechanics(self):
        self.warrior.stats["Health"] = 50
        health_before = self.warrior.stats["Health"]

        success, message = self.warrior.use_item("Health Potion")
        assert success == True
        assert self.warrior.stats["Health"] > health_before
        assert "recovers" in message

        success, message = self.warrior.use_item("Invalid Item")
        assert success == False
        assert "Invalid item" in message

class TestNPC:
    def setup_method(self):
        self.healer = NPC("Healer", player_level=1)
        self.fighter = NPC("Fighter", player_level=1)

    def test_npc_initialization(self):
        assert self.healer.level == 1
        assert self.fighter.level == 1

        assert hasattr(self.healer, "spells")
        assert self.healer.spells is not None
        assert hasattr(self.fighter, "spells")
        assert self.fighter.spells is None

    def test_npc_stat_scaling(self):
        fighter_initial_health = self.fighter.stats["Health"]
        healer_initial_magic = self.healer.stats["Magic"]

        self.fighter.level = 2
        self.fighter.update_stats()
        self.healer.level = 2
        self.healer.update_stats()

        assert self.fighter.stats["Health"] > fighter_initial_health
        assert self.healer.stats["Magic"] > healer_initial_magic

    def test_healer_spells(self):
        assert hasattr(self.healer, "spells")
        assert isinstance(self.healer.spells, dict)

        expected_spells = ["Heal", "Blessing", "Smite"]
        for spell in expected_spells:
            assert spell in self.healer.spells, f"Spell {spell} not found in healer's spells"

    def test_fighter_no_spells(self):
        assert self.fighter.spells is None

        assert self.fighter.current_mana == 0
        assert self.fighter.max_mana == 0

    def test_healer_mana_increase(self):
        initial_max_mana = self.healer.max_mana
        initial_current_mana = self.healer.current_mana

        self.healer.level = 2
        self.healer.update_stats()

        assert self.healer.max_mana > initial_max_mana
        assert self.healer.current_mana == self.healer.max_mana
        assert self.healer.current_mana > initial_current_mana        

class TestEnemy:
    def setup_method(self):
        self.goblin = Enemy("Goblin", player_level=1)
        self.ogre = Enemy("Ogre", player_level=1)

    def test_enemy_initialization(self):
        assert self.goblin.level == 1
        assert self.ogre.level == 1

        assert self.goblin.experience_value > 0
        assert self.ogre.experience_value > 0

    def test_enemy_level_scaling(self):
        high_level_ogre = Enemy("Ogre", player_level=5)
        assert high_level_ogre.level == 5
        assert high_level_ogre.stats["Health"] > self.ogre.stats["Health"]
        assert high_level_ogre.experience_value > self.ogre.experience_value

    def test_enemy_level_restrictions(self):
        low_level_enemy = Enemy("Goblin", player_level=2)
        assert low_level_enemy.level == 1

        mid_level_enemy = Enemy("Goblin", player_level=3)
        assert mid_level_enemy.level == 2

class TestBoss:
    def setup_method(self):
        self.test_party = Party("player")
        self.test_party.add_member(Player("Warrior"))
        self.dragon = Boss("Dragon", player_level=5, player_party=self.test_party)

    def test_boss_initialization(self):
        assert self.dragon.level > 5
        assert self.dragon.experience_value > 0

    def test_boss_party_size_scaling(self):
        small_party_boss = Boss("Dragon", player_level=5, player_party=self.test_party)

        self.test_party.add_member(NPC("Healer", 5))
        large_party_boss = Boss("Dragon", player_level=5, player_party=self.test_party)

        assert large_party_boss.level > small_party_boss.level
        assert large_party_boss.stats["Health"] > small_party_boss.stats["Health"]

    def test_boss_types(self):
        troll = Boss("Troll", player_level=5, player_party=self.test_party)
        giant = Boss("Giant", player_level=5, player_party=self.test_party)

        assert troll.stats["Health"] != giant.stats["Health"]
        assert troll.experience_value != giant.experience_value

class TestCombat:
    def setup_method(self):
        self.game = Game()
        self.player = Player("Warrior")
        self.player_party = Party("player")
        self.player_party.add_member(self.player)

        self.enemy = Enemy("Goblin", player_level=1)
        self.enemy_party = Party("enemy")
        self.enemy_party.add_member(self.enemy)

        self.combat = Combat(self.player_party, self.enemy_party)

    def test_combat_initialization(self):
        assert isinstance(self.combat.player_party, Party)
        assert isinstance(self.combat.enemy_party, Party)
        assert len(self.combat.initiative_order) > 0
        assert self.combat.current_turn_index == 0
        assert isinstance(self.combat.is_player_turn, bool)

    def test_invalid_combat_initialization(self):
        invalid_party = Party("player")
        with pytest.raises(ValueError) as exc_info:
            Combat(invalid_party, invalid_party)
        assert "Combat must be between a player party and enemy party" in str(exc_info.value)

    def test_initiative_system(self):
        initial_order = self.combat.initiative_order.copy()
        all_combatants = self.player_party.members + self.enemy_party.members

        assert len(initial_order) == len(all_combatants)
        assert all(hasattr(combatant, 'initiative') for combatant in initial_order)

    def test_combat_turn_handling(self, monkeypatch):
        initial_index = self.combat.current_turn_index
        initial_turn = self.combat.is_player_turn

        def mock_randint(_):
            return 1
        monkeypatch.setattr('random.randint', mock_randint)

        print(f"Initial Turn Index: {initial_index}")
        print(f"Initial Turn Flag: {initial_turn}")

        self.combat.handle_initiative()

        print(f"Updated Turn Index: {self.combat.current_turn_index}")
        print(f"Updated Turn Flag: {self.combat.is_player_turn}")

        assert self.combat.current_turn_index != initial_index

        if len(self.combat.initiative_order) > 1:
            assert self.combat.is_player_turn != initial_turn

    def test_basic_attack_mechanics(self):
        initial_enemy_health = self.enemy.stats["Health"]
        attack_result = self.combat.attack(target_index=0)

        assert attack_result in ["HIT_0", "MISS"] or attack_result.startswith("HIT_")
        if attack_result.startswith("HIT_"):
            assert self.enemy.stats["Health"] < initial_enemy_health

    def test_spell_casting_mechanics(self):
        mage = Player("Mage")
        mage_party = Party("player")
        mage_party.add_member(mage)
        spell_combat = Combat(mage_party, self.enemy_party)

        initial_enemy_health = self.enemy.stats["Health"]
        spell_result = spell_combat.cast_spell(mage, "Fireball", self.enemy)

        assert spell_result.startswith("Spell hit") or spell_result == "Invalid Spell"
        if spell_result.startswith("Spell hit"):
            assert self.enemy.stats["Health"] < initial_enemy_health

    def test_combat_victory_conditions(self, monkeypatch):
        self.enemy.stats["Health"] = 0

        def mock_random(*_):
            return 75
        monkeypatch.setattr('random.randint', mock_random)

        result = self.combat.attack()
        assert result == "VICTORY"

    def test_combat_defeat_conditions(self, monkeypatch):
        self.player.stats["Health"] = 0

        monkeypatch.setattr('random.randint', lambda _: 75)

        result = self.combat.attack()
        assert result == "DEFEAT"

    def test_combat_flee_mechanics(self):
        flee_result = self.combat.handle_combat_action(self.player, "flee")
        assert flee_result in ["FLED", "FAILED_FLEE"]

    def test_item_usage_in_combat(self, monkeypatch):
        self.player.stats["Health"] = 50
        initial_health = self.player.stats["Health"]

        inputs = iter(['1'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        result = self.combat.handle_combat_action(
                self.player,
                "use_item",
                item_name="Health Potion"
                )

        assert result is not None
        assert isinstance(result, str)
        assert result.startswith("ITEM_USED") or result.startswith("ITEM_FAILED")
        if result.startswith("ITEM_USED"):
            assert self.player.stats["Health"] > initial_health
    
    def test_experience_distribution(self):
        initial_exp = self.player.experience
        self.enemy.stats["Health"] = 0

        self.combat.handle_combat_action(self.player, "attack", target_index=0)

        assert self.player.experience > initial_exp

    def test_boss_combat_mechanics(self):
        boss = Boss("Dragon", player_level=1, player_party=self.player_party)
        boss_party = Party("enemy")
        boss_party.add_member(boss)

        boss_combat = Combat(self.player_party, boss_party)

        assert boss.level >= self.player.level
        attack_result = boss_combat.attack()
        assert attack_result in ["HIT_0", "MISS"] or attack_result.startswith("HIT_")

    def test_spell_failure_conditions(self):
        mage = Player("Mage")
        mage.current_mana = 0
        mage_party = Party("player")
        mage_party.add_member(mage)

        spell_combat = Combat(mage_party, self.enemy_party)
        result = spell_combat.cast_spell(mage, "Fireball", self.enemy)

        assert "Not enough mana" in result

    def test_combat_status_reporting(self):
        player_status, enemy_status = self.combat.get_combat_status()

        assert isinstance(player_status, list)
        assert isinstance(enemy_status, list)
        assert len(player_status) == len(self.player_party.members)
        assert len(enemy_status) == len(self.enemy_party.members)

        for status in player_status + enemy_status:
            assert "Health" in status

class TestHandleCombatEncounter:
    def setup_method(self):
        self.player = Player("Warrior")
        self.player_party = Party("player")
        self.player_party.add_member(self.player)

        self.enemy = Enemy("Goblin", player_level=1)
        self.enemy_party = Party("enemy")
        self.enemy_party.add_member(self.enemy)

        self.combat = Combat(self.player_party, self.enemy_party)

    @pytest.fixture(autouse=True)
    def setup_mocks(self, monkeypatch):
        monkeypatch.setattr('random.randint', lambda a, b: (a + b) // 2)

    def test_victory_scenario(self, monkeypatch):
        self.enemy.stats["Health"] = 1
        
        inputs = iter(['1', '1'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        # Changed from handle_combat_encounter to instance method
        result = self.combat.handle_combat_encounter()
        assert result == "VICTORY"

    def test_multi_round_combat(self, monkeypatch):
        self.player.stats["Health"] = 200
        self.enemy.stats["Health"] = 200

        inputs = iter(['1', '1'] * 10)
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        result = self.combat.handle_combat_encounter()
        print(f"Combat result: {result}")
        assert result in ["VICTORY", "DEFEAT", "FLED"]

    def test_mage_combat_scenario(self, monkeypatch):
        mage = Player("Mage")
        mage_party = Party("player")
        mage_party.add_member(mage)
        mage_combat = Combat(mage_party, self.enemy_party)

        inputs = iter(['2', 'Fireball', '1'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        # Changed from handle_combat_encounter to instance method
        result = mage_combat.handle_combat_encounter()
        assert result in ["VICTORY", "DEFEAT", "FLED"]

class TestParty:
    def setup_method(self):
        self.player_party = Party("player")
        self.enemy_party = Party("enemy")
        self.warrior = Player("Warrior")
        self.goblin = Enemy("Goblin", 1)

    def test_party_initialization(self):
        assert self.player_party.party_type == "player"
        assert self.enemy_party.party_type == "enemy"
        assert len(self.player_party.members) == 0
        assert len(self.enemy_party.members) == 0

    def test_add_valid_member_to_player_party(self):
        healer = NPC("Healer", player_level=1)

        self.player_party.add_member(self.warrior)
        assert len(self.player_party.members) == 1
        assert self.warrior in self.player_party.members

        self.player_party.add_member(healer)
        assert len(self.player_party.members) == 2
        assert healer in self.player_party.members

    def test_add_valid_member_to_enemy_party(self):
        dragon = Boss("Dragon", player_level=1, player_party=self.player_party)

        self.enemy_party.add_member(self.goblin)
        assert len(self.enemy_party.members) == 1
        assert self.goblin in self.enemy_party.members

        self.enemy_party.add_member(dragon)
        assert len(self.enemy_party.members) == 2
        assert dragon in self.enemy_party.members

    def test_add_invalid_member_to_player_party(self):
        with pytest.raises(ValueError) as exc_info:
            self.player_party.add_member(self.goblin)
        assert "Can only add Player or NPC to player parties" in str(exc_info.value)

    def test_add_invalid_member_to_enemy_party(self):
        with pytest.raises(ValueError) as exc_info:
            self.enemy_party.add_member(self.warrior)
        assert "Can only add Enemy or Boss to enemy parties" in str(exc_info.value)

    def test_non_game_entity(self):
        non_entity = object()
        with pytest.raises(ValueError) as exc_info:
            self.player_party.add_member(non_entity)
        assert "Can only add game entities to parties" in str(exc_info)

    def test_remove_member(self):
        self.player_party.add_member(self.warrior)
        assert len(self.player_party.members) == 1

        self.player_party.remove_member(self.warrior)
        assert len(self.player_party.members) == 0
        assert self.warrior not in self.player_party.members

    def test_remove_nonexistent_member(self):
        self.player_party.remove_member(self.warrior)
        assert len(self.player_party.members) == 0

    def test_get_active_members(self):
        self.player_party.add_member(self.warrior)
        mage = Player("Mage")
        self.player_party.add_member(mage)

        assert len(self.player_party.get_active_members()) == 2

        self.warrior.stats["Health"] = 0
        active_members = self.player_party.get_active_members()
        assert len(active_members) == 1
        assert mage in active_members
        assert self.warrior not in active_members

    def test_is_party_alive(self):
        self.player_party.add_member(self.warrior)
        assert self.player_party.is_party_alive() == True

        self.warrior.stats["Health"] = 0 
        assert self.player_party.is_party_alive() == False

    def test_synchronize_level_player_party(self):
        healer = NPC("Healer", player_level=1)
        self.player_party.add_member(healer)

        initial_healer_level = healer.level
        self.player_party.synchronize_level(5)

        assert healer.level == 5
        assert healer.level > initial_healer_level

    def test_synchronize_level_enemy_party(self):
        dragon = Boss("Dragon", player_level=1, player_party=self.player_party)
        self.enemy_party.add_member(self.goblin)
        self.enemy_party.add_member(dragon)

        initial_goblin_level = self.goblin.level
        initial_dragon_level = dragon.level

        self.enemy_party.synchronize_level(5)

        assert self.goblin.level == 5
        assert self.goblin.level > initial_goblin_level
        assert dragon.level > initial_dragon_level

    def test_get_total_health(self):
        self.player_party.add_member(self.warrior)
        mage = Player("Mage")
        self.player_party.add_member(mage)

        total_health = self.player_party.get_total_health()
        assert total_health > 0
        assert isinstance(total_health, float)

    def test_get_party_status(self):
        self.player_party.add_member(self.warrior)
        status = self.player_party.get_party_status()

        assert isinstance(status, list)
        assert len(status) == 1
        assert isinstance(status[0], str)
        assert "Warrior" in status[0]
        assert "Health" in status[0]

    def test_mixed_level_party(self):
        healer = NPC("Healer", player_level=3)
        self.warrior.level = 5

        self.player_party.add_member(self.warrior)
        self.player_party.add_member(healer)

        status = self.player_party.get_party_status()
        assert len(status) == 2
        assert all("Health" in member_status for member_status in status)

    def test_empty_party_operations(self):
        assert self.player_party.get_total_health() == 0
        assert len(self.player_party.get_party_status()) == 0
        assert self.player_party.is_party_alive() == False
        assert len(self.player_party.get_active_members()) == 0

    def test_party_size_limits(self):
        max_size = 4
        self.player_party = Party(max_size=max_size)
        for _ in range(max_size):
            self.player_party.add_member(Player("Warrior"))

        assert len(self.player_party.members) == max_size

        with pytest.raises(ValueError) as exc_info:
            self.player_party.add_member(Player("Mage"))
        assert "Party is full" in str(exc_info.value)

class TestStoryNode:
    def setup_method(self):
        self.narrative_node = StoryNode("test_narrative", "narrative")
        self.combat_node = StoryNode("test_combat", "combat")
        self.recruitment_node = StoryNode("test_recruitment", "recruitment")

    def test_node_initialization(self):
        assert self.narrative_node.node_id == "test_narrative"
        assert self.narrative_node.node_type == "narrative"
        assert isinstance(self.narrative_node.content, dict)
        assert isinstance(self.narrative_node.choices, list)
        assert isinstance(self.narrative_node.requirements, dict)
        assert isinstance(self.narrative_node.consequences, dict)

    def test_content_modification(self):
        test_content = {
                "text": "Test narrative text",
                "description": "Test description"
                }
        self.narrative_node.content = test_content
        assert self.narrative_node.content == test_content

    def test_choice_addition(self):
        choice = StoryChoice("choice_1", "Test choice", "next_node")
        self.narrative_node.choices.append(choice)
        assert len(self.narrative_node.choices) == 1
        assert self.narrative_node.choices[0].choice_id == "choice_1"

    def test_requirements_setting(self):
        requirements = {"min_level": 5}
        self.narrative_node.requirements = requirements
        assert self.narrative_node.requirements == requirements

class TestStoryChoice:
    def setup_method(self):
        self.basic_choice = StoryChoice("choice_1", "Go to town", "town_node")
        self.choice_with_requirements = StoryChoice(
                "choice_2",
                "Enter dungeon",
                "dungeon_node",
                requirements= {"min_level": 5}
                )
    def test_choice_initialization(self):
        assert self.basic_choice.choice_id == "choice_1"
        assert self.basic_choice.text == "Go to town"
        assert self.basic_choice.next_node_id == "town_node"
        assert self.basic_choice.requirements == {}

    def test_choice_with_requirements(self):
        assert self.choice_with_requirements.requirements["min_level"] == 5

class TestStoryTree:
    def setup_method(self):
        self.story_tree = StoryTree()
        self.start_node = StoryNode("start", "narrative")
        self.town_node = StoryNode("town", "narrative")
        self.combat_node = StoryNode("combat", "combat")

        self.story_tree.add_node(self.start_node)
        self.story_tree.add_node(self.town_node)
        self.story_tree.add_node(self.combat_node)

        self.player = Player("Warrior")
        self.party = Party("player")
        self.party.add_member(self.player)

    def test_tree_initialization(self):
        assert isinstance(self.story_tree.nodes, dict)
        assert self.story_tree.current_node is None

    def test_node_addition(self):
        new_node = StoryNode("new_node", "narrative")
        self.story_tree.add_node(new_node)
        assert "new_node" in self.story_tree.nodes
        assert self.story_tree.nodes["new_node"] == new_node

    def test_story_start(self):
        self.story_tree.start_story("start")
        assert self.story_tree.current_node == self.start_node

    def test_available_choices(self):
        self.start_node.choices = []

        self.start_node.choices.append(
            StoryChoice("choice_1", "Go to town", "town_node")
        )
        self.start_node.choices.append(
            StoryChoice("choice_2", "Fight enemy", "combat_node", {"min_level": 5})
        )

        self.story_tree.start_story("start")
        self.party.members[0].level = 1
        available_choices = self.story_tree.get_available_choices(self.party)

        print(f"Available Choices: {[choice.text for choice in available_choices]}")
        for choice in available_choices:
            print(f"Choice Text: {choice.text}, Requirements: {choice.requirements}")

        if self.party.members[0].level < 5:
            assert len(available_choices) == 1

    def test_requirement_checking(self):
        requirements = {
                "party_size": {
                    "min": 1,
                    "max": 3
                    }
                }

        assert self.story_tree._check_requirements(requirements, self.party)

        for _ in range(3):
            self.party.add_member(Player("Warrior"))

        assert not self.story_tree._check_requirements(requirements, self.party)

class TestStoryProgression:
    def setup_method(self):
        self.story_tree = create_story()
        self.player = Player("Warrior")
        self.party = Party("player")
        self.party.add_member(self.player)

    def test_narrative_progression(self):
        result = handle_story_progression(self.story_tree, self.party)
        assert result is not None
        assert isinstance(result, dict)
        assert result["type"] == "narrative"
        assert "content" in result
        assert "choices" in result

    def test_combat_progression(self):
        combat_node = StoryNode("test_combat", "combat")
        combat_node.content = {
                "enemies": [("Goblin", 1)],
                "victory_node": "post_combat",
                "defeat_node": "game_over"
                }

        self.story_tree.add_node(combat_node)
        self.story_tree.current_node = combat_node

        if not self.party.members:
            player = Player("Warrior")
            player.level = 1
            self.party.add_member(player)

        assert self.story_tree.current_node == combat_node
        assert len(self.party.members) > 0

        assert self.story_tree.current_node.node_type == "combat"
        assert "enemies" in self.story_tree.current_node.content


    def test_recruitment_progression(self):
        recruitment_node = StoryNode("test_recruit", "recruitment")
        recruitment_node.content = {
                "npc_class": "Healer",
                "name": "Elena",
                "description": "A skilled healer",
                "next_node_accept": "town",
                "next_node_reject": "forest"
                }

        self.story_tree.add_node(recruitment_node)
        self.story_tree.current_node = recruitment_node

        result = handle_story_progression(self.story_tree, self.party)
        assert result is not None
        assert isinstance(result, dict)
        assert result["type"] == "recruitment"
        assert "content" in result

    def test_invalid_node_type(self):
        invalid_node = StoryNode("invalid", "invalid_type")
        self.story_tree.add_node(invalid_node)
        self.story_tree.current_node = invalid_node


        result = handle_story_progression(self.story_tree, self.party)
        assert result is None

class TestStoryContent:
    def setup_method(self):
        self.story_tree = create_story()
        self.player = Player("Warrior")
        self.party = Party("player")
        self.party.add_member(self.player)

    def test_story_creation(self):
        assert isinstance(self.story_tree, StoryTree)
        assert self.story_tree.current_node is not None
        assert "start" in self.story_tree.nodes

    def test_initial_choices(self):
        start_node = self.story_tree.nodes["start"]
        assert isinstance(start_node.choices, list)
        assert len(start_node.choices) > 0

        choice = start_node.choices[0]
        assert isinstance(choice, StoryChoice)
        assert choice.text
        assert choice.next_node_id

    def test_choice_requirements(self):
        available_choices = self.story_tree.get_available_choices(self.party)
        assert isinstance(available_choices, list)
        assert len(available_choices) > 0

        for choice in available_choices:
            requirements = choice.requirements
            assert self.story_tree._check_requirements(requirements, self.party)

    def test_story_branching(self):
        start_result = handle_story_progression(self.story_tree, self.party)
        assert start_result is not None
        assert isinstance(start_result, dict)
        assert start_result["type"] == "narrative"
        assert len(start_result["choices"]) > 0

        initial_node = self.story_tree.current_node
        first_choice = start_result["choices"][0]
        assert isinstance(first_choice, StoryChoice)  # Add this check
        assert hasattr(first_choice, 'next_node_id')  # Add this check

        self.story_tree.current_node = self.story_tree.nodes[first_choice.next_node_id]
        assert self.story_tree.current_node != initial_node

class TestGameSave:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.game_save = GameSave(save_directory=self.temp_dir)
        self.player = Player("Warrior")
        self.current_location = "town"

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_save_game_initialization(self):
        assert os.path.exists(self.temp_dir)
        assert self.game_save.max_slots == 5

    def test_basic_save_functionality(self):
        filepath = self.game_save.save_game(self.player, self.current_location)
        assert os.path.exists(filepath)

        with open(filepath, 'r') as f:
            save_data = json.load(f)

        assert save_data["player"]["class"] == "Warrior"
        assert save_data["player"]["level"] == 1
        assert save_data["location"] == "town"
        assert "timestamp" in save_data

    def test_save_with_slot(self):
        filepath = self.game_save.save_game(self.player, self.current_location, slot=1)
        assert "save_slot_1.json" in filepath
        assert os.path.exists(filepath)

    def test_save_slot_limit(self):
        with pytest.raises(ValueError) as exc_info:
            self.game_save.save_game(self.player, self.current_location, slot=6)
        assert "cannot exceed 5" in str(exc_info.value)

    def test_auto_save(self):
        filepath = self.game_save.save_game(self.player, self.current_location, auto_save=True)
        assert "autosave.json" in filepath
        assert os.path.exists(filepath)

    def test_load_game(self):
        save_path = self.game_save.save_game(self.player, self.current_location)
        loaded_data = self.game_save.load_game(os.path.basename(save_path))

        assert loaded_data is not None
        assert loaded_data["player"]["class"] == "Warrior"
        assert loaded_data["location"] == "town"

    def test_load_nonexistent_save(self):
        loaded_data = self.game_save.load_game("nonexistent.json")
        assert loaded_data is None

    def test_list_saves(self):
        first_save = self.game_save.save_game(self.player, "town", slot=1)
        second_save = self.game_save.save_game(self.player, "dungeon", slot=2)

        assert os.path.exists(first_save)
        assert os.path.exists(second_save)

        saves = self.game_save.list_saves()
        assert len(saves) == 2

        for save in saves:
            assert "filename" in save
            assert "timestamp" in save
            assert "player_class" in save
            assert "player_level" in save
            assert "location" in save
            assert save["location"] in ["town", "dungeon"]

    def test_save_mage_character(self):
        mage = Player("Mage")
        filepath = self.game_save.save_game(mage, "town")

        with open(filepath, 'r') as f:
            save_data = json.load(f)

        assert save_data["player"]["class"] == "Mage"
        assert "current_mana" in save_data["player"]
        assert "max_mana" in save_data["player"]

    def test_save_file_structure(self):
        filepath = self.game_save.save_game(self.player, self.current_location)

        with open(filepath, 'r') as f:
            save_data = json.load(f)

        required_player_fields = ["class", "level", "experience", "stats"]
        for field in required_player_fields:
            assert field in save_data["player"]

        required_stats = ["Strength", "Health", "Defense"]
        for stat in required_stats:
            assert stat in save_data["player"]["stats"]

    def test_invalid_save_attempts(self):
        with pytest.raises(ValueError) as exc_info:
            self.game_save.save_game(None, self.current_location)
        assert "Cannot save game without a player" in str(exc_info.value)

class TestGame:
    def setup_method(self):
        self.game = Game()

    def test_game_initialization(self):
        assert isinstance(self.game.game_save, GameSave)
        assert self.game.player is None
        assert self.game.player_party is None
        assert self.game.current_location == "town"
        assert isinstance(self.game.story, StoryTree)
        assert isinstance(self.game.keyboard, KeyboardInput)
        assert self.game.playing is True

    def test_start_new_game(self, monkeypatch):
        inputs = iter(['1', 'Warrior'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        success = self.game.start_new_game()
        assert success is True
        assert isinstance(self.game.player, Player)
        assert self.game.player.player_class == "Warrior"
        assert isinstance(self.game.player_party, Party)
        assert len(self.game.player_party.members) == 1
        assert self.game.player in self.game.player_party.members

    def test_invalid_class_selection(self, monkeypatch):
        inputs = iter(['4', '1', 'Warrior'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        success = self.game.start_new_game()
        assert success is True
        assert isinstance(self.game.player, Player)
        assert self.game.player.player_class == "Warrior"
        
    def test_load_game_with_valid_save(self, monkeypatch):
        mock_save_data = {
                "player": {
                    "class": "Warrior",
                    "level": 2,
                    "experience": 50,
                    "stats": {
                        "Strength": 25,
                        "Health": 120,
                        "Defense": 18
                        }
                    },
                "location": "dungeon"
                }

        def mock_save_menu(*_):
            return mock_save_data

        monkeypatch.setattr(self.game.game_save, 'handle_save_menu', mock_save_menu)
        success = self.game.load_game()
        assert success is True

    def test_load_game_with_invalid_save(self, monkeypatch):
        def mock_save_menu(*_):
            return None

        monkeypatch.setattr(self.game.game_save, 'handle_save_menu', mock_save_menu)
        success = self.game.load_game()
        assert success is False

    def test_rest_mechanics(self, monkeypatch):
        self.game.player = Player("Warrior")
        self.game.player.stats["Health"] = 50
        initial_max_health = self.game.player.max_health

        monkeypatch.setattr('time.sleep', lambda _: None)

        self.game.rest()
        assert self.game.player.stats["Health"] == initial_max_health

    def test_game_combat_initialization(self, monkeypatch):
        self.game.player = Player("Warrior")
        self.game.player_party = Party("player")
        self.game.player_party.add_member(self.game.player)

        inputs = iter(['1', '1'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        def mock_combat(_):
            return "VICTORY"
        monkeypatch.setattr(Combat, 'handle_combat_encounter', mock_combat)

        self.game.start_combat()
        assert isinstance(self.game.player, Player)
        assert self.game.current_location in ["town", "dungeon"]
        
    def test_handle_story_node(self, monkeypatch):
        self.game.player = Player("Warrior")
        self.game.player_party = Party("player")
        self.game.player_party.add_member(self.game.player)

        inputs = iter(['1'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        self.game.story.start_story("start")
        self.game.handle_story_node()
        assert self.game.story.current_node is not None

    def test_town_menu_navigation(self, monkeypatch):
        self.game.player = Player("Warrior")
        self.game.current_location = "town"

        inputs = iter(['1'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        self.game.town_menu()
        assert self.game.current_location == "dungeon"

    def test_dungeon_menu_navigation(self, monkeypatch):
        self.game.player = Player("Warrior")
        self.game.current_location = "dungeon"

        inputs = iter(['3'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        self.game.dungeon_menu()
        assert self.game.current_location == "town"

    def test_show_character_stats(self, monkeypatch, capsys):
        self.game.player = Player("Warrior")
        monkeypatch.setattr('builtins.input', lambda _: '')

        self.game.show_character_stats()
        captured = capsys.readouterr()
        assert "CHARACTER STATS" in captured.out
        assert "Warrior" in captured.out
        assert "Level" in captured.out

    def test_invalid_location_handling(self, monkeypatch):
        self.game.player = Player("Warrior")
        self.game.player_party = Party("player")
        self.game.player_party.add_member(self.game.player)
        self.game.current_location = "Invalid_location"

        def mock_input(prompt):
            return '1'

        monkeypatch.setattr('builtins.input', mock_input)

        self.game.main_game_loop()
        print(f"Current location: {self.game.current_location}")
        assert self.game.current_location == "town"

    def test_party_level_synchronization(self):
        self.game.player = Player("Warrior")
        self.game.player_party = Party("player")
        self.game.player_party.add_member(self.game.player)

        initial_level = self.game.player.level
        self.game.player.gain_experience(100)

        assert self.game.player.level > initial_level
        for member in self.game.player_party.members:
            assert member.level == self.game.player.level
