import random

from game import Game
from player import Player
from move import Move

def get_random_move(round, player):
    # leading player can play anything legal
    if round.current_trick.lead_move is None:
        cards = player.hand[:]
        random.shuffle(cards)

        for card in cards:
            move = Move([card], round)

            if move.type != "unknown":
                return move

        return None

    needed = len(round.current_trick.lead_move.cards)

    cards = player.hand[:]
    random.shuffle(cards)

    from itertools import combinations

    for chosen in combinations(cards, needed):
        move = Move(list(chosen), round)

        if move.type != "unknown":
            if round.current_trick.is_valid_move(player, move):
                return move

    return None

players = [
    Player("p1"),
    Player("p2"),
    Player("p3"),
    Player("p4")
]

game = Game(players)
game.start_round()
round = game.current_round
round.trump_suit = "Hearts"
round.start_trick(players[0])
while True:
    player = round.current_player

    move = get_random_move(round, player)

    if move is None:
        print("No legal move for", player.name)
        break

    print(player.name, "plays", move.cards)

    round.play_move(player, move)

    if round.current_trick is None:
        print("Round ended!")
        break