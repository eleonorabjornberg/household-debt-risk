"""C1b: Freddie lookup (as-of rule, single-report growth), the cell scaling, the MVS table parser. Offline."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


c1b = _load("c1b_nowcast", HERE / "nowcast_c1b.py")
mvs = _load("freddie_mvs", HERE / "freddie_mvs.py")

REP = pd.DataFrame({"report_month": ["2019-12", "2020-01", "2020-02"],
                    "pub_date": ["2020-01-23", "2020-02-24", "2020-03-25"],
                    "content_label": ["", "content possibly revised", ""]})
ROWS = pd.DataFrame({"report_month": ["2019-12", "2020-01", "2020-01", "2020-02", "2020-02", "2020-02"],
                     "row_month": ["2019-12", "2019-12", "2020-01", "2019-12", "2020-01", "2020-02"],
                     # the Feb report restates Dec (definition change): growth must come from one report only
                     "ending_balance_usd_m": [100.0, 100.0, 102.0, 110.0, 112.2, 115.5]})
FR = c1b.Freddie(REP.replace("", np.nan), ROWS)


def test_no_new_month_gives_growth_one():
    f = FR.at("2020-02-15", "2019Q4", "2020Q1")        # only the Dec report is out
    assert f["report"] == "2019-12" and f["g"] == 1.0 and f["F_T"] == 100.0


def test_report_published_on_t_is_not_used():
    assert FR.at("2020-02-24", "2019Q4", "2020Q1")["report"] == "2019-12"
    assert FR.at("2020-02-25", "2019Q4", "2020Q1")["report"] == "2020-01"


def test_growth_from_a_single_report():
    f = FR.at("2020-04-15", "2019Q4", "2020Q1")
    assert f["report"] == "2020-02" and f["F_T"] == 110.0
    assert f["g"] == pytest.approx(115.5 / 110.0)       # not 115.5 / 100 across reports
    assert FR.at("2020-03-15", "2019Q4", "2020Q1")["report_label"] == "content possibly revised"


def test_no_report_before_t_raises():
    with pytest.raises(ValueError):
        FR.at("2019-12-31", "2019Q3", "2019Q4")


CELLS = {("mortgages", "public", "mort_gse"): 100.0, ("mortgages", "public", "mort_pools"): 900.0,
         ("mortgages", "private", "mort_banks"): 1000.0, ("mortgages", "private", "mort_other_private"): 500.0,
         ("consumer credit", "public", "cc_federal"): 300.0, ("consumer credit", "private", "cc_depository"): 400.0,
         ("consumer credit", "private", "cc_other_private"): 300.0}
G1 = {k: 1.0 for k in ["TOTALGOV", "TOTALDI", "TOTALFC", "TOTALTCU", "TOTALNS", "RREACBW027NBOG"]}
MAP = {"cc_federal": "TOTALGOV", "cc_depository": "TOTALDI", "mort_banks": "RREACBW027NBOG"}


def test_growth_one_reproduces_c1_bridge():
    sh, s = c1b.c1b_share(CELLS, G1, {"F_T": 400.0, "g": 1.0}, MAP)
    assert sh == pytest.approx(c1b.nc.bridge_share(CELLS, G1, 1.0, MAP)) and s == pytest.approx(0.4)


def test_scaling_and_cap():
    sh, s = c1b.c1b_share(CELLS, G1, {"F_T": 400.0, "g": 1.1}, MAP)
    pub = 1000 * (1 + 0.4 * 0.1) + 300
    assert sh == pytest.approx(pub / (pub + 1500 + 700))
    _, s = c1b.c1b_share(CELLS, G1, {"F_T": 5000.0, "g": 1.0}, MAP)
    assert s == 1.0


def test_table1_parser_infers_missing_first_year():
    text = ("TABLE 1 - TOTAL MORTGAGE PORTFOLIO\nNov 1 (2) (3) 4 1,000 1% 2%\nDec 1 (2) (3) 4 1,010 1% 2%\n"
            "Full-Year 2016 $1 ($2) ($3) $4 $1,010 1% 2%\nJan 2017 1 (2) (3) 4 1,020 1% 2%\n"
            "Feb 1 - (3) 4 1,030 1% 2%\nTABLE 2 - X\n")
    assert mvs.table1_rows(text, "2017-02") == [("2016-11", 1000.0), ("2016-12", 1010.0), ("2017-01", 1020.0),
                                               ("2017-02", 1030.0)]
    with pytest.raises(ValueError):
        mvs.table1_rows(text.replace("Jan 2017", "Jan 2018"), "2017-02")


def test_paired_t_and_verdict():
    d = np.array([1.0, 2.0, 3.0, 4.0])
    stat, p = c1b.paired_t_hln(d)
    assert stat == pytest.approx(2.5 / np.sqrt(1.25 / 4) * np.sqrt(3 / 4)) and 0 < p < 1
