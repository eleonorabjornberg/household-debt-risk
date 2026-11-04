"""Synthetic two-vintage tests for what_moved.py and stale_claims.py (no network, no real data)."""
import csv
import importlib.util
import json
import zipfile
from pathlib import Path

import pandas as pd
import pytest

SK = Path(__file__).resolve().parents[1] / "scripts"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SK / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


wm, sc = _load("what_moved"), _load("stale_claims")

CAT = {
    "risk_buckets": {"pub": {"public": True}, "priv": {"public": False}},
    "series": [
        {"id": "FL893065105", "source": "z1", "role": "total"},
        {"id": "FL153165105", "source": "z1", "role": "total"},
        {"id": "FL153166000", "source": "z1", "role": "total"},
        {"id": "FL154104015", "source": "z1", "role": "total"},
        {"id": "FLM1", "source": "z1", "role": "mortgage_holder", "risk_bucket": "pub"},
        {"id": "FLM2", "source": "z1", "role": "mortgage_holder", "risk_bucket": "priv"},
        {"id": "FLC1", "source": "z1", "role": "cc_holder", "risk_bucket": "pub"},
        {"id": "FLC2", "source": "z1", "role": "cc_holder", "risk_bucket": "priv"},
    ],
}
QS = pd.to_datetime(["2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30"])


def frame(n, m1=40.0, c1=10.0, bump=None):
    """n quarters; mortgage 100 (m1 public, rest private), cc 50 (c1 public). bump: {quarter_idx: extra m1}."""
    rows = []
    for i in range(n):
        a = m1 + (bump or {}).get(i, 0.0)
        rows.append({"FLM1": a, "FLM2": 100 - 40.0 + 0, "FL893065105": a + 60.0, "FL153165105": a + 60.0,
                     "FLC1": c1, "FLC2": 50 - c1, "FL153166000": 50.0, "FL154104015": a + 60.0 + 50.0})
    return pd.DataFrame(rows, index=QS[:n])


def parts():
    return wm.catalog_parts(CAT)


def test_compute_and_buckets():
    mh, ch, public, ids = parts()
    r = wm.compute(frame(6), mh, ch, public)
    last = r.iloc[-1]
    assert last["public"] == pytest.approx(50.0)           # 40 mortgage + 10 cc
    assert last["scope"] == pytest.approx(150.0)
    assert last["share"] == pytest.approx(1 / 3)
    assert last["b_pub"] + last["b_priv"] == pytest.approx(last["scope"])  # buckets sum to scope


def test_formatting_like_site():
    assert wm.fpct(0.5638) == "56.4%"
    assert wm.ftn(10_768_000) == "$10.77T"
    assert wm.fpp(0.0013) == "+0.1 pp"
    assert wm.fpp(-0.0002) == "0.0 pp"
    assert wm.ftn_d(-70_000) == "-$0.07T"


def test_note_new_quarter_headline_and_revisions():
    mh, ch, public, _ = parts()
    prev = wm.compute(frame(5, bump=None), mh, ch, public)
    cur = wm.compute(frame(6, bump={2: 3.0, 5: 5.0}), mh, ch, public)   # 2025Q3 revised up; new 2026Q2
    note = wm.build_note(prev, cur, "2026-06-10", "2026-09-11", None, thr_pp=0.05, thr_musd=1.0, top_n=10)
    assert "## New quarters\n\n2026Q2" in note
    assert "## Headline, 2026Q2" in note
    assert "| Public share of scope | 36.2% |" in note or "| Public share of scope |" in note
    assert "| 2025Q3 |" in note                      # the revised quarter is listed
    assert "| 2025Q2 |" not in note                  # unrevised quarters are not
    assert "No validation results supplied" in note


def test_no_new_quarter_and_top_n():
    mh, ch, public, _ = parts()
    same = wm.compute(frame(6), mh, ch, public)
    note = wm.build_note(same, same, "a", "b")
    assert "None: the current vintage ends in the same quarter" in note
    assert "No quarter crosses the thresholds." in note
    cur = wm.compute(frame(6, bump={0: 1, 1: 2, 2: 3, 3: 4}), mh, ch, public)
    _, top, n_over = wm.revisions_table(same, cur, 0.05, 1.0, 2)
    assert n_over == 4 and len(top) == 2


def test_validation_flags_section():
    mh, ch, public, _ = parts()
    r = wm.compute(frame(6), mh, ch, public)
    res = {"meta": {"latest": "2026Q2"}, "summary": {"PASS": 1, "WARN": 1},
           "checks": [{"id": "A1", "description": "ok", "status": "PASS", "observed": "x"},
                      {"id": "E8", "description": "jumps", "status": "WARN", "observed": "1 unexplained"}],
           "unexplained_jumps": [{"series": "FLM1", "quarter": "2026Q1", "date": "2026-03-31", "delta_pp": 1.5, "robust_z": 7.0},
                                 {"series": "FLM2", "quarter": "2025Q1", "date": "2025-03-31", "delta_pp": -2.0, "robust_z": 8.0}]}
    note = wm.build_note(r, r, "a", "b", res)
    assert "| E8 jumps | WARN |" in note and "A1" not in note
    assert "- FLM1 2026Q1: +1.5 pp" in note and "FLM2 2025Q1" not in note   # only recent jumps listed
    res["meta"]["latest"] = "2026Q1"
    assert "WARNING: results.json is for 2026Q1" in wm.build_note(r, r, "a", "b", res)


