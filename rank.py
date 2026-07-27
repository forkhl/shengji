BASE_ORDER = [
    "2", "3", "4", "5", "6",
    "7", "8", "9", "10",
    "J", "Q", "K", "A"
]


def get_normal_order(level):
    order = BASE_ORDER.copy()
    order.remove(level)
    return order


def get_trump_order(level):
    order = get_normal_order(level)

    order.append(level + "_normal")
    order.append(level + "_trump")
    order.append("Small")
    order.append("Big")

    return order

def get_card_position(card, round):
    if card.suit == "Joker":
        order = get_trump_order(round.level)
        
        return order.index(card.rank)

    # Level cards
    if card.rank == round.level:
        order = get_trump_order(round.level)

        if card.suit == round.trump_suit:
            return order.index(round.level + "_trump")
        else:
            return order.index(round.level + "_normal")

    # Trump suit cards
    if card.suit == round.trump_suit:
        order = get_trump_order(round.level)
        return order.index(card.rank)

    # Normal cards
    order = get_normal_order(round.level)
    return order.index(card.rank)