<div id="top">

<!-- HEADER STYLE: MODERN -->
<div align="center" style="width: 100%;">

<img src="./frontend/public/logo.svg" width="35%" style="display: block; margin: 0 auto;" alt="Project Logo"/>

# LOCAL CHESS ANALYZER

<em><em>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/tarekchaalan/local-chess-analyzer?style=flat&logo=opensourceinitiative&logoColor=white&color=#FFFFFF" alt="license">
<img src="https://img.shields.io/github/last-commit/tarekchaalan/local-chess-analyzer?style=flat&logo=git&logoColor=white&color=#FFFFFF" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/tarekchaalan/local-chess-analyzer?style=flat&color=#FFFFFF" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/tarekchaalan/local-chess-analyzer?style=flat&color=#FFFFFF" alt="repo-language-count">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/JSON-000000.svg?style=flat&logo=JSON&logoColor=white" alt="JSON">
<img src="https://img.shields.io/badge/npm-CB3837.svg?style=flat&logo=npm&logoColor=white" alt="npm">
<img src="https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=flat&logo=SQLAlchemy&logoColor=white" alt="SQLAlchemy">
<img src="https://img.shields.io/badge/Svelte-FF3E00.svg?style=flat&logo=Svelte&logoColor=white" alt="Svelte">
<img src="https://img.shields.io/badge/JavaScript-F7DF1E.svg?style=flat&logo=JavaScript&logoColor=black" alt="JavaScript">
<img src="https://img.shields.io/badge/GNU%20Bash-4EAA25.svg?style=flat&logo=GNU-Bash&logoColor=white" alt="GNU%20Bash">
<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat&logo=FastAPI&logoColor=white" alt="FastAPI">
<br>
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white" alt="Docker">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/TypeScript-3178C6.svg?style=flat&logo=TypeScript&logoColor=white" alt="TypeScript">
<img src="https://img.shields.io/badge/C-A8B9CC.svg?style=flat&logo=C&logoColor=black" alt="C">
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=flat&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
<img src="https://img.shields.io/badge/Vite-646CFF.svg?style=flat&logo=Vite&logoColor=white" alt="Vite">
<img src="https://img.shields.io/badge/CSS-663399.svg?style=flat&logo=CSS&logoColor=white" alt="CSS">

</div>
</div>
<br clear="right">

---

## Table of Contents

