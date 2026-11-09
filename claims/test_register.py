"""pytest wrapper for claims/check_register.py.

    uv run --project pipeline pytest claims/test_register.py

The first two tests fail when the real register is invalid or a published number has no row.
The rest are unit tests of the matcher on synthetic text and synthetic registers.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_register as cr  # noqa: E402


def test_register_is_valid():
    errors, rows = cr.validate_register()
    assert not errors, "\n".join(errors)
    assert rows, "register is empty"


def test_every_published_number_has_a_register_row():
    _, rows = cr.validate_register()
    unmatched = cr.scan_files(rows)
    assert not unmatched, "\n".join(f"{f}:{n}  {t!r}" for f, n, t in unmatched)


def test_spelling_variants_normalise_to_one_token():
    same = ["+13.1 pp", "13.1 pts", "−13.1 points", "13.1 point"]
    assert len({cr.normalize(s) for s in same}) == 1
    assert cr.normalize("3.56×") == cr.normalize("3.56x")
    assert cr.normalize("$19 trillion") == cr.normalize("$19T")
    assert cr.normalize("56.4%") != cr.normalize("56%")  # rounding differences are different claims
    assert cr.normalize("p ≈ 0.30") == cr.normalize("p ≈ .30")


def test_extract_tokens_finds_numbers_but_not_years_or_ids():
    line = "From 2007Q4 to 2011Q4 (FL153165105) the share rose +13.1 pp, 5 of 11, $10.77T, p ≈ 0.30, 98th, 3.56×."
    toks = [cr.normalize(t) for t in cr.extract_tokens(line)]
    assert toks == ["13.1pp", "5of11", "$10.77t", "p≈.30", "98th", "3.56x"]


def test_scan_flags_unregistered_number_and_respects_allowlist_and_code():
    covered = cr.register_tokens(["56.4%", "+13.1 pp | 13 points"])
    md = "Share is 56.4%, up 13 points but also 61.2%.\n`7.7%` in code\n```\n9.9%\n```\nSee the 20th of March.\n"
    bad = cr.scan_text("README.md", md, covered)
    assert bad == [(1, "61.2%")] or [t for _, t in bad] == ["61.2%"]
    assert all(t != "20th" for _, t in bad)  # allowlisted for README.md
    assert cr.scan_text("other.md", "the 20th", covered) == [(1, "20th")]  # allowlist is per file


def test_typescript_comments_are_not_published_copy():
    covered = cr.register_tokens(["56.4%"])
    ts = "// e.g. 99.9%\nconst a = \"56.4%\"; // 88.8%\nconst b = \"12.3%\";\n"
    assert [t for _, t in cr.scan_text("x/story.ts", ts, covered)] == ["12.3%"]


def _write(tmp: Path, rows: list[dict]):
    p = tmp / "register.csv"
    with p.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cr.SCHEMA, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cr.SCHEMA})
    return p


def _row(**kw):
    base = dict(claim_id="a_b", claim="c", display="1.0%", value="0.01", unit="share", period="2026Q2",
                locations="README.md:1", computation="C2", series_ids="X", vintage="z1:2026-09-11",
                validation="UNVERIFIED", check_id="", notes="")
    return base | kw


@pytest.mark.parametrize("bad,fragment", [
    (dict(validation="MAYBE"), "not in"),
    (dict(validation="PASS", check_id=""), "needs a check_id"),
    (dict(validation="PASS", check_id="ZZ99"), "not in validation/results.json"),
    (dict(validation="UNVERIFIED", check_id="C2"), "must be empty"),
    (dict(locations="README.md:99999"), "outside the file"),
    (dict(value="abc"), "not numeric"),
    (dict(claim_id="Bad Id"), "not a slug"),
])
def test_register_validation_catches_bad_rows(tmp_path, bad, fragment):
    errors, _ = cr.validate_register(register=_write(tmp_path, [_row(**bad)]))
    assert any(fragment in e for e in errors), errors


def test_duplicate_ids_and_status_disagreement(tmp_path):
    p = _write(tmp_path, [_row(), _row(), _row(claim_id="c_d", validation="FAIL", check_id="C2")])
    errors, _ = cr.validate_register(register=p)
    assert any("duplicate claim_id" in e for e in errors)
    assert any("row says FAIL but validation/results.json says C2 is PASS" in e for e in errors)


def test_drifted_location_is_caught(tmp_path):
    """A location whose line no longer shows the number fails (lines inserted above it)."""
    import shutil
    import check_register as cr
    root = tmp_path
    (root / "claims").mkdir()
    (root / "doc.md").write_text("intro\nThe share is 56.4% now.\n")
    reg = root / "claims" / "register.csv"
    head = ",".join(cr.SCHEMA)
    row = "x,c,56.4%,0.564,share,2026Q2,doc.md:{ln},calc,FL1,z1:2026-09-11,UNVERIFIED,,"
    reg.write_text(head + "\n" + row.format(ln=2) + "\n")
    shutil.copy(cr.VALIDATION_RESULTS, root / "results.json")
    errs, _ = cr.validate_register(root=root, register=reg, results_path=root / "results.json")
    assert not [e for e in errs if "drifted" in e]
    reg.write_text(head + "\n" + row.format(ln=1) + "\n")
    errs, _ = cr.validate_register(root=root, register=reg, results_path=root / "results.json")
    assert [e for e in errs if "drifted" in e]


def test_line_cited_files_need_a_row_citing_the_line(tmp_path):
    """In LINE_CITED_FILES a matching display elsewhere is not enough (docket 51 findings-scan (a))."""
    import check_register as cr
    (tmp_path / "f.md").write_text("Share is 56.4% now.\nAnd 56.4% again.\n")
    rows = [{"display": "56.4%", "locations": "f.md:1"}]
    assert cr.scan_files(rows, root=tmp_path, scan_files_=["f.md"], line_cited={"f.md"}) == [("f.md", 2, "56.4%")]
    assert cr.scan_files(rows, root=tmp_path, scan_files_=["f.md"], line_cited=set()) == []
    rows.append({"display": "56.4%", "locations": "other.md:9;f.md:2"})
    assert cr.scan_files(rows, root=tmp_path, scan_files_=["f.md"], line_cited={"f.md"}) == []
    assert "analysis/findings.md" in cr.LINE_CITED_FILES
