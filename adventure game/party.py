# manages parties for both players and enemies
from base_classes import GameEntity
from characters import NPC, Enemy, Boss 

class Party:
    def __init__(self, party_type="player", max_size=4):
        self.members = []
        self.party_type = party_type
        self.max_size = max_size

    def add_member(self, member):
        if len(self.members) >= self.max_size:
            raise ValueError("Party is full")
        if not isinstance(member, GameEntity):
            raise ValueError("Can only add game entities to parties")
        if self.party_type == "player":
            if hasattr(member, 'player_class') or hasattr(member, 'npc_class'):
                self.members.append(member)
            else:
                raise ValueError("Can only add Player or NPC to player parties")
        elif self.party_type == "enemy":
            if hasattr(member, 'enemy_class') or hasattr(member, 'boss_class'):
                self.members.append(member)
            else:
                raise ValueError("Can only add Enemy or Boss to enemy parties")

    def remove_member(self, member):
        if member in self.members:
            self.members.remove(member)

    def get_active_members(self):
        return [member for member in self.members if member.stats["Health"] > 0]

    def is_party_alive(self):
        return len(self.get_active_members()) > 0

    def synchronize_level(self, player_level):
        if self.party_type == "player":
            for member in self.members:
                if isinstance(member, NPC):
                    member.synchronize_level(player_level)
        elif self.party_type == "enemy":
            party_size = len(self.members)
            for member in self.members:
                if isinstance(member, Enemy):
                    member.__init__(member.enemy_class, player_level)
                elif isinstance(member, Boss):
                    member.__init__(member.boss_class, player_level, party_size)

    def get_total_health(self):
        if not self.members:
            return 0
        return sum(member.level for member in self.members) / len(self.members)

    def get_party_status(self):
        status = []
        for i, member in enumerate(self.members):
            member_type = (
                    getattr(member, 'player_class', None) or
                    getattr(member, 'npc_class', None) or
                    getattr(member, 'enemy_class', None) or
                    getattr(member, 'boss_class', None)
                    )
            status.append(f"{member_type} (#{i}): Health = {member.stats['Health']}")
        return status
