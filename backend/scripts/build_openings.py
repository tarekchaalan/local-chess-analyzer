"""Regenerate lca/data/openings.json from the Lichess chess-openings dataset (CC0).

Usage: uv run python scripts/build_openings.py
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import chess.pgn
import httpx

BASE = "https://raw.githubusercontent.com/lichess-org/chess-openings/master/"
FILES = ["a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv"]
OUT = Path(__file__).resolve().parents[1] / "lca" / "data" / "openings.json"


def main() -> int:
    book: dict[str, list[str]] = {}
    with httpx.Client(timeout=60) as client:
        for name in FILES:
            r = client.get(BASE + name)
            r.raise_for_status()
            lines = r.text.splitlines()
            header = lines[0].split("\t")
            eco_i, name_i, pgn_i = header.index("eco"), header.index("name"), header.index("pgn")
            for line in lines[1:]:
                cols = line.split("\t")
                game = chess.pgn.read_game(io.StringIO(cols[pgn_i]))
                if game is None:
                    continue
                board = game.board()
                for mv in game.mainline_moves():
                    board.push(mv)
                book[board.epd()] = [cols[eco_i], cols[name_i]]
            print(f"{name}: {len(lines) - 1} rows", file=sys.stderr)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(dict(sorted(book.items())), ensure_ascii=False, separators=(",", ":"))
    )
    print(f"wrote {len(book)} positions to {OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