def _write_long_zip(path, rows):
    lines = ["Series Name,description,Unit:,x,Multiplier:,y,Currency:,z,Unit_Mult:,u,Series_Name_Long,Date,Value"]
    for sid, d, v in rows:
        lines.append(f'Z1/Z1/{sid}.Q,"desc, with comma",a,b,c,d,e,f,g,h,{sid},{d},{v}')
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("Z1.csv", "\n".join(lines) + "\n")


def _write_table_zip(path, rows):
    ids = sorted({r[0] for r in rows})
    qs = sorted({r[1] for r in rows})
    val = {(s, d): v for s, d, v in rows}
    out = ["date," + ",".join(i + ".Q" for i in ids)]
    for d in qs:
        y, m = d[:4], int(d[5:7])
        out.append(f"{y}:Q{(m - 1) // 3 + 1}," + ",".join(str(val.get((i, d), "")) for i in ids))
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("table.csv", "\n".join(out) + "\n")


def test_both_zip_formats_end_to_end(tmp_path):
    root = tmp_path / "root"
    (root / "validation").mkdir(parents=True)
    (root / "pipeline").mkdir()
    real = Path(__file__).resolve().parents[4] / "validation" / "zparse.py"
    (root / "validation" / "zparse.py").write_text(real.read_text())
    (root / "pipeline" / "series_catalog.yaml").write_text(
        __import__("yaml").safe_dump(CAT))
    f_prev, f_cur = frame(5), frame(6, bump={5: 2.0})
    to_rows = lambda f, drop=(): [(c, d.strftime("%Y-%m-%d"), v) for d, r in f.iterrows() for c, v in r.items() if c not in drop]
    prev_zip, cur_zip = tmp_path / "z1_csv_files.zip", tmp_path / "FRB_Z1_csv.zip"
    _write_table_zip(prev_zip, to_rows(f_prev, drop=("FL154104015",)))   # per-table format, scope derived
    _write_long_zip(cur_zip, to_rows(f_cur))                            # long format
    out = tmp_path / "note.md"
    assert wm.main(["--prev", str(prev_zip), "--curr", str(cur_zip), "--root", str(root), "--out", str(out)]) == 0
    text = out.read_text()
    assert "## New quarters\n\n2026Q2" in text and "latest quarter 2026Q1" in text


# ---- stale_claims -------------------------------------------------------------------------
CHECKS = {"C2": {"observed": "56.38%"}, "C3": {"observed": "$10.768T of $19.097T"},
          "C4": {"observed": "36.12% -> 49.22%"}, "C5": {"observed": "+13.11 pp (rounded pts: +13.1)"}}


def row(**kw):
    base = dict(claim_id="X", claim="c", display="56.4%", value="56.4", unit="%", period="2026Q2",
                locations="web/page.tsx:12", check_id="C2")
    base.update(kw)
    return base


def test_stale_detects_only_display_changes():
    rows = [row(claim_id="same"),
            row(claim_id="moved", value="56.6"),                         # 56.6 vs 56.38 -> 56.4: changes
            row(claim_id="usd", display="$10.77T", value="10.77", unit="$T", check_id="C3"),
            row(claim_id="usd_old", display="$10.62T", value="10.62", unit="$T", check_id="C3"),
            row(claim_id="amb", display="49.2%", value="49.2", check_id="C4"),
            row(claim_id="pp", display="+13.1 pp", value="13.1", unit="pp", check_id="C5"),
            row(claim_id="nocheck", check_id="")]
    stale, same, cannot, no_check = sc.analyse(rows, CHECKS)
    assert [s[0]["claim_id"] for s in stale] == ["moved", "usd_old"]
    assert {s[0]["claim_id"] for s in same} == {"same", "usd", "amb", "pp"}
    assert [r["claim_id"] for r in no_check] == ["nocheck"]
    amb = [s for s in same if s[0]["claim_id"] == "amb"][0]
    assert amb[5] is True                                               # two candidates, flagged
    text = sc.render(stale, same, cannot, no_check, "t")
    assert "locations: web/page.tsx:12" in text and "moved" in text


def test_cannot_compare_is_listed_not_skipped():
    stale, same, cannot, _ = sc.analyse([row(claim_id="bad", unit="$T", display="$1.00T", value="1")], CHECKS)
    assert not stale and not same and len(cannot) == 1


def test_missing_register_skips_with_message(tmp_path, capsys):
    assert sc.main(["--register", str(tmp_path / "nope.csv"), "--results", str(tmp_path / "r.json")]) == 0
    assert "does not exist yet" in capsys.readouterr().out


def test_stale_main_never_edits_register(tmp_path):
    reg, res = tmp_path / "register.csv", tmp_path / "results.json"
    with reg.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row()))
        w.writeheader()
        w.writerow(row(value="56.6"))
    before = reg.read_bytes()
    res.write_text(json.dumps({"meta": {}, "checks": [{"id": "C2", "observed": "56.38%"}]}))
    assert sc.main(["--register", str(reg), "--results", str(res)]) == 0
    assert reg.read_bytes() == before


def test_detect_release_verdicts():
    from datetime import datetime
    d = _load("detect_release")
    rec = {"bytes": 100, "vintage": "2026-09-11", "path": "p"}
    assert d.verdict(100, datetime(2026, 9, 11, 16), rec, "2026-09-11")[0] == 0
    assert d.verdict(101, datetime(2026, 12, 10, 16), rec, "2026-09-11")[0] == 10
    assert d.verdict(100, datetime(2026, 12, 10, 16), rec, "2026-09-11")[0] == 10
    assert d.verdict(100, datetime(2026, 9, 11), None, None)[0] == 2
