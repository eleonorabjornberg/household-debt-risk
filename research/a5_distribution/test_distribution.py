"""Offline tests for A5 (no downloads): DFA share check, state parsing, tile layout."""
import importlib.util
import io
import zipfile
from pathlib import Path

import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location("distribution", Path(__file__).with_name("distribution.py"))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def _zip(tmp_path, shares_bottom):
    cols = ["Date", "Category"] + d.DEBT + ["Assets", "Net worth", "Real estate"]
    rows = []
    for date in d.DATES:
        for cat, v in (("Bottom50", shares_bottom), ("Top50", 100 - shares_bottom)):
            rows.append([date, cat] + [v] * (len(cols) - 2))
    df = pd.DataFrame(rows, columns=cols)
    p = tmp_path / "dfa.zip"
    with zipfile.ZipFile(p, "w") as z:
        for stem in d.GROUPINGS.values():
            for kind in ("shares", "levels"):
                z.writestr(f"dfa-{stem}-{kind}.csv", df.to_csv(index=False))
    return p


def test_dfa_shares_must_add_to_100(tmp_path):
    shares, lev = d.dfa_tables(_zip(tmp_path, 40.0))
    assert set(shares.Date) == set(d.DATES)
    bad = tmp_path / "bad"
    bad.mkdir()
    p = _zip(bad, 40.0)
    with zipfile.ZipFile(p) as z:
        files = {n: z.read(n) for n in z.namelist()}
    df = pd.read_csv(io.BytesIO(files["dfa-income-shares.csv"]))
    df.loc[0, "Home mortgages"] += 5  # planted error
    files["dfa-income-shares.csv"] = df.to_csv(index=False).encode()
    with zipfile.ZipFile(p, "w") as z:
        for n, b in files.items():
            z.writestr(n, b)
    with pytest.raises(AssertionError):
        d.dfa_tables(p)


def test_read_state_parses_header_and_codes(tmp_path):
    raw = pd.DataFrame([["Citation: x", None, None], ["state", "Q4_2024", "Q4_2025"], ["AK", 1, 2], ["Note", None, None]])
    p = tmp_path / "s.xlsx"
    with pd.ExcelWriter(p) as w:
        raw.to_excel(w, sheet_name="mortgage", header=False, index=False)
    t = d.read_state(p, "mortgage")
    assert list(t.index) == ["AK"] and list(t.columns) == [2024, 2025] and t.at["AK", 2025] == 2


def test_tile_layout_has_50_states_and_dc():
    src = Path(__file__).with_name("figures.py").read_text()
    ns = {}
    start = src.index("TILES = {")
    exec(src[start:src.index("}", start) + 1], ns)
    tiles = ns["TILES"]
    assert len(tiles) == d.STATES and "DC" in tiles and "PR" not in tiles
    assert len(set(tiles.values())) == len(tiles)  # no two states share a square
