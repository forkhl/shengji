LEVELS = [
    "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "J", "Q", "K", "A"
]

class Team:
    def __init__(self, players):
        self.players = players
        self.level = "2"

        for player in players:
            player.team = self

    def has_player(self, player):
        return player in self.players

    def increase_level(self, amount):
        index = LEVELS.index(self.level)
        index += amount

        if index >= len(LEVELS):
            index = len(LEVELS) - 1

        self.level = LEVELS[index]