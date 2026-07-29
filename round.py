from deck import BOTTOM_CARD_COUNT
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

        self.current_call = None

        self.current_player = None

    def play_move(self, player, move):
        if player != self.current_player:
            return False
        if not self.current_trick.is_valid_move(player, move):
            return False
        for card in move.cards:
            player.hand.remove(card)
        self.current_trick.add_move(player, move)
        if len(self.current_trick.moves) == 4:
            winner = self.end_trick()
            if self.is_round_over():
                self.game.end_round()
            else:
                self.start_trick(winner)
        else:
            self.current_player = self.get_next_player()
        return True

    def is_round_over(self):
        for player in self.game.players:
            if len(player.hand) > 0:
                return False
        return True

    def can_call(self, player, cards):
        for card in cards:
            if card not in player.hand:
                return False

        call_type = self.get_call_type(cards)

        if call_type == "invalid":
            return False

        if call_type != "wu_zhu":
            for card in cards:
                if card.rank != self.level:
                    return False

            if len(cards) == 2 and cards[0].suit != cards[1].suit:
                return False
            return True

        if self.current_call is not None:
            _, current_cards = self.current_call

            if self.compare_calls(cards, current_cards) <= 0:
                return False

        return True

    def get_call_type(self, cards):
        if all(card.suit == "Joker" for card in cards):
            if (
                len(cards) == 2
                and cards[0].rank == cards[1].rank
            ):
                return "wu_zhu"
            return "invalid"

        if len(cards) == 1:
            return "single"

        if len(cards) == 2:
            if cards[0].rank == cards[1].rank:
                return "pair"

        return "invalid"

    def compare_calls(self, cards1, cards2):
        type1 = self.get_call_type(cards1)
        type2 = self.get_call_type(cards2)

        strength = {
            "single": 1,
            "pair": 2,
            "wu_zhu": 3
        }

        return strength[type1] - strength[type2]


    def make_call(self, player, cards):
        if not self.can_call(player, cards):
            return False

        self.current_call = (player, cards)

        return True

    def finish_calling(self):
        if self.current_call is None:
            return False
        
        player, cards = self.current_call

        self.it_player = player

        if cards[0].suit == "Joker":
            self.trump_suit = "Wu Zhu"
        else:
            self.trump_suit = cards[0].suit

        return True

    def pick_up_bottom(self):
        self.it_player.hand.extend(self.bottom_cards)

    def discard_bottom(self, cards):
        if len(cards) != len(self.bottom_cards):
            return False
        self.bottom_cards = []
        for card in cards:
            if card in self.it_player.hand:
                self.it_player.hand.remove(card)
                self.bottom_cards.append(card)
            else:
                return False
        return True

    def deal_cards(self):
        self.game.deck.shuffle()
        self.bottom_cards = self.game.deck.deal(self.game.players)

    def get_next_player(self):
        index = self.game.players.index(self.current_player)
        return self.game.players[(index+1)%4]

    def start_trick(self, lead_player):
        self.current_trick = Trick(lead_player, self)
        self.current_player = lead_player

    def end_trick(self):
        winner = self.current_trick.get_winner()

        points = self.current_trick.get_points()

        if winner.team == self.attacking_team:
            self.attacker_points += points

        self.tricks.append(self.current_trick)
        self.current_trick = None

        return winner

    def add_bottom_points(self):
        if self.tricks[-1].get_winner().team != self.attacking_team:
            return
        cards_used = self.trick[-1].get_card_count()
        mult = 2**cards_used
        points = 0
        for card in self.bottom_cards:
            if card.rank == "5":
                points += 5
            elif card.rank == "10":
                points += 10
            elif card.rank == "K":
                points += 10
        self.attacker_points += points * mult