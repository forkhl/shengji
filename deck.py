
from card import Card
import random
 
BOTTOM_CARD_COUNT = 8
 
suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
 
class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck(2)
        self.deal_order = []
 
    def create_deck(self, num_decks):
        for i in range(num_decks):
            self.cards.append(Card("Big", "Joker"))
            self.cards.append(Card("Small", "Joker"))
            for suit in suits:
                for rank in ranks:
                    card = Card(rank, suit)
                    self.cards.append(card)
 
    def shuffle(self):
        random.shuffle(self.cards)
 
    def deal(self, players):
        self.deal_order = []
        for player in players:
            player.hand = []
        for i, card in enumerate(self.cards[:-BOTTOM_CARD_COUNT]):
            players[i % len(players)].hand.append(card)
            self.deal_order.append(card)
 
        return self.cards[-BOTTOM_CARD_COUNT:]
