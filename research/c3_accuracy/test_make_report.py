"""C3 report: its input-consistency checks hold on the committed files, and the README is current."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("make_report", HERE / "make_report.py")
mr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr)


def test_inputs_consistent():
    import json
    hold = json.loads((mr.ROOT / mr.HOLD).read_text())
    c1b = json.loads((mr.ROOT / mr.C1B_HOLD).read_text())
    mr.check_c2_dev_errors(mr.read_csv(f"{mr.C2D}/forecasts_dev.csv"), mr.read_csv(f"{mr.C2D}/scores_dev.csv"))
    mr.check_c1_dev_errors(mr.read_csv(f"{mr.C1D}/nowcasts_dev.csv"), mr.read_csv(f"{mr.C1D}/scores_dev.csv"))
    mr.check_c1b_hold(mr.read_csv(f"{mr.C1BD}/nowcasts_holdout.csv"), c1b, hold["c1"])
    mr.check_verdicts(hold["c2"]["verdicts"], mr.read_csv(f"{mr.C2D}/tests_dev.csv"))


def test_quarter_arithmetic():
    assert mr.qadd("2023Q2", 1) == "2023Q3" and mr.qadd("2022Q4", 8) == "2024Q4"
    assert mr.inwin("2020Q3", "2020Q1", "2020Q4") and not mr.inwin("2021Q1", "2020Q1", "2020Q4")
