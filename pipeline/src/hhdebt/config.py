"""Paths, catalog and static dimensions (crises)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

PIPELINE_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = PIPELINE_DIR.parent
CATALOG_PATH = PIPELINE_DIR / "series_catalog.yaml"
DATA_DIR = Path(os.environ.get("HHDEBT_DATA_DIR", REPO_ROOT / "data"))
STAGING_DIR = DATA_DIR / "staging"      # extract output: one long CSV per source
OUT_DIR = DATA_DIR / "out"              # transform output: one CSV per core/mart table
SNAPSHOT_DIR = REPO_ROOT / "web" / "public" / "data"
MIGRATIONS_DIR = REPO_ROOT / "supabase" / "migrations"

Z1_ZIP_URL = "https://www.federalreserve.gov/releases/z1/data/FRB_Z1_csv.zip"
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={id}"
FRED_API_URL = "https://api.stlouisfed.org/fred"
NYFED_PAGE_URL = "https://www.newyorkfed.org/microeconomics/hhdc"
NYFED_XLSX_URL = (
    "https://www.newyorkfed.org/medialibrary/interactives/householdcredit/data/xls/HHD_C_Report_{yq}.xlsx"
)
HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; hhdebt-pipeline/0.1; +https://github.com/)"}

# Crisis-event window offsets (quarters), must match mart.crisis_event_window check constraint.
WINDOW_MIN, WINDOW_MAX = -8, 16


@lru_cache
def catalog() -> dict:
    with open(CATALOG_PATH) as f:
        return yaml.safe_load(f)


def series(source: str | None = None, role: str | None = None) -> list[dict]:
    out = catalog()["series"]
    if source:
        out = [s for s in out if s["source"] == source]
    if role:
        out = [s for s in out if s["role"] == role]
    return out


def series_ids(source: str | None = None, role: str | None = None) -> list[str]:
    return [s["id"] for s in series(source, role)]


def risk_buckets() -> dict[str, dict]:
    return catalog()["risk_buckets"]


def public_buckets() -> list[str]:
    return [k for k, v in risk_buckets().items() if v["public"]]


def collateral_classes() -> dict[str, dict]:
    return catalog()["collateral_classes"]


@dataclass(frozen=True)
class Crisis:
    crisis_id: str
    name: str
    kind: str          # nber_recession | policy_shock
    start_q: str       # quarter label, e.g. "2007Q4"
    end_q: str | None
    notes: str | None = None


# NBER peak/trough quarters; policy shocks have no end quarter.
CRISES: list[Crisis] = [
    Crisis("recession_1953", "1953-54 recession", "nber_recession", "1953Q2", "1954Q2", "Post-Korean War recession"),
    Crisis("recession_1957", "1957-58 recession", "nber_recession", "1957Q3", "1958Q2", "Eisenhower recession"),
    Crisis("recession_1960", "1960-61 recession", "nber_recession", "1960Q2", "1961Q1", None),
    Crisis("recession_1969", "1969-70 recession", "nber_recession", "1969Q4", "1970Q4", None),
    Crisis("oil_shock_1973", "1973-75 recession (oil shock)", "nber_recession", "1973Q4", "1975Q1", "OPEC oil embargo, stagflation"),
    Crisis("recession_1980", "1980 recession", "nber_recession", "1980Q1", "1980Q3", "Volcker tightening, credit controls"),
    Crisis("volcker_1981", "1981-82 recession", "nber_recession", "1981Q3", "1982Q4", "Volcker double-dip"),
    Crisis("sl_1990", "1990-91 recession (S&L crisis)", "nber_recession", "1990Q3", "1991Q1", "Savings & loan crisis, Gulf War oil shock"),
    Crisis("dotcom_2001", "2001 recession (dot-com)", "nber_recession", "2001Q1", "2001Q4", "Dot-com bust, 9/11"),
    Crisis("gfc_2007", "Great Recession (GFC)", "nber_recession", "2007Q4", "2009Q2", "Subprime / global financial crisis; GSE conservatorship Sep 2008"),
    Crisis("covid_2020", "COVID-19 recession", "nber_recession", "2019Q4", "2020Q2", "NBER peak Feb 2020 (2019Q4 quarterly peak), trough Apr 2020"),
    Crisis("cares_forbearance_2020", "CARES Act forbearance & student-loan pause", "policy_shock", "2020Q1", None,
           "Mortgage forbearance and federal student-loan payment pause (March 2020)"),
    Crisis("student_repayment_2023", "Student-loan repayment restart", "policy_shock", "2023Q4", None,
           "Federal student-loan payments resumed Oct 2023 (on-ramp period through Sep 2024)"),
    Crisis("student_collections_2025", "Student-loan collections & credit re-reporting restart", "policy_shock", "2025Q2", None,
           "Collections on defaulted federal student loans and credit re-reporting resumed May 2025"),
]


def database_url() -> str | None:
    return os.environ.get("DATABASE_URL") or None
