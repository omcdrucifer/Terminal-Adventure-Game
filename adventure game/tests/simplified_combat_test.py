import pytest
from characters import Player, Enemy
from combat import Combat
from party import Party

@pytest.mark.timeout(3)  # 3 second timeout
def test_simplified_combat_encounter():
    # Create player and enemy parties
    player = Player("Warrior")
    player_party = Party("player")
    player_party.add_member(player)

    enemy = Enemy("Goblin", player_level=1)
    enemy_party = Party("enemy")
    enemy_party.add_member(enemy)

    combat = Combat(player_party, enemy_party)

    # Run the simplified combat encounter
    result = combat.simplified_combat_encounter()

    # Check if the result is either VICTORY or DEFEAT
    assert result in ["VICTORY", "DEFEAT"], f"Unexpected result: {result}"
