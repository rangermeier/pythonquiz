import nose
from kalaha import *

def test_board():
    board = Board()
    assert(len(board.players) == 2)

def test_sow():
    board = Board()
    p1h = board.players[0].houses
    p2h = board.players[1].houses
    p1k = board.players[0].kalaha
    assert(len(p1h[0].seeds) == 3)
    assert(len(p1k.seeds) == 0)
    board.sow(p1h[4])
    assert(len(p1h[4].seeds) == 0)
    assert(len(p1h[5].seeds) == 4)
    assert(len(p2h[0].seeds) == 4)
    assert(len(p1k.seeds) == 1)

def test_next():
    board = Board()
    assert(board.turn.houses[0].next() == board.turn.houses[1])
    assert(board.turn.houses[5].next() == board.turn.kalaha)
    assert(board.turn.kalaha.next() == board.turn.opponent.houses[0])
    assert(board.turn.opponent.houses[5].next() == board.turn.houses[0])

def test_neighbours():
    board = Board()
    n = board.turn.houses[3].neighbours(10)
    assert(n[0] == board.turn.houses[4])
    assert(n[2] == board.turn.kalaha)
    assert(n[8] == board.turn.opponent.houses[5])
    assert(n[9] == board.turn.houses[0])

def test_opposite():
    board = Board()
    assert(board.turn.houses[0].opposite() == board.turn.opponent.houses[5])
    assert(board.turn.houses[4].opposite() == board.turn.opponent.houses[1])

def test_capture():
    board = Board()
    assert(len(board.turn.kalaha.seeds) == 0)
    assert(board.players[0] == board.turn)
    board.sow(board.turn.houses[3])
    assert(board.players[0] == board.turn)
    assert(len(board.turn.houses[3].seeds) == 0)
    assert(len(board.turn.kalaha.seeds) == 1) # play another turn ...
    board.sow(board.turn.houses[0])
    assert(board.players[1] == board.turn)
    assert(len(board.players[0].houses[3].seeds) == 0)
    assert(len(board.players[0].houses[3].opposite().seeds) == 0)
    assert(len(board.players[0].kalaha.seeds) == 5)
    
def test_player_seeds():
    board = Board()
    assert(len(board.players[0].seeds()) == 18)
    board.sow(board.players[0].houses[5])
    assert(len(board.players[0].seeds()) == 15)
    assert(len(board.players[1].seeds()) == 20)
    
