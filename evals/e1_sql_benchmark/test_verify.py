import csv
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("e1_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def test_pilot_gold_answers_verify():
    res = verify.verify()
    assert len(res) == 10
    assert all(r["ok"] for r in res), [r for r in res if not r["ok"]]


def test_disagreement_is_caught(tmp_path):
    rows = list(csv.DictReader(verify.REGISTER.open()))
    for r in rows:
        if r["claim_id"] == "public_share_2026q2":
            r["value"] = "0.5700"
        if r["claim_id"] == "gfc_jump_pp":
            r["validation"] = "UNVERIFIED"
    bad = tmp_path / "register.csv"
    with bad.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    res = {r["id"]: r for r in verify.verify(register=bad)}
    assert not res["q01"]["ok"] and not res["q09"]["ok"]
    assert sum(not r["ok"] for r in res.values()) == 2


def test_precision():
    assert abs(verify.precision("0.5638") - 0.00005) < 1e-12
    assert abs(verify.precision("19.1") - 0.05) < 1e-12
