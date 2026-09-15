import chess
import pytest

from lca.domain.openings import Opening, OpeningBook


@pytest.fixture(scope="module")
def book() -> OpeningBook:
    return OpeningBook.load()


def _board(*sans: str) -> chess.Board:
    b = chess.Board()
    for san in sans:
        b.push_san(san)
    return b


def test_kings_knight_opening(book):
    op = book.lookup(_board("e4", "e5", "Nf3").epd())
    assert op == Opening(eco="C40", name="King's Knight Opening")


def test_ruy_lopez(book):
    op = book.lookup(_board("e4", "e5", "Nf3", "Nc6", "Bb5").epd())
    assert op is not None and op.name == "Ruy Lopez"


def test_is_book_uses_board(book):
    assert book.is_book(_board("d4", "d5", "c4"))
    assert not book.is_book(chess.Board("8/8/8/3k4/8/8/8/3K4 w - - 0 1"))


def test_start_position_is_not_an_opening(book):
    assert book.lookup(chess.Board().epd()) is None
