"""ECO opening book backed by a bundled EPD -> (eco, name) map."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import chess

_DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "openings.json"


@dataclass(frozen=True, slots=True)
class Opening:
    eco: str
    name: str


class OpeningBook:
    def __init__(self, entries: dict[str, Opening]):
        self._entries = entries

    @classmethod
    def load(cls, path: Path | None = None) -> OpeningBook:
        raw = json.loads((path or _DEFAULT_PATH).read_text(encoding="utf-8"))
        return cls({epd: Opening(eco=v[0], name=v[1]) for epd, v in raw.items()})

    @classmethod
    def empty(cls) -> OpeningBook:
        return cls({})

    def __len__(self) -> int:
        return len(self._entries)

    def lookup(self, epd: str) -> Opening | None:
        return self._entries.get(epd)

    def is_book(self, board: chess.Board) -> bool:
        return board.epd() in self._entries
