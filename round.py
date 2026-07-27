from trick import Trick

class Round:
    def __init__(self, game, defending_team, attacking_team):
        self.game = game

        self.defending_team = defending_team
        self.attacking_team = attacking_team

        self.level = defending_team.level
        self.trump_suit = None

        self.tricks = []
        self.current_trick = None
        self.attacker_points = 0

        self.bottom_cards = []
        self.it_player = None

    def deal_cards(self):
        self.game.deck.shuffle()
        self.bottom_cards = self.game.deck.deal(self.game.players)

    def start_trick(self, lead_player):
        self.current_trick = Trick(lead_player, self)

    def end_trick(self):
        winner = self.current_trick.get_winner()

        points = self.current_trick.get_points()

        if winner.team == self.attacking_team:
            self.attacker_points += points

        self.tricks.append(self.current_trick)
        self.current_trick = None

        return winner