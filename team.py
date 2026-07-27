class Team:
    def __init__(self, players):
        self.players = players
        self.level = "2"

    def has_player(self, player):
        return player in self.players