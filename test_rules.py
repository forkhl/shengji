from player import Player
from card import Card
from game import Game
from round import Round
from move import Move


def setup_round():
    players = [
        Player("p1"),
        Player("p2"),
        Player("p3"),
        Player("p4")
    ]

    game = Game(players)

    game.current_round = Round(
        game,
        game.teams[0],
        game.teams[1]
    )

    round = game.current_round
    round.level = "7"
    round.trump_suit = "Hearts"

    return round, players


def make_card(rank, suit):
    return Card(rank, suit)


def test_single_follow():
    round, players = setup_round()

    lead_card = make_card("A", "Clubs")
    follow_card = make_card("5", "Clubs")
    off_suit_card = make_card("9", "Spades")

    players[1].hand = [
        follow_card,
        off_suit_card
    ]

    round.start_trick(players[0])

    lead = Move([lead_card], round)
    good_move = Move([follow_card], round)

    round.current_trick.add_move(players[0], lead)

    assert round.current_trick.is_valid_move(
        players[1],
        good_move
    )

    print("single follow passed")


def test_cannot_ignore_suit():
    round, players = setup_round()

    club = make_card("5", "Clubs")
    spade = make_card("A", "Spades")

    players[1].hand = [
        club,
        spade
    ]

    round.start_trick(players[0])

    lead = Move(
        [make_card("K", "Clubs")],
        round
    )

    bad_move = Move(
        [spade],
        round
    )

    round.current_trick.add_move(players[0], lead)

    assert not round.current_trick.is_valid_move(
        players[1],
        bad_move
    )

    print("cannot ignore suit passed")


def test_can_slough_when_no_suit():
    round, players = setup_round()

    spade = make_card("A", "Spades")

    players[1].hand = [
        spade
    ]

    round.start_trick(players[0])

    lead = Move(
        [make_card("K", "Clubs")],
        round
    )

    move = Move(
        [spade],
        round
    )

    round.current_trick.add_move(players[0], lead)

    assert round.current_trick.is_valid_move(
        players[1],
        move
    )

    print("slough passed")


def test_pair_follow():
    round, players = setup_round()

    pair1 = make_card("5", "Clubs")
    pair2 = make_card("5", "Clubs")

    players[1].hand = [
        pair1,
        pair2
    ]

    round.start_trick(players[0])

    lead = Move(
        [
            make_card("A", "Clubs"),
            make_card("A", "Clubs")
        ],
        round
    )

    response = Move(
        [
            pair1,
            pair2
        ],
        round
    )

    round.current_trick.add_move(players[0], lead)

    assert round.current_trick.is_valid_move(
        players[1],
        response
    )

    print("pair passed")


def test_wrong_pair():
    round, players = setup_round()

    pair1 = make_card("5", "Clubs")
    pair2 = make_card("5", "Clubs")
    single = make_card("6", "Clubs")

    players[1].hand = [
        pair1,
        pair2,
        single
    ]

    round.start_trick(players[0])

    lead = Move(
        [
            make_card("A", "Clubs"),
            make_card("A", "Clubs")
        ],
        round
    )

    bad = Move(
        [
            pair1,
            single
        ],
        round
    )

    round.current_trick.add_move(players[0], lead)

    assert not round.current_trick.is_valid_move(
        players[1],
        bad
    )

    print("wrong pair passed")


def test_tractor():
    round, players = setup_round()

    cards = [
        make_card("5", "Clubs"),
        make_card("5", "Clubs"),
        make_card("6", "Clubs"),
        make_card("6", "Clubs")
    ]

    players[1].hand = cards

    round.start_trick(players[0])

    lead = Move(
        [
            make_card("3", "Clubs"),
            make_card("3", "Clubs"),
            make_card("4", "Clubs"),
            make_card("4", "Clubs")
        ],
        round
    )

    response = Move(cards, round)

    round.current_trick.add_move(players[0], lead)
    
    assert round.current_trick.is_valid_move(
        players[1],
        response
    )
    
    print("tractor passed")


test_single_follow()
test_cannot_ignore_suit()
test_can_slough_when_no_suit()
test_pair_follow()
test_wrong_pair()
test_tractor()

print("\nALL TESTS PASSED")