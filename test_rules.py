from card import Card
from rules import compare_cards

class Game:
    level = "7"
    trump_suit = "Heart"
    wu_zhu = False


game = Game()

card1 = Card("Heart", "7")
card2 = Card("Heart", "A")

winner = compare_cards(card1, card2, game)

print(winner)