import chess

from lca.domain.sacrifice import en_prise, is_piece_sacrifice, is_simple_recapture, see


def test_see_hanging_queen():
    board = chess.Board("8/8/8/3q4/8/8/8/3RK2k w - - 0 1")
    assert see(board, chess.D5) == 9


def test_see_defended_pawn_not_worth_taking_with_rook():
    board = chess.Board("4k3/8/4p3/3p4/8/8/8/3RK3 w - - 0 1")
    assert see(board, chess.D5) == 0


def test_see_handles_xray_batteries():
    # Rd2xd5 Rd7xd5 Rd1xd5 Rd8xd5 -> White loses material overall.
    board = chess.Board("3r2k1/3r4/8/3p4/8/8/3R4/3RK3 w - - 0 1")
    assert see(board, chess.D5) == 0


def test_see_no_attackers():
    board = chess.Board("4k3/8/8/3p4/8/8/8/4K3 w - - 0 1")
    assert see(board, chess.D5) == 0


def test_en_prise():
    assert en_prise(chess.Board("8/8/8/3q4/8/8/8/3RK2k w - - 0 1"), chess.D5)
    assert not en_prise(chess.Board("4k3/8/4p3/3p4/8/8/8/3RK3 w - - 0 1"), chess.D5)


def test_greek_gift_is_a_sacrifice():
    board = chess.Board("5rk1/5ppp/8/8/8/3B1N2/8/3QK3 w - - 0 1")
    assert is_piece_sacrifice(board, chess.Move.from_uci("d3h7"))


def test_exchange_sacrifice():
    board = chess.Board("2r3k1/8/8/8/8/2N5/1P6/6K1 b - - 0 1")
    assert is_piece_sacrifice(board, chess.Move.from_uci("c8c3"))


def test_queen_trade_is_not_a_sacrifice():
    board = chess.Board("r2qk3/8/8/8/8/8/8/3QK3 w - - 0 1")
    assert not is_piece_sacrifice(board, chess.Move.from_uci("d1d8"))


def test_pawn_sacrifice_does_not_count():
    board = chess.Board("4k3/8/2n5/8/8/8/3P4/4K3 w - - 0 1")
    assert not is_piece_sacrifice(board, chess.Move.from_uci("d2d4"))


def test_piece_already_hanging_is_not_a_new_sacrifice():
    board = chess.Board("4k3/8/8/8/3p4/2N5/8/4K3 w - - 0 1")
    assert not is_piece_sacrifice(board, chess.Move.from_uci("e1d1"))


def test_moving_a_piece_into_capture_is_a_sacrifice():
    # Knight jumps to a square attacked by a pawn, nothing captured.
    board = chess.Board("4k3/8/8/3p4/8/2N5/8/4K3 w - - 0 1")
    assert is_piece_sacrifice(board, chess.Move.from_uci("c3e4"))


def test_simple_recapture():
    board = chess.Board()
    for san in ("e4", "d5", "exd5"):
        board.push_san(san)
    prev = board.peek()
    assert is_simple_recapture(board, chess.Move.from_uci("d8d5"), prev)


def test_not_a_recapture_when_previous_move_was_quiet():
    board = chess.Board()
    for san in ("e4", "d5", "Nf3"):
        board.push_san(san)
    assert not is_simple_recapture(board, chess.Move.from_uci("d5e4"), board.peek())
    assert not is_simple_recapture(board, chess.Move.from_uci("d5e4"), None)
