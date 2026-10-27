"""`hhdebt` command line: run | extract | transform | load | export-snapshot | export-tableau."""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from . import config


def _load_dotenv() -> None:
    """Minimal .env loader (repo root), never overriding variables already set."""
    path = config.REPO_ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"').strip("'")
        if v:
            os.environ.setdefault(k.strip(), v)


def cmd_extract(a) -> None:
    from .extract import fred, nyfed, z1
    sources = a.sources or ["z1", "fred", "nyfed"]
    if "z1" in sources:
        z1.run(zip_path=a.z1_zip, csv_path=a.z1_csv, force_download=a.force_download)
    if "fred" in sources:
        fred.run()
    if "nyfed" in sources:
        try:
            nyfed.run(xlsx_path=a.nyfed_xlsx)
        except Exception:
            if a.strict:
                raise
            logging.exception("nyfed extract failed; continuing without it (use --strict to fail)")


def cmd_transform(a) -> None:
    from . import transform
    transform.run()


def cmd_load(a) -> None:
    from . import load
    load.run()


def cmd_export(a) -> None:
    from . import export
    export.run(source=a.source)


def cmd_export_tableau(a) -> None:
    from . import tableau_export
    tableau_export.run(source=a.source)


def cmd_run(a) -> None:
    cmd_extract(a)
    cmd_transform(a)
    if config.database_url() and not a.no_load:
        cmd_load(a)
    else:
        logging.warning("DATABASE_URL not set (or --no-load): skipping load")
    if a.export:
        cmd_export(a)
        cmd_export_tableau(a)


def main(argv: list[str] | None = None) -> None:
    _load_dotenv()
    p = argparse.ArgumentParser(prog="hhdebt", description="Who Holds the Debt? data pipeline")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    def extract_args(sp):
        sp.add_argument("--sources", nargs="+", choices=["z1", "fred", "nyfed"], help="default: all")
        sp.add_argument("--z1-zip", type=Path, help="use this local FRB_Z1_csv.zip instead of downloading")
        sp.add_argument("--z1-csv", type=Path, help="use an unzipped Z1.csv (dev cache; also env HHDEBT_Z1_CSV)")
        sp.add_argument("--force-download", action="store_true", help="re-download the Z.1 zip")
        sp.add_argument("--nyfed-xlsx", type=Path, help="use this local HHD_C_Report_*.xlsx")
        sp.add_argument("--strict", action="store_true", help="fail if the NY Fed extract fails")

    sp = sub.add_parser("run", help="extract -> transform -> load (if DATABASE_URL) [-> export-snapshot]")
    extract_args(sp)
    sp.add_argument("--no-load", action="store_true")
    sp.add_argument("--export", action="store_true", help="also write web/public/data snapshots and tableau/data CSVs")
    sp.add_argument("--source", default="auto", choices=["auto", "db", "local"], help=argparse.SUPPRESS)
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("extract", help="download sources -> data/staging/<source>.csv")
    extract_args(sp)
    sp.set_defaults(func=cmd_extract)

    sub.add_parser("transform", help="data/staging -> data/out (core + mart tables)").set_defaults(func=cmd_transform)
    sub.add_parser("load", help="upsert raw, replace core + mart (one transaction)").set_defaults(func=cmd_load)

    sp = sub.add_parser("export-snapshot", help="write web/public/data/<table>.json")
    sp.add_argument("--source", default="auto", choices=["auto", "db", "local"],
                    help="auto = database if DATABASE_URL is set, else data/out")
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("export-tableau", help="write tableau/data/<dashboard>.csv (flat, pre-joined)")
    sp.add_argument("--source", default="auto", choices=["auto", "db", "local"],
                    help="auto = database if DATABASE_URL is set, else data/out")
    sp.set_defaults(func=cmd_export_tableau)

    a = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    a.func(a)


if __name__ == "__main__":
    main()