- [Quick Download](#quick-download)
- [Overview](#overview)
- [Game review](#game-review)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Download

  - [macOS Apple Silicon](https://github.com/tarekchaalan/local-chess-analyzer/releases/latest/download/LocalChessAnalyzer-macOS-AppleSilicon.zip)
  - [macOS Intel](https://github.com/tarekchaalan/local-chess-analyzer/releases/latest/download/LocalChessAnalyzer-macOS-Intel.zip)
  - [Windows](https://github.com/tarekchaalan/local-chess-analyzer/releases/latest/download/LocalChessAnalyzer-Windows.zip)
  - [Linux](https://github.com/tarekchaalan/local-chess-analyzer/releases/latest/download/LocalChessAnalyzer-Linux.zip)

Unzip and run `LocalChessAnalyzer`. It opens in your browser at `http://127.0.0.1:42069`. Everything (games, analyses, settings) is stored in `data/` next to the executable — nothing leaves your machine.

---

## Overview

Private, offline game review for your **Chess.com** and **Lichess** games.

- **Any number of accounts**, on either platform, in one library. Syncs are incremental.
- **Stockfish analysis in a background queue** with live progress — close the tab, come back later, it keeps going.
- **chess.com-standard move classification**: Brilliant, Great, Best, Excellent, Good, Book, Inaccuracy, Mistake, Miss, Blunder, Forced.
- **Accuracy per player**, opening detection (ECO), evaluation graph, best lines, and clocks.
- **Insights across games**: accuracy trend, results by colour, blunder rate by time control, most played openings.
- Dark-first UI, keyboard navigation, export/import of the whole library as one SQLite file.

---

## Game review

Every move is classified from the engine's win probability (`Δ = win% before − win% after`, mover's point of view):

| Label | Rule |
| --- | --- |
| Book | Position is in the opening book (Lichess `chess-openings`, CC0) |
| Forced | Only one legal move |
| Brilliant | Best-or-near-best move that sacrifices a piece (by static exchange evaluation), not losing after, not already crushing |
| Great | The engine's top move where the second-best line is ≥10 win% worse |
| Best | The engine's top move |
| Miss | Opponent just blundered (or a mate was on) and the move gives ≥10 win% back while still ahead |
| Excellent / Good / Inaccuracy / Mistake / Blunder | Δ ≤ 2 / ≤ 5 / ≤ 10 / ≤ 20 / > 20 |

Accuracy uses the published Lichess formula; for Chess.com games their own accuracy is shown alongside for comparison.

---

## Project structure

```
backend/lca/          FastAPI app (Python 3.12, managed with uv)
  domain/             pure logic: classifier, SEE, accuracy, openings, PGN helpers
  platforms/          Chess.com and Lichess API clients
  services/           engine session, analysis pipeline, sync, job runner, stats
  api/                routers + pydantic schemas; /api/events streams progress (SSE)
  data/openings.json  ECO book (regenerate with scripts/build_openings.py)
backend/tests/        pytest suite with recorded API fixtures
frontend/src/         Svelte 5 + TypeScript SPA (no router/chart/CSS frameworks)
  lib/{router,api,stores,chess,ui,components,icons}
  routes/             Dashboard, Games, GameReview, Accounts, Settings, Setup
stockfish/            engine binaries per platform (GPL-3.0, see Copying.txt)
pyinstaller.spec      desktop bundle build; .github/workflows/release.yml publishes it
docs/superpowers/     design spec and implementation plan for v2
```

---

## Getting started

### Prerequisites

Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 22+. Stockfish binaries for every platform are bundled in `stockfish/`.

### Installation

```sh
git clone https://github.com/tarekchaalan/local-chess-analyzer
cd local-chess-analyzer
(cd backend && uv sync)          # backend deps into backend/.venv
(cd frontend && npm install)     # frontend deps
```

### Usage

**Desktop app (recommended)** — download the bundle for your platform from [Releases](https://github.com/tarekchaalan/local-chess-analyzer/releases/latest), unzip, run `LocalChessAnalyzer`. Data lives in `data/` next to the executable (`lca.db`).

**Development**

```sh
# terminal 1 — API on http://127.0.0.1:42069 (docs at /docs)
cd backend && uv run uvicorn lca.main:app --reload --port 42069

# terminal 2 — UI on http://localhost:5173 (proxies /api to the backend)
cd frontend && npm run dev
```

**Docker**

```sh
docker compose up --build
```
Frontend on http://localhost:6969, API on http://localhost:42069.

### Testing

```sh
cd backend && uv run pytest && uv run ruff check
cd frontend && npm test && npm run check
```

---

## Roadmap

- [x] Multi-account sync (Chess.com + Lichess)
- [x] Background analysis queue with live progress
- [x] chess.com-standard classifications, accuracy, openings, eval graph
- [x] Cross-game insights dashboard
- [ ] PGN import from disk
- [ ] Per-opening deep dives and mistake patterns
- [ ] Engine comparison (analyse the same game with two engines)

---

## Contributing

- **🐛 [Report Issues](https://github.com/tarekchaalan/local-chess-analyzer/issues)**: Submit bugs found or log feature requests for the `local-chess-analyzer` project.
- **💡 [Submit Pull Requests](https://github.com/tarekchaalan/local-chess-analyzer/pulls)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/tarekchaalan/local-chess-analyzer
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/tarekchaalan/local-chess-analyzer/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=tarekchaalan/local-chess-analyzer">
   </a>
</p>
</details>

---

## License

This project includes Stockfish, which is licensed under the GNU General Public License v3.0. See [LICENSE](./LICENSE) for details.

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square

---

