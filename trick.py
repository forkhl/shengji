from move import Move
from rules import compare_cards
from rules import is_trump

class Trick:
    def __init__(self, lead_player, round):
        self.lead_player = lead_player
        self.round = round
        self.moves = []
        self.lead_move = None

    def get_winner(self):
        winning_move = self.moves[0][1]
        winning_player = self.moves[0][0]

        for player, move in self.moves[1:]:
            if self.compare_moves(move, winning_move, self.round) > 0:
                winning_move = move
                winning_player = player

        return winning_player

    def add_move(self, player, move):
        self.moves.append((player, move))

        if self.lead_move is None:
            self.lead_move = move

    def is_valid_move(self, player, move):
        if self.lead_move is None and move.type != "unknown":
            return True
        
        # length always has to match
        if len(self.lead_move.cards) != len(move.cards):
            return False

        matching_cards = self.get_matching_cards(player, self.lead_move)
        
        if self.lead_move.type == "single":
            if move.cards[0] in matching_cards and len(matching_cards) > 0:
                return True
            elif len(matching_cards) == 0:
                return True
            else:
                return False
            
        if self.lead_move.type == "pair":
            if all(card in matching_cards for card in move.cards) and len(matching_cards) >= 2:
                if self.has_pair(matching_cards) and move.type != "pair":
                    return False
            elif len(matching_cards) == 0:
                return True
            elif len(matching_cards) == 1:
                if matching_cards[0] in move.cards:
                    return True
                return False
            else:
                return False

        if self.lead_move.type == "tractor":
            if move.type == "tractor":
                return True
            elif self.has_tractor(matching_cards):
                return False
            elif self.has_pair(matching_cards):
                return self.count_pairs(move.cards) >= self.count_pairs(matching_cards)
            else:
                return True

    def count_pairs(self, cards):
        counts = {}
        for card in cards:
            if card.rank not in counts:
                counts[card.rank] = 1
            else:
                counts[card.rank] += 1
        pair_count = 0
        for count in counts.values():
            pair_count += count // 2
        return pair_count
            

    def has_tractor(self, cards):
        if not self.has_pair(cards):
            return False
        for i in range(len(cards)-len(self.lead_move.cards)+1):
            if Move(cards[i:i+len(self.lead_move.cards)], self.round).type == "tractor":
                return True
        return False


    def has_pair(self, cards):
        ranks = {}
        for card in cards:
            if card.rank not in ranks:
                ranks[card.rank] = 1
            else:
                ranks[card.rank] += 1
        for count in ranks.values():
            if count >= 2:
                return True
        return False

    def get_matching_cards(self, player, lead_move):
        matching_cards = []

        for card in player.hand:
            if is_trump(lead_move.cards[0], self.round):
                if is_trump(card, self.round):
                    matching_cards.append(card)
            else:
                if card.suit == lead_move.cards[0].suit:
                    matching_cards.append(card)

        return matching_cards




    # assumes moves are legal
    # NOT FLUSHED OUT
    def compare_moves(self, move1, move2):
        if move1.type != move2.type:
            return -1
        if move1.type == "single":
            return compare_cards(
                move1.cards[0],
                move2.cards[0],
                self.round
            )
        if move1.type == "pair":
            return compare_cards(
                move1.cards[0],
                move2.cards[0],
                self.round
            )
        if move1.type == "tractor":
            return compare_cards(
                move1.cards[0],
                move2.cards[0],
                self.round
            )
        return -2

    

