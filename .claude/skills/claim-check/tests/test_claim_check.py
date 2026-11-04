"""Synthetic register + results fixtures (no real data, no network)."""
import csv
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "claim_check.py"
spec = importlib.util.spec_from_file_location("claim_check", SCRIPT)
cc = importlib.util.module_from_spec(spec)
import sys
sys.modules["claim_check"] = cc
spec.loader.exec_module(cc)

COLS = ["claim_id", "claim", "display", "value", "unit", "period", "locations", "computation", "series_ids",
        "vintage", "validation", "check_id", "notes"]


def row(cid, display, value, unit, computation, check_id="", validation="UNVERIFIED", claim="x", period="2026Q2", loc="doc.md:1"):
    return dict(claim_id=cid, claim=claim, display=display, value=value, unit=unit, period=period, locations=loc,
                computation=computation, series_ids="FL1", vintage="z1:2026-09-11", validation=validation,
                check_id=check_id, notes="")


@pytest.fixture
def ctx(tmp_path):
    (tmp_path / "claims").mkdir()
    (tmp_path / "validation").mkdir()
    (tmp_path / "analysis" / "tables").mkdir(parents=True)
    rows = [
        row("share_c2", "56.4%", "0.5638", "share", "C2", "C2", "PASS"),
        row("usd_pub", "$10.77T", "10.77", "usd_tn", "C3", "C3", "PASS", claim="Public held it"),
        row("usd_scope", "$19.10T", "19.1", "usd_tn", "C3", "C3", "PASS", claim="Scope totalled"),
        row("share_edge", "56.2%", "0.56249", "share", "analysis/tables/e.csv share_t16 (2019Q4 = 0.5625, rounded to 4 d.p.)"),
        row("dotted", "$9.16T", "9.16", "usd_tn", "analysis/results.json public_book.public_mortgage_latest_busd"),
        row("expr", "29%", "0.29", "share", "analysis/results.json gfc_dollars_busd: public_t16 / public_t0 - 1"),
        row("listkey", "98th percentile", "98.2", "pct_rank", "analysis/results.json windows[2007Q4].percentile_among_all_windows"),
        row("csvrow", "+7.0 pp", "7.0", "pp", "analysis/tables/w.csv fwd16_pp (1990Q3)", loc="doc.md:5"),
        row("csvrow2", "+7.0 pp", "7.0", "pp", "analysis/tables/w.csv prior16_pp (1990Q3)", loc="doc.md:6"),
        row("jsonsum", "$4.6T", "4.61", "usd_tn", "d.json: sum(real_musd) where bucket='pls' and date='2006-12-31'"),
        row("stale", "60.0%", "0.5", "share", "analysis/results.json bad_share", validation="STALE"),
        row("nocomp", "12.5%", "0.125", "share", "external description, not computed"),
        row("dup_a", "24.6%", "0.246", "share", "analysis/results.json dup", claim="A"),
        row("dup_b", "24.6%", "0.246", "share", "analysis/results.json dup", claim="B"),
    ]
    with (tmp_path / "claims" / "register.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, COLS); w.writeheader(); w.writerows(rows)
    checks = [
        {"id": "C2", "description": "Public share 2026Q2", "observed": "56.38%", "status": "PASS"},
        {"id": "C3", "description": "Public $ and scope 2026Q2", "observed": "$10.768T of $19.097T", "status": "PASS"},
    ]
    (tmp_path / "validation" / "results.json").write_text(json.dumps({"checks": checks}))
    (tmp_path / "analysis" / "results.json").write_text(json.dumps({
        "edge_share": 0.5625, "bad_share": 0.4, "dup": 0.246,
        "public_book": {"public_mortgage_latest_busd": 9162.5},
        "gfc_dollars_busd": {"public_t0": 4762.4, "public_t16": 6158.1},
        "windows": [{"crisis": "2007Q4", "percentile_among_all_windows": 0.982}],
    }))
    (tmp_path / "analysis" / "tables" / "w.csv").write_text("crisis,fwd16_pp,prior16_pp\n1990Q3,7.04,6.96\n")
    (tmp_path / "analysis" / "tables" / "e.csv").write_text("crisis,share_t0,share_t16\n2019Q4,0.5,0.5625\n")
    (tmp_path / "d.json").write_text(json.dumps([
        {"date": "2006-12-31", "bucket": "pls", "real_musd": 2000000.5},
        {"date": "2006-12-31", "bucket": "pls", "real_musd": 2608000.0},
        {"date": "2006-12-31", "bucket": "other", "real_musd": 9},
    ]))
    (tmp_path / "doc.md").write_text("line1\n\n\n\n+7.0 pp here\n+7.0 pp there\n")
    return cc.Ctx(root=tmp_path)


def verdict(ctx, text):
    items = [i for n, t, r in [(1, text, None)] for i in cc.check_line(t, n, ctx, None)]
    return items


def v1(ctx, text):
    items = verdict(ctx, text)
    assert len(items) == 1, items
    return items[0]


def test_match_via_check(ctx):
    it = v1(ctx, "Share is 56.4%.")
    assert it["verdict"] == "MATCH" and it["rows"][0]["recompute"]["status"] == "ok"
    assert it["rows"][0]["check_id"] == "C2"


def test_a_of_b_pairing(ctx):
    items = verdict(ctx, "$10.77T of $19.10T")
    assert [i["verdict"] for i in items] == ["MATCH", "MATCH"]
    assert items[1]["rows"][0]["recompute"]["value_token_units"].startswith("19.09")


def test_untraced(ctx):
    it = v1(ctx, "Public holders own 61.2% in 2026Q2.")
    assert it["verdict"] == "UNTRACED"
    assert any(r["claim_id"] == "share_c2" for r in it["related"])  # a lead, never a match


def test_mismatch_register_stale(ctx):
    it = v1(ctx, "It is 60.0% now.")
    j = it["rows"][0]
    assert it["verdict"] == "MISMATCH"
    assert any("recompute 40" in n for n in j["notes"]) and any("rounds to 50" in n for n in j["notes"])


def test_ambiguous_then_pinned_by_location(ctx):
    it = v1(ctx, "24.6% of debt")
    assert it["verdict"] == "AMBIGUOUS" and {r["claim_id"] for r in it["rows"]} == {"dup_a", "dup_b"}
    its = cc.check_line("+7.0 pp here", 5, ctx, "doc.md")
    assert its[0]["verdict"] == "MATCH" and its[0]["rows"][0]["claim_id"] == "csvrow"
    assert cc.check_line("+7.0 pp there", 6, ctx, "doc.md")[0]["rows"][0]["claim_id"] == "csvrow2"
    assert v1(ctx, "+7.0 pp")["verdict"] == "AMBIGUOUS"   # plain text has no location to pin it


def test_not_recomputable_never_guesses(ctx):
    it = v1(ctx, "About 12.5% of it.")
    assert it["verdict"] == "NOT RECOMPUTABLE" and it["rows"][0]["recompute"]["status"] == "none"


def test_rounding_edge_half_up(ctx):
    # register 0.56249 -> 56.249 -> 56.2; the 4-d.p. source 0.5625 cannot settle it (56.25 half-up is 56.3)
    it = v1(ctx, "56.2%")
    assert it["verdict"] == "MATCH"
    assert any("edge case" in n for n in it["rows"][0]["notes"])
    assert cc.round_hu(cc.Decimal("56.25"), 1) == cc.Decimal("56.3")
    assert cc.round_hu(cc.Decimal("56.249"), 1) == cc.Decimal("56.2")


def test_share_fraction_converted_to_percent(ctx):
    rc = v1(ctx, "29% growth")["rows"][0]["recompute"]       # 6158.1/4762.4 - 1 = 0.2931 -> 29.31 percent
    assert rc["status"] == "ok" and rc["value_token_units"].startswith("29.3")
    assert v1(ctx, "29% growth")["verdict"] == "MATCH"


def test_dotted_key_and_unit_conversion(ctx):
    it = v1(ctx, "$9.16T of mortgages")     # public_book.public_mortgage_latest_busd = 9162.5 $B -> 9.1625 $T
    assert it["verdict"] == "MATCH" and it["rows"][0]["recompute"]["value_token_units"].startswith("9.16")


def test_list_key_and_percent_rank(ctx):
    it = v1(ctx, "the 98th percentile")      # windows[2007Q4].pct = 0.982 -> 98.2
    assert it["verdict"] == "MATCH"


def test_json_sum_where(ctx):
    it = v1(ctx, "about $4.6T")              # (2000000.5 + 2608000.0) $M = 4.6080 $T
    assert it["verdict"] == "MATCH" and it["rows"][0]["recompute"]["value_token_units"].startswith("4.6080")


def test_recompute_mismatch_reported_with_size(ctx):
    (ctx.root / "analysis" / "tables" / "e.csv").write_text("crisis,share_t0,share_t16\n2019Q4,0.5,0.6000\n")
    it = v1(ctx, "56.2%")
    assert it["verdict"] == "MISMATCH" and "off by 3.8" in " ".join(it["rows"][0]["notes"])


def test_cli_exit_codes_and_json(ctx, capsys):
    base = ["--root", str(ctx.root)]
    assert cc.main(base + ["Share is 56.4%."]) == 0
    assert cc.main(base + ["Public holders own 61.2%."]) == 1
    assert cc.main(base + ["It is 60.0% now."]) == 1
    assert cc.main(base + ["About 12.5% of it."]) == 0
    assert cc.main(base) == 2
    assert cc.main(base + ["x", "--file", "doc.md"]) == 2
    capsys.readouterr()
    assert cc.main(base + ["--json", "56.4%"]) == 0
    assert json.loads(capsys.readouterr().out)["summary"] == {"MATCH": 1}
    assert cc.main(base + ["--file", "doc.md", "--line", "5"]) == 0
    assert cc.main(base + ["--file", "doc.md"]) == 0
    assert cc.main(base + ["--file", "nope.md"]) == 2


def test_never_writes(ctx):
    before = {p: p.read_bytes() for p in ctx.root.rglob("*") if p.is_file()}
    cc.main(["--root", str(ctx.root), "56.4% and 60.0% and 61.2%"])
    assert before == {p: p.read_bytes() for p in ctx.root.rglob("*") if p.is_file()}
