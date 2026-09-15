# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build for the desktop bundle. Run from the repo root:
    backend/.venv/bin/pyinstaller --clean --noconfirm pyinstaller.spec
"""
import os

from PyInstaller.building.build_main import COLLECT, EXE, PYZ, Analysis

datas = [("backend/lca/data", "lca/data")]
if os.path.isdir("frontend/dist"):
    datas.append(("frontend/dist", "frontend_dist"))
if os.path.isdir("stockfish"):
    datas.append(("stockfish", "stockfish"))

a = Analysis(
    ["backend/lca/cli.py"],
    pathex=["backend"],
    binaries=[],
    datas=datas,
    hiddenimports=["aiosqlite", "sse_starlette", "sse_starlette.sse"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LocalChessAnalyzer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="LocalChessAnalyzer",
)
