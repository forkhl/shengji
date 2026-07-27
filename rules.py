rank_order = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14
}


def is_joker(card):
    return card.suit == "Joker"


def is_trump(card, round):
    # Jokers are always trump
    if is_joker(card):
        return True

    # Current level cards are always trump
    if card.rank == round.level:
        return True

    # Trump suit does not exist in Wu Zhu
    if round.trump_suit != "Wu Zhu":
        if card.suit == round.trump_suit:
            return True

    return False

def get_strength(card, round):
    # Big Joker highest
    if card.suit == "Joker" and card.rank == "Big":
        return 1000

    # Small Joker second
    if card.suit == "Joker" and card.rank == "Small":
        return 900

    # Current level cards
    if card.rank == round.level:
        if card.suit == round.trump_suit:
            return 800
        else:
            return 700

    # Trump suit cards
    if card.suit == round.trump_suit:
        return 600 + rank_order[card.rank]

    # Normal cards
    return rank_order[card.rank]

def compare_cards(card1, card2, round):
    strength1 = get_strength(card1, round)
    strength2 = get_strength(card2, round)

    if strength1 > strength2:
        return 1
    elif strength1 < strength2:
        return -1
    else:
        return 0