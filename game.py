from deck import Deck
from player import Player
from round import Round
from team import Team

class Game:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.teams = [
            Team([players[0], players[2]]),
            Team([players[1], players[3]])
        ]
        self.current_round = None

    def start_round(self):
        defending_team = self.teams[0]
        attacking_team = self.teams[1]

        self.current_round = Round(self, defending_team, attacking_team)

        self.current_round.deal_cards()

        for player in self.players:
            player.sort_hand(self.current_round)

    def end_round(self):
        self.current_round.add_bottom_points()
        points = self.current_round.attacker_points
        
        if points == 0:
            self.current_round.defending_team.increase_level(3)
        elif points < 40:
            self.current_round.defending_team.increase_level(2)
        elif points < 80:
            self.current_round.defending_team.increase_level(1)
        elif points < 120:
            self.teams[0], self.teams[1] = self.teams[1], self.teams[0]
        elif points < 150:
            self.current_round.attacking_team.increase_level(1)
            self.teams[0], self.teams[1] = self.teams[1], self.teams[0]
        else:
            self.current_round.attacking_team.increase_level(2)
            self.teams[0], self.teams[1] = self.teams[1], self.teams[0]
        self.start_round()


