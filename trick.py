from move import Move
from rules import compare_cards

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

    # assumes moves are legal
    # NOT FLUSHED OUT
    def compare_moves(self, move1, move2):
        return compare_cards(
            move1.cards[0],
            move2.cards[0],
            self.round
        )

    

