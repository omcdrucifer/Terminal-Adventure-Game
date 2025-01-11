# mostly unchanged from the original code. I removed the level sync logic since I'm no longer
# tethering levels in the class constructor logic as it will be easier to do that in the game loop
# when constructing the party.
class Party:
    def __init__(self, party_type="player", max_size=4):
        self.members = []
        self.party_type = party_type
        self.max_size = max_size

    def add_member(self, member):
        if len(self.members) >= self.max_size:
            raise ValueError("Party is full!")
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

    def get_total_health(self):
        if not self.members:
            return 0
        return sum([member.stats["Health"] for member in self.members])

    def get_party_status(self):
        status = []
        for i, member in enumerate(self.members):
            member_type = (
                    "Player" if hasattr(member, "player_class") or hasattr(member, "npc_class")
                else "Enemy" if hasattr(member, "enemy_class") or hasattr(member, "boss_class")
                else "Unknown"
            )
            status.append(f"{i+1}. {member_type} - {member.stats['Health']} HP")
        return status

    def get_average_level(self):
        if not self.members:
            return 0
        return sum([member.level for member in self.members]) / len(self.members)
