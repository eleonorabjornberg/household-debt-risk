#!/usr/bin/env python3
"""Generate the Tableau Public starter workbook for "Who Holds the Debt?".

    python3 -I tableau/build_workbook.py            # writes WhoHoldsTheDebt.twb and .twbx
    python3 -I tableau/build_workbook.py --check    # also re-reads both with tableaudocumentapi, if installed
    python3 -I tableau/build_workbook.py --corpus DIR   # also checks sibling order against real .twb files in DIR

Stdlib only. Outputs (next to this file):
  WhoHoldsTheDebt.twb    the XML workbook; its text-file connection points at the relative folder Data/data
  WhoHoldsTheDebt.twbx   zip: WhoHoldsTheDebt.twb at the root + Data/data/*.csv (self-contained; open this one)

v1/v2 contents: data source `ratchet` (ratchet.csv), worksheets "Ratchet – main" (stacked area of
SUM(share_of_total) by bucket_label over the continuous quarter) and "Public share" (line of
AVG(public_share)), and dashboard "Ratchet" (1000x700, title, both sheets, colour legend).
v3 adds (names fixed by INTEGRATION_CONTRACT.md):
  * ratchet.csv columns `recession` (0/1) and `crisis_id`;
  * a string list parameter `Active crisis` (default "none") in a Parameters datasource;
  * calcs `Band` = IF [recession] = 1 THEN 1 END and `Is active crisis` = [crisis_id] = [Parameters].[Active crisis];
  * on "Ratchet – main", a dual axis (AVG(Band) + SUM(Share of total)): grey full-width recession bars
    (darker for the active crisis) drawn BEHIND the coloured areas, axes synchronised at 0-1, the second
    axis hidden;
  * still NO sort element: the Descending stack order stays a manual step (GETTING_STARTED.md).
  * figures 2-4 as dashboards CrisisSmallMultiples / Collateral / PaymentPriority (exact names: the site embeds
    views/WhoHoldsTheDebt/<name>), each on its own packaged text source, built only from single-measure
    line/area panes, discrete dimensions crossed with the measure on Rows, and single-member categorical filters;
  * every dashboard uses <size sizing-mode='automatic' /> (was fixed 1000x700).
  Provenance of each v3 element is in the comment next to the code that writes it (V3 SOURCES below).
Tableau requires unique names across worksheets and dashboards, so the area sheet cannot also be
called "Ratchet"; the dashboard owns that name because the site embeds views/WhoHoldsTheDebt/Ratchet.

XML provenance. No Tableau software runs where this was written, so every element and attribute here
was copied from real Tableau-written workbooks and cross-checked element by element:
  * Primary model (version 18.1 packaged workbook with a relative-directory textscan connection,
    metadata-records, area/line panes, palette colour maps in the datasource <style>, dashboard zones
    including text and colour-legend zones, windows/cards):
    https://github.com/tableau/document-api-python/blob/master/samples/show_workbook_info/geocoding.twbx
    (SuperstoreWithCustomGeocoding.twb, "Sales Commission" datasource:
     <connection class='textscan' directory='Data/Superstore' filename='Sales Commission.csv' .../>)
  * Header/build string, fixed dashboard <size>, layout-basic zones, worksheet <window> cards:
    https://github.com/tableau/document-api-python/blob/master/test/assets/filtering.twb
  * Legacy (pre-object-model) plain <relation connection=...> inside a federated connection:
    https://github.com/tableau/document-api-python/blob/master/test/assets/multiple_connections.twb
Those 18.1 files also carry a <document-format-change-manifest> and doubled "_.fcp.<Feature>.true..."/
"_.fcp.<Feature>.false..." attributes. We deliberately write NO manifest and only the plain (feature-off,
"false...") forms, i.e. the layout every pre-2019 workbook uses; Tableau upgrades such files on open.
The one name not seen verbatim in the examples is the quarter truncation derivation
'Quarter-Trunc' / instance prefix 'tqr', inferred from the examples' 'Month-Trunc'/'tmn',
'Week-Trunc'/'twk' and 'Year-Trunc'/'tyr'.

V3 SOURCES (all real Tableau-written files; "LS" = https://github.com/tableau/Logshark/blob/main/LogShark/Workbooks/,
"TSI" = https://github.com/tableau/community-tableau-server-insights/blob/master/datasources/):
  [P] Parameters datasource + string list parameter + its copy in a view's datasource-dependencies, and
      calc formulas reading [Parameters].[...]: geocoding.twbx above ("Sort by", param-domain-type='list',
      <members>), and TSI ts_events/ts_events_04.02.twb (18.1, build 2025.1.0: "Tableau Server Protocol").
      In every one of 88 18.1 views that use a parameter, <datasources> lists the data source then
      'Parameters', and datasource-dependencies list 'Parameters' first; at workbook level 'Parameters' is
      the first <datasource> (31 of 31 18.1 files that have one).
  [S] (researched, NOT written in v3) <sort class='computed' column=... direction=... using='[ds].[min:...:qk]'/> directly after
      datasource-dependencies and before <aggregation>: document-api-python
      samples/replicate-workbook/sample-superstore.twb (exact placement), LS DataServer.twbx (build 2020.2.2,
      using a [min:...] instance), and RESTAPISample.twb in tableau/server-client-python test/assets (sort on a
      field that is only on Color). 18.1 files written with the 'SortTagCleanup' entry in a
      <document-format-change-manifest> spell it <computed-sort>/<manual-sort>; we write no manifest, and the
      D2E8DA72 error Tableau gave for v1 lists exactly this content model:
      (datasources?,mapsources?,datasource-dependencies*,filter,sort,perspectives,slices?,aggregation).
      All 102 computed sorts in the corpus declare their 'using' instance in datasource-dependencies.
  [D] dual axis: rows '(A + B)', panes id='1'/'2' with y-axis-name, and in the axis style-rule
      <encoding ... fold='true' scope='rows' synchronized='true' type='space'/> on the second measure:
      LS ClusterController.twbx "Disk Space Used" (18.1, build 2022.3.22, continuous time on cols).
      Fixed range on the first measure next to the synchronised second one: LS ServerTelemetry.twbx
      "Session Comparison" (range-type='fixedmin' + fold/synchronized in one style-rule).
      Hidden axis <format attr='display' class=... field=... scope='rows' value='false'/>:
      LS Hyper.twbx "Total Queries Donut Chart" (18.1, build 2023.3.12). Axis title
      <format attr='title' class='0' field=... scope=... value=.../>: ServerTelemetry as above.
      Different mark class per pane with a pane-level <style><style-rule element='mark'> holding
      'mark-transparency': ServerTelemetry "Session Comparison" (Bar + Circle, transparency 126).
      Dashboard colour-legend zone of a dual-axis sheet: pane-specification-id = the id of the pane that
      carries the colour encoding (LS ResourceManager.twbx, legend -> pane 8 of panes 7/8/9).
  [B] Bar on a continuous truncated date sized to the date interval:
      <mark-sizing custom-mark-size-in-axis-units='1.0' mark-alignment='mark-alignment-left'
      mark-sizing-setting='marks-scaling-on' use-custom-mark-size='false'/>: LS Apache.twbx
      "Count of Viz Loads Per Day" (18.1, 2022.3.22) and TSI ts_background_tasks_04.02.twb (18.1, 2025.1.0).
  [C] Calculated fields '[Calculation_<digits>]' with caption + <calculation class='tableau' formula=.../>,
      boolean dimension calcs (datatype='boolean' role='dimension' type='nominal'), and palettes for a
      boolean field written as <bucket>true</bucket>/<bucket>false</bucket> (unquoted): TSI
      ts_content_04.02.twb and VizAlerts config/VizAlertsConfig.twb.
  Draw order: the measure listed second in a dual axis is drawn on top, so Band comes first in rows.

Column names come from pipeline/src/hhdebt/tableau_export.py COLUMNS["ratchet"]; the script checks the
CSV header against them and fails loudly if they drift.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
TWB = HERE / "WhoHoldsTheDebt.twb"
TWBX = HERE / "WhoHoldsTheDebt.twbx"
PACKAGED_DIR = "Data/data"  # relative directory inside the .twbx, as in Tableau-packaged workbooks
CSV_FILES = ["ratchet.csv", "crisis_windows.csv", "collateral.csv", "payment_priority.csv", "crises.csv"]

# Real released 18.1 build string, copied from filtering.twb (Tableau 2021.1.2 still writes version 18.1).
BUILD = "20211.21.0511.0935"
SOURCE_BUILD = f"2021.1.2 ({BUILD})"
VERSION = "18.1"

TITLE = "Who holds US household debt? 1952–2026"
SHEET_MAIN = "Ratchet – main"
SHEET_PUBLIC = "Public share"
DASHBOARD = "Ratchet"

# Must equal COLUMNS["ratchet"] in pipeline/src/hhdebt/tableau_export.py (checked against the CSV header).
# name -> (tableau datatype, role, type, caption, default-format or None)
RATCHET_FIELDS = {
    "date": ("date", "dimension", "ordinal", "Date", None),
    "risk_bucket": ("string", "dimension", "nominal", "Risk bucket", None),
    "bucket_label": ("string", "dimension", "nominal", "Bucket label", None),
    "is_public": ("boolean", "dimension", "nominal", "Is public", None),
    "sort_order": ("integer", "measure", "quantitative", "Sort order", None),
    "debt_type": ("string", "dimension", "nominal", "Debt type", None),
    "nominal_musd": ("real", "measure", "quantitative", "Nominal $M", None),
    "real_musd": ("real", "measure", "quantitative", "Real $M", None),
    "share_of_total": ("real", "measure", "quantitative", "Share of total", "p0%"),
    "public_share": ("real", "measure", "quantitative", "Public share", "p0.0%"),
    "fed_mbs_share_of_scope": ("real", "measure", "quantitative", "Fed MBS share of scope", "p0.0%"),
    "recession": ("integer", "measure", "quantitative", "Recession", None),
    "crisis_id": ("string", "dimension", "nominal", "Crisis id", None),
}
# OLE DB type codes Tableau writes in <remote-type> (129/20 from geocoding.twbx's textscan source,
# 5 = R8 from its excel source; 133 = DBDATE -> local-type date as in samples/show_workbook_info/world.tds;
# 11 = BOOL as in geocoding.twbx's local-type boolean records).
REMOTE_TYPE = {"string": 129, "integer": 20, "real": 5, "date": 133, "boolean": 11}
DEFAULT_AGG = {"string": "Count", "integer": "Sum", "real": "Sum", "date": "Year", "boolean": "Count"}

# workbook_specs.md §0.2, keyed by the bucket_label values actually present in ratchet.csv.
BUCKET_COLORS = [  # (sort_order, risk_bucket, colour); labels are read from the CSV
    (1, "federal_direct", "#1c5cab"),
    (2, "gse_agency", "#1baf7a"),
    (3, "state_local", "#3987e5"),
    (4, "banks_credit_unions", "#e34948"),
    (5, "private_securitization", "#eda100"),
    (6, "nonbank_other", "#e87ba4"),
]


def tableau_id(seed: str, n: int = 28) -> str:
    """Deterministic lowercase base-36 id like Tableau's 'federated.0a01cod1oxl83l1f5yves1cfciqo'."""
    x = int(hashlib.sha1(seed.encode()).hexdigest(), 16)
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while len(out) < n:
        x, r = divmod(x, 36)
        out += digits[r]
    return out


DS = "federated." + tableau_id("hhdebt-ratchet-datasource")
CONN = "textscan." + tableau_id("hhdebt-ratchet-textscan")
DS_CAPTION = "ratchet"


# ---- v3: figures 2-4 (CrisisSmallMultiples, Collateral, PaymentPriority); names fixed by the site's embed paths
DASH_CRISIS, DASH_COLLATERAL, DASH_PAYMENT = "CrisisSmallMultiples", "Collateral", "PaymentPriority"
SHEET_CRISIS = "Crisis SM – main"
SHEET_COLL_SHARE = "Collateral – share"
SHEET_COLL_COVER = "Collateral – coverage"
SHEET_PAYMENT = "Payment priority – main"
OPEN_SHEET = "Public share"
SHEETS = [SHEET_MAIN, SHEET_PUBLIC, SHEET_CRISIS, SHEET_COLL_SHARE, SHEET_COLL_COVER, SHEET_PAYMENT]
CRISIS_FIELDS = {  # == tableau_export.COLUMNS["crisis_windows"]
    "crisis_id": ("string", "dimension", "nominal", "Crisis id", None),
    "crisis_name": ("string", "dimension", "nominal", "Crisis name", None),
    "kind": ("string", "dimension", "nominal", "Kind", None),
    "start_q": ("date", "dimension", "ordinal", "Start quarter", None),
    "metric": ("string", "dimension", "nominal", "Metric", None),
    # integer dimension used continuously: ordinal column + [none:...:qk] instance, like TSI's
    # '[none:Calculation_7300619133441268:qk]' on cols (ts_background_tasks_04.02.twb)
    "q_offset": ("integer", "dimension", "ordinal", "Quarters from t0", None),
    "date": ("date", "dimension", "ordinal", "Date", None),
    "value": ("real", "measure", "quantitative", "Value", None),
    "value_at_t0": ("real", "measure", "quantitative", "Value at t0", None),
    "delta_from_t0": ("real", "measure", "quantitative", "Change since t0", None),
}
COLLATERAL_FIELDS = {  # == tableau_export.COLUMNS["collateral"]
    "date": ("date", "dimension", "ordinal", "Date", None),
    "collateral_class": ("string", "dimension", "nominal", "Collateral class", None),
    "class_label": ("string", "dimension", "nominal", "Class label", None),
    "debt_musd": ("real", "measure", "quantitative", "Debt $M", None),
    "collateral_value_musd": ("real", "measure", "quantitative", "Collateral value $M", None),
    "coverage_ratio": ("real", "measure", "quantitative", "Coverage ratio", None),
    "share_of_debt": ("real", "measure", "quantitative", "Share of debt", "p0%"),
    "is_estimated": ("boolean", "dimension", "nominal", "Is estimated", None),
}
PCT = 'n#,##0.0"%";-#,##0.0"%"'  # values already in percent; format string as geocoding.twbx 'Commission Rate'
PAYMENT_FIELDS = {  # == tableau_export.COLUMNS["payment_priority"]
    "date": ("date", "dimension", "ordinal", "Date", None),
    "loan_type": ("string", "dimension", "nominal", "Loan type", None),
    "loan_label": ("string", "dimension", "nominal", "Loan label", None),
    "collateral_class": ("string", "dimension", "nominal", "Collateral class", None),
    "balance_busd": ("real", "measure", "quantitative", "Balance $B", None),
    "transition_serious_pct": ("real", "measure", "quantitative", "Into serious delinquency (%)", PCT),
    "baseline_2003_06_pct": ("real", "measure", "quantitative", "Baseline 2003-06 (%)", PCT),
    "stress_index": ("real", "measure", "quantitative", "Stress index", None),
}
COLLATERAL_LABELS = {"home_backed": "Home-backed", "vehicle_backed": "Vehicle-backed",
                     "uncollateralized": "No collateral", "other_nonrevolving": "Other non-revolving"}
COLLATERAL_COLORS = {"home_backed": "#6250d6", "vehicle_backed": "#eda100", "uncollateralized": "#e34948",
                     "other_nonrevolving": "#898781"}


def _src(key, fields):
    return {"key": key, "csv": f"{key}.csv", "caption": key, "fields": fields,
            "ds": "federated." + tableau_id(f"hhdebt-{key}-datasource"),
            "conn": "textscan." + tableau_id(f"hhdebt-{key}-textscan")}


SRC = {"ratchet": {"key": "ratchet", "csv": "ratchet.csv", "caption": DS_CAPTION, "fields": RATCHET_FIELDS,
                   "ds": DS, "conn": CONN},
       "crisis_windows": _src("crisis_windows", CRISIS_FIELDS),
       "collateral": _src("collateral", COLLATERAL_FIELDS),
       "payment_priority": _src("payment_priority", PAYMENT_FIELDS)}


# ---- v3: parameter + calculated fields (see V3 SOURCES [P] and [C] in the module docstring)
CALC_PTS = "[Calculation_" + str(int(hashlib.sha1(b"hhdebt-delta-pts").hexdigest(), 16))[:19] + "]"
CALCS = {}  # name -> (caption, datatype, role, type, default-format, formula)
CALCS[CALC_PTS] = ("Change since t0 (pts)", "real", "measure", "quantitative", 'n#,##0.0" pts";-#,##0.0" pts"',
                   "[delta_from_t0] * 100")  # shares -> percentage points; format pattern as geocoding.twbx



def q(field_instance: str) -> str:
    """Fully-qualified column reference, e.g. [federated.x].[sum:share_of_total:qk]."""
    return f"[{DS}].{field_instance}"


I_BUCKET = "[none:bucket_label:nk]"
I_QUARTER = "[tqr:date:qk]"
I_SHARE = "[sum:share_of_total:qk]"
I_PUBLIC = "[avg:public_share:qk]"
I_CLASS_LABEL = "[none:class_label:nk]"
I_CCLASS = "[none:collateral_class:nk]"
I_COLL_SHARE = "[sum:share_of_debt:qk]"
I_COVER = "[avg:coverage_ratio:qk]"
I_CRISIS = "[none:crisis_name:nk]"
I_METRIC = "[none:metric:nk]"
I_QOFF = "[none:q_offset:qk]"
I_PTS = "[avg:" + CALC_PTS[1:-1] + ":qk]"
I_LOAN = "[none:loan_label:nk]"
I_TRANS = "[avg:transition_serious_pct:qk]"


def qs(key: str, inst: str) -> str:
    return f"[{SRC[key]['ds']}].{inst}"





def sub(parent, tag, attrib=None, text=None):
    el = ET.SubElement(parent, tag, {k: str(v) for k, v in (attrib or {}).items()})
    if text is not None:
        el.text = text
    return el


def read_ratchet_meta() -> dict[str, str]:
    """Check the header and return risk_bucket -> bucket_label from the CSV."""
    path = DATA_DIR / "ratchet.csv"
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        labels = {row["risk_bucket"]: row["bucket_label"] for row in reader}
    if header != list(RATCHET_FIELDS):
        sys.exit(f"ratchet.csv header {header} != expected {list(RATCHET_FIELDS)} "
                 "(update RATCHET_FIELDS to match tableau_export.COLUMNS['ratchet'])")
    missing = [b for _, b, _ in BUCKET_COLORS if b not in labels]
    if missing:
        sys.exit(f"ratchet.csv has no rows for buckets {missing}")
    return labels


def check_fig_headers() -> None:
    for key in ("crisis_windows", "collateral", "payment_priority"):
        with (DATA_DIR / f"{key}.csv").open(newline="", encoding="utf-8") as f:
            header = next(csv.reader(f))
        if header != list(SRC[key]["fields"]):
            sys.exit(f"{key}.csv header {header} != {list(SRC[key]['fields'])} (update the *_FIELDS dict)")


# ---------------------------------------------------------------- data source

def tq(value: str) -> str:
    """Tableau string literal as stored in XML values/formulas: "none" (the &quot; comes from escaping)."""
    return f'"{value}"'


def calc_decl(parent, name):
    """Calculated field: caption, datatype, [default-format], name, role, type + <calculation> (ts_content_04.02.twb)."""
    caption, dtype, role, typ, fmt, formula = CALCS[name]
    attrib = {"caption": caption, "datatype": dtype}
    if fmt:
        attrib["default-format"] = fmt
    attrib.update({"name": name, "role": role, "type": typ})
    col = sub(parent, "column", attrib)
    sub(col, "calculation", {"class": "tableau", "formula": formula})
    return col

def column_decl(parent, name, with_format=True, fields=None):
    dtype, role, typ, caption, fmt = (fields or RATCHET_FIELDS)[name]
    attrib = {"caption": caption, "datatype": dtype}
    if fmt and with_format:
        attrib["default-format"] = fmt
    attrib.update({"name": f"[{name}]", "role": role, "type": typ})
    return sub(parent, "column", attrib)


def build_text_datasource(parent, src, calcs=(), instances=(), palettes=(), semantic=False):
    """Packaged text-file data source (same shape for every CSV; see the geocoding.twbx provenance above).
    instances: [(column, derivation, instance, type)] declared at datasource level (as Tableau does for
    palette fields); palettes: [(instance, [(bucket text, colour)])] in one mark style-rule."""
    fields, csvname, conn = src["fields"], src["csv"], src["conn"]
    stem = csvname[:-4]
    ds = sub(parent, "datasource", {"caption": src["caption"], "inline": "true", "name": src["ds"], "version": VERSION})
    fed = sub(ds, "connection", {"class": "federated"})
    ncs = sub(fed, "named-connections")
    nc = sub(ncs, "named-connection", {"caption": stem, "name": conn})
    sub(nc, "connection", {"class": "textscan", "directory": PACKAGED_DIR, "filename": csvname,
                           "password": "", "server": ""})
    rel = sub(fed, "relation", {"connection": conn, "name": csvname, "table": f"[{stem}#csv]",
                                "type": "table"})
    cols = sub(rel, "columns", {"character-set": "UTF-8", "header": "yes", "locale": "en_US", "separator": ","})
    for i, (name, spec) in enumerate(fields.items()):
        sub(cols, "column", {"datatype": spec[0], "name": name, "ordinal": i})
    cmap = sub(fed, "cols")
    for name in fields:
        sub(cmap, "map", {"key": f"[{name}]", "value": f"[{csvname}].[{name}]"})
    sub(fed, "refresh", {"increment-key": "", "incremental-updates": "false"})  # [E]: after <cols>

    mrs = sub(fed, "metadata-records")
    cap = sub(mrs, "metadata-record", {"class": "capability"})
    sub(cap, "remote-name")
    sub(cap, "remote-type", text="0")
    sub(cap, "parent-name", text=f"[{csvname}]")
    sub(cap, "remote-alias")
    sub(cap, "aggregation", text="Count")
    sub(cap, "contains-null", text="true")
    attrs = sub(cap, "attributes")
    for k, v in [("character-set", "UTF-8"), ("collation", "en_US"), ("field-delimiter", ","),
                 ("header-row", "true"), ("locale", "en_US"), ("single-char", "")]:
        sub(attrs, "attribute", {"datatype": "string", "name": k}, f'"{v}"')
    for i, (name, spec) in enumerate(fields.items()):
        dtype = spec[0]
        mr = sub(mrs, "metadata-record", {"class": "column"})
        sub(mr, "remote-name", text=name)
        sub(mr, "remote-type", text=str(REMOTE_TYPE[dtype]))
        sub(mr, "local-name", text=f"[{name}]")
        sub(mr, "parent-name", text=f"[{csvname}]")
        sub(mr, "remote-alias", text=name)
        sub(mr, "ordinal", text=str(i))
        sub(mr, "local-type", text=dtype)
        sub(mr, "aggregation", text=DEFAULT_AGG[dtype])
        if dtype == "string":
            sub(mr, "scale", text="1")
            sub(mr, "width", text="1073741823")
        sub(mr, "contains-null", text="true")
        if dtype == "string":
            sub(mr, "collation", {"flag": "0", "name": "LEN_RUS"})

    sub(ds, "aliases", {"enabled": "yes"})
    for name in fields:
        column_decl(ds, name, fields=fields)
    for name in calcs:
        calc_decl(ds, name)
    for column, derivation, inst, typ in instances:
        sub(ds, "column-instance", {"column": f"[{column}]", "derivation": derivation, "name": inst,
                                    "pivot": "key", "type": typ})
    extract_decl(ds, src)
    sub(ds, "layout", {"dim-ordering": "alphabetic", "dim-percentage": "0.5", "measure-ordering": "alphabetic",
                       "measure-percentage": "0.4", "show-structure": "true"})
    if palettes:
        rule = sub(sub(ds, "style"), "style-rule", {"element": "mark"})
        for inst, maps in palettes:
            enc = sub(rule, "encoding", {"attr": "color", "field": inst, "type": "palette"})
            for bucket, color in maps:
                sub(sub(enc, "map", {"to": color}), "bucket", text=bucket)
    if semantic:
        sv = sub(ds, "semantic-values")
        sub(sv, "semantic-value", {"key": "[Country].[Name]", "value": '"United States"'})
    return ds


# ---- v3.1 extracts. [E] = tabcmd tests/assets/WorkbookWithExtract.twbx (WorkbookWithExtract.twb, 18.1,
# build 2021.1.2 (20211.21.0511.0935), the same build string as this file):
#   https://github.com/tableau/tabcmd/blob/main/tests/assets/WorkbookWithExtract.twbx
# Tableau Public only saves extract-backed sources (error 3C242D89), so each source keeps its textscan
# connection (the "original" source, as [E] keeps its msaccess one) and gains, after its column declarations and
# before <layout>:
#   <extract count='-1' enabled='true' units='records'>
#     <connection authentication='auth-none' author-locale='en_US' class='hyper' dbname='Data/Extracts/x.hyper'
#                 default-settings='yes' schema='Extract' sslmode='' tablename='Extract' update-time=... username=''>
#       <relation name='Extract' table='[Extract].[Extract]' type='table' />
#       <refresh increment-key='' incremental-updates='false'><refresh-event .../></refresh>
#       <metadata-records> one column record per field, parent-name [Extract] </metadata-records>
# plus <refresh increment-key='' incremental-updates='false' /> after the federated <cols>, and
# upgrade-extracts='false' on <workbook>. As everywhere else in this file, only the feature-off spelling is
# written: [E]'s '_.fcp.ObjectModelEncapsulateLegacy.false...relation' becomes a plain <relation> (exactly as
# in document-api-python test/assets/TABLEAU_10_TWBX.twbx's manifest-free <extract>), and the feature-on
# twins ('...true...relation', '...true...object-id') are dropped because there is no manifest.
EXTRACT_DIR = "Data/Extracts"
EXTRACT_TIME = ("10/27/2026 12:00:00 PM", "2026-10-27 12:00:00.000")  # fixed -> reproducible XML
HYPER_COLLATION = {"flag": "1", "name": "LEN_RUS_S2"}  # [E]'s string columns in the hyper extract


def read_rows(key):
    with (DATA_DIR / f"{key}.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def extract_decl(ds, src):
    key, fields = src["key"], src["fields"]
    rows = read_rows(key)
    ex = sub(ds, "extract", {"count": "-1", "enabled": "true", "units": "records"})
    c = sub(ex, "connection", {"authentication": "auth-none", "author-locale": "en_US", "class": "hyper",
                               "dbname": f"{EXTRACT_DIR}/{key}.hyper", "default-settings": "yes",
                               "schema": "Extract", "sslmode": "", "tablename": "Extract",
                               "update-time": EXTRACT_TIME[0], "username": ""})
    sub(c, "relation", {"name": "Extract", "table": "[Extract].[Extract]", "type": "table"})
    r = sub(c, "refresh", {"increment-key": "", "incremental-updates": "false"})
    sub(r, "refresh-event", {"add-from-file-path": "", "increment-value": "%null%", "refresh-type": "create",
                             "rows-inserted": len(rows), "timestamp-start": EXTRACT_TIME[1]})
    mrs = sub(c, "metadata-records")
    for i, (name, spec) in enumerate(fields.items()):
        dtype = spec[0]
        mr = sub(mrs, "metadata-record", {"class": "column"})
        sub(mr, "remote-name", text=name)
        sub(mr, "remote-type", text=str(REMOTE_TYPE[dtype]))
        sub(mr, "local-name", text=f"[{name}]")
        sub(mr, "parent-name", text="[Extract]")
        sub(mr, "remote-alias", text=name)
        sub(mr, "ordinal", text=str(i))
        sub(mr, "family", text=src["csv"])  # [E]: the federated relation the column came from
        sub(mr, "local-type", text=dtype)
        sub(mr, "aggregation", text=DEFAULT_AGG[dtype])
        sub(mr, "approx-count", text=str(len({row[name] for row in rows})))
        sub(mr, "contains-null", text="true")
        if dtype == "string":
            sub(mr, "collation", HYPER_COLLATION)


HYPER_TYPES = {"date": "date", "string": "text", "real": "double", "integer": "big_int", "boolean": "bool"}


def _parse(dtype, v):
    import datetime
    if v == "":
        return None
    return {"date": lambda x: datetime.date.fromisoformat(x), "string": str, "real": float, "integer": int,
            "boolean": lambda x: {"True": True, "False": False}[x]}[dtype](v)


def write_hypers(out_dir: Path) -> dict[str, Path]:
    """One .hyper per data source: table "Extract"."Extract", columns named and typed as the CSV."""
    try:
        from tableauhyperapi import (Connection, CreateMode, HyperProcess, Inserter, NOT_NULLABLE, NULLABLE,
                                     SqlType, TableDefinition, TableName, Telemetry)
    except ImportError:
        sys.exit("tableauhyperapi is needed to build the extracts: "
                 "uv run --with tableauhyperapi python tableau/build_workbook.py")
    paths = {}
    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        for key, src in SRC.items():
            path = out_dir / f"{key}.hyper"
            table = TableName("Extract", "Extract")
            cols = [TableDefinition.Column(n, getattr(SqlType, HYPER_TYPES[spec[0]])(), NULLABLE)
                    for n, spec in src["fields"].items()]
            with Connection(hyper.endpoint, path, CreateMode.CREATE_AND_REPLACE) as con:
                con.catalog.create_schema("Extract")
                con.catalog.create_table(TableDefinition(table, cols))
                with Inserter(con, table) as ins:
                    for row in read_rows(key):
                        ins.add_row([_parse(spec[0], row[n]) for n, spec in src["fields"].items()])
                    ins.execute()
            paths[key] = path
    return paths


def hyper_check() -> None:
    """Reopen every packaged .hyper and compare its row count and columns with the CSV."""
    import tempfile
    from tableauhyperapi import Connection, HyperProcess, TableName, Telemetry
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(TWBX) as z, \
            HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        for key, src in SRC.items():
            path = Path(z.extract(f"{EXTRACT_DIR}/{key}.hyper", tmp))
            with Connection(hyper.endpoint, path) as con:
                table = TableName("Extract", "Extract")
                n = con.execute_scalar_query(f"SELECT COUNT(*) FROM {table}")
                cols = [str(c.name).strip('"') for c in con.catalog.get_table_definition(table).columns]
                types = [str(c.type) for c in con.catalog.get_table_definition(table).columns]
            expected = len(read_rows(key))
            assert n == expected and cols == list(src["fields"]), (key, n, expected, cols)
            print(f"hyper OK: {key}.hyper rows={n} (csv {expected}) columns={len(cols)} types={sorted(set(types))}")


def build_datasource(parent, labels):
    return build_text_datasource(
        parent, SRC["ratchet"], instances=[("bucket_label", "None", I_BUCKET, "nominal")],
        palettes=[(I_BUCKET, [(f'"{labels[b]}"', c) for _, b, c in BUCKET_COLORS])], semantic=True)


def build_fig_datasources(parent):
    """Figures 2-4: one packaged text source each, no joins."""
    cl = [(f'"{COLLATERAL_LABELS[k]}"', c) for k, c in COLLATERAL_COLORS.items()]
    ck = [(f'"{k}"', c) for k, c in COLLATERAL_COLORS.items()]
    build_text_datasource(parent, SRC["crisis_windows"], calcs=[CALC_PTS])
    build_text_datasource(parent, SRC["collateral"], instances=[("class_label", "None", I_CLASS_LABEL, "nominal")],
                          palettes=[(I_CLASS_LABEL, cl)])
    build_text_datasource(parent, SRC["payment_priority"],
                          instances=[("collateral_class", "None", I_CCLASS, "nominal")],
                          palettes=[(I_CCLASS, ck)])


# ---------------------------------------------------------------- worksheets

def view_header(table, fields, instances, calcs=(), key="ratchet"):
    src = SRC[key]
    view = sub(table, "view")
    dss = sub(view, "datasources")
    sub(dss, "datasource", {"caption": src["caption"], "name": src["ds"]})
    dep = sub(view, "datasource-dependencies", {"datasource": src["ds"]})
    for name in fields:
        column_decl(dep, name, fields=src["fields"])
    for name in calcs:
        calc_decl(dep, name)
    for column, derivation, inst, typ in instances:
        sub(dep, "column-instance", {"column": f"[{column}]", "derivation": derivation, "name": inst,
                                     "pivot": "key", "type": typ})
    return view


def title(parent, text):
    lo = sub(parent, "layout-options")
    t = sub(lo, "title")
    ft = sub(t, "formatted-text")
    sub(ft, "run", text=text)


def build_main_sheet(parent, labels):
    """v2 design, restored in v3.1: the v3 dual-axis bands rendered the Ratchet dashboard blank in the Tableau
    Public app 2026.3, so the bands, the Band/Is active crisis calcs and the Parameters datasource are gone."""
    ws = sub(parent, "worksheet", {"name": SHEET_MAIN})
    title(ws, "Share of US household mortgages + consumer credit, by who holds the risk")
    table = sub(ws, "table")
    view = view_header(table, ["bucket_label", "date", "share_of_total"], [
        ("bucket_label", "None", I_BUCKET, "nominal"),
        ("share_of_total", "Sum", I_SHARE, "quantitative"),
        ("date", "Quarter-Trunc", I_QUARTER, "quantitative"),
    ])
    # No sort element: Tableau Public rejected <manual-sort> here (error D2E8DA72, "element
    # 'manual-sort' is not allowed"). Stack order is set by hand (GETTING_STARTED.md: sort
    # Bucket label by Sort order); the legend falls back to alphabetical until then.
    sub(view, "aggregation", {"value": "true"})
    style = sub(table, "style")
    rule = sub(style, "style-rule", {"element": "axis"})
    sub(rule, "encoding", {"attr": "space", "class": "0", "field": q(I_SHARE), "field-type": "quantitative",
                           "max": "1.0", "min": "0.0", "range-type": "fixed", "scope": "rows", "type": "space"})
    panes = sub(table, "panes")
    pane = sub(panes, "pane", {"selection-relaxation-option": "selection-relaxation-allow"})
    pv = sub(pane, "view")
    sub(pv, "breakdown", {"value": "auto"})
    sub(pane, "mark", {"class": "Area"})
    encs = sub(pane, "encodings")
    sub(encs, "color", {"column": q(I_BUCKET)})
    sub(table, "rows", text=q(I_SHARE))
    sub(table, "cols", text=q(I_QUARTER))


def build_public_sheet(parent):
    ws = sub(parent, "worksheet", {"name": SHEET_PUBLIC})
    title(ws, "Public share: federal government + GSEs/agency pools + state & local")
    table = sub(ws, "table")
    view = view_header(table, ["date", "public_share"], [
        ("public_share", "Avg", I_PUBLIC, "quantitative"),
        ("date", "Quarter-Trunc", I_QUARTER, "quantitative"),
    ])
    sub(view, "aggregation", {"value": "true"})
    sub(table, "style")
    panes = sub(table, "panes")
    pane = sub(panes, "pane", {"selection-relaxation-option": "selection-relaxation-allow"})
    pv = sub(pane, "view")
    sub(pv, "breakdown", {"value": "auto"})
    # 'Automatic' (not 'Line'): continuous date x measure renders as a line, and 'Automatic' is the
    # mark class the example files use for their time-series sheets. Default colour: no mark-colour
    # attribute appears in the example files, so none is written.
    sub(pane, "mark", {"class": "Automatic"})
    sub(table, "rows", text=q(I_PUBLIC))
    sub(table, "cols", text=q(I_QUARTER))


def member_filter(view, key, inst, value):
    """Single-value categorical filter + its <slices> entry, copied from TSI ts_content_04.02.twb (18.1, 2025.1):
    <filter class='categorical' column=...><groupfilter function='member' level=... member='"View"'
    user:ui-domain='relevant' user:ui-enumeration='inclusive' user:ui-marker='enumerate'/></filter> ... <slices>."""
    f = sub(view, "filter", {"class": "categorical", "column": qs(key, inst)})
    sub(f, "groupfilter", {"function": "member", "level": inst, "member": tq(value), "user:ui-domain": "relevant",
                           "user:ui-enumeration": "inclusive", "user:ui-marker": "enumerate"})
    sub(sub(view, "slices"), "column", text=qs(key, inst))


def simple_pane(table, mark, color=None):
    pane = sub(sub(table, "panes"), "pane", {"selection-relaxation-option": "selection-relaxation-allow"})
    sub(sub(pane, "view"), "breakdown", {"value": "auto"})
    sub(pane, "mark", {"class": mark})  # 'Line' as in Logshark ResourceManager.twbx; 'Area' as v2
    if color:
        sub(sub(pane, "encodings"), "color", {"column": color})


def build_crisis_sheet(parent):
    k = "crisis_windows"
    ws = sub(parent, "worksheet", {"name": SHEET_CRISIS})
    title(ws, "Public share around each crisis: change since the start quarter (t0), percentage points")
    table = sub(ws, "table")
    view = view_header(table, ["crisis_name", "delta_from_t0", "metric", "q_offset"], [
        ("crisis_name", "None", I_CRISIS, "nominal"),
        ("metric", "None", I_METRIC, "nominal"),
        ("q_offset", "None", I_QOFF, "quantitative"),
        (CALC_PTS[1:-1], "Avg", I_PTS, "quantitative"),
    ], calcs=[CALC_PTS], key=k)
    member_filter(view, k, I_METRIC, "public_share")
    sub(view, "aggregation", {"value": "true"})
    sub(table, "style")
    simple_pane(table, "Line")
    # one panel per row: discrete dimension crossed with the measure, '([dim:nk] * [measure:qk])' as in
    # Logshark Bridge.twbx (18.1) / TSI ts_web_requests_03.01.twb
    sub(table, "rows", text=f"({qs(k, I_CRISIS)} * {qs(k, I_PTS)})")
    sub(table, "cols", text=qs(k, I_QOFF))


def build_collateral_sheets(parent):
    k = "collateral"
    ws = sub(parent, "worksheet", {"name": SHEET_COLL_SHARE})
    title(ws, "Share of household debt by collateral behind it")
    table = sub(ws, "table")
    view = view_header(table, ["class_label", "date", "share_of_debt"], [
        ("class_label", "None", I_CLASS_LABEL, "nominal"),
        ("share_of_debt", "Sum", I_COLL_SHARE, "quantitative"),
        ("date", "Quarter-Trunc", I_QUARTER, "quantitative"),
    ], key=k)
    sub(view, "aggregation", {"value": "true"})
    rule = sub(sub(table, "style"), "style-rule", {"element": "axis"})
    sub(rule, "encoding", {"attr": "space", "class": "0", "field": qs(k, I_COLL_SHARE), "field-type": "quantitative",
                           "max": "1.0", "min": "0.0", "range-type": "fixed", "scope": "rows", "type": "space"})
    simple_pane(table, "Area", qs(k, I_CLASS_LABEL))
    sub(table, "rows", text=qs(k, I_COLL_SHARE))
    sub(table, "cols", text=qs(k, I_QUARTER))

    ws = sub(parent, "worksheet", {"name": SHEET_COLL_COVER})
    title(ws, "Home-backed debt: collateral value ÷ debt (coverage ratio)")
    table = sub(ws, "table")
    view = view_header(table, ["collateral_class", "coverage_ratio", "date"], [
        ("collateral_class", "None", I_CCLASS, "nominal"),
        ("coverage_ratio", "Avg", I_COVER, "quantitative"),
        ("date", "Quarter-Trunc", I_QUARTER, "quantitative"),
    ], key=k)
    member_filter(view, k, I_CCLASS, "home_backed")
    sub(view, "aggregation", {"value": "true"})
    sub(table, "style")
    simple_pane(table, "Line")
    sub(table, "rows", text=qs(k, I_COVER))
    sub(table, "cols", text=qs(k, I_QUARTER))


def build_payment_sheet(parent):
    k = "payment_priority"
    ws = sub(parent, "worksheet", {"name": SHEET_PAYMENT})
    title(ws, "Share of balances moving into serious delinquency (90+ days), by loan type")
    table = sub(ws, "table")
    view = view_header(table, ["collateral_class", "date", "loan_label", "transition_serious_pct"], [
        ("collateral_class", "None", I_CCLASS, "nominal"),
        ("loan_label", "None", I_LOAN, "nominal"),
        ("transition_serious_pct", "Avg", I_TRANS, "quantitative"),
        ("date", "Quarter-Trunc", I_QUARTER, "quantitative"),
    ], key=k)
    sub(view, "aggregation", {"value": "true"})
    sub(table, "style")
    simple_pane(table, "Line", qs(k, I_CCLASS))
    sub(table, "rows", text=f"({qs(k, I_LOAN)} * {qs(k, I_TRANS)})")
    sub(table, "cols", text=qs(k, I_QUARTER))


# ---------------------------------------------------------------- dashboard + windows

W, H = 1000, 700  # design size used to split zone heights; the dashboards themselves size automatically
DASHBOARDS = {  # name -> zones top to bottom: (kind, px or None = takes the rest, sheet/text, legend param, pane)
    DASHBOARD: [("title", 50, TITLE, None, None), ("sheet", None, SHEET_MAIN, None, None),
                ("legend", 50, SHEET_MAIN, q(I_BUCKET), "0"), ("sheet", 170, SHEET_PUBLIC, None, None)],
    DASH_CRISIS: [("title", 50, "Did crises move debt onto the public balance sheet?", None, None),
                  ("sheet", None, SHEET_CRISIS, None, None)],
    DASH_COLLATERAL: [("title", 50, "What stands behind US household debt?", None, None),
                      ("sheet", None, SHEET_COLL_SHARE, None, None),
                      ("legend", 50, SHEET_COLL_SHARE, qs("collateral", I_CLASS_LABEL), "0"),
                      ("sheet", 220, SHEET_COLL_COVER, None, None)],
    DASH_PAYMENT: [("title", 50, "Which debts do households stop paying first?", None, None),
                   ("sheet", None, SHEET_PAYMENT, None, None),
                   ("legend", 50, SHEET_PAYMENT, qs("payment_priority", I_CCLASS), "0")],
}
SHEET_LEGENDS = {SHEET_MAIN: (q(I_BUCKET), "0"), SHEET_COLL_SHARE: (qs("collateral", I_CLASS_LABEL), "0"),
                 SHEET_PAYMENT: (qs("payment_priority", I_CCLASS), "0")}


def zone_style(parent, margin):
    zs = sub(parent, "zone-style")
    for attr, val in [("border-color", "#000000"), ("border-style", "none"), ("border-width", "0"),
                      ("margin", margin)]:
        sub(zs, "format", {"attr": attr, "value": val})


def build_dashboard(parent, name, rows):
    db = sub(parent, "dashboard", {"name": name})
    sub(db, "style")
    # Automatic sizing so the views fit the site's column width: <size sizing-mode='automatic' />, as in
    # Logshark Bridge.twbx / TabadminController.twbx / Config.twbx (18.1, builds 2022.3.22 and 2023.3.12).
    sub(db, "size", {"sizing-mode": "automatic"})
    zones = sub(db, "zones")
    root = sub(zones, "zone", {"h": 100000, "id": 1, "type": "layout-basic", "w": 100000, "x": 0, "y": 0})
    flow = sub(root, "zone", {"h": 100000, "id": 2, "param": "vert", "type": "layout-flow", "w": 100000,
                              "x": 0, "y": 0})
    rest = H - sum(px for _, px, *_ in rows if px)
    y = 0
    for zid, (kind, px, what, param, pane) in enumerate(rows, start=3):
        h = round((px or rest) * 100000 / H)
        if kind == "title":
            z = sub(flow, "zone", {"fixed-size": px, "h": h, "id": zid, "is-fixed": "true", "type": "text",
                                   "w": 100000, "x": 0, "y": y})
            ft = sub(z, "formatted-text")
            sub(ft, "run", {"bold": "true", "fontcolor": "#0b0b0b", "fontsize": "18"}, what)
            zone_style(z, "8")
        elif kind == "legend":
            z = sub(flow, "zone", {"fixed-size": px, "h": h, "id": zid, "is-fixed": "true",
                                   "leg-item-layout": "horz", "name": what, "pane-specification-id": pane,
                                   "param": param, "type": "color", "w": 100000, "x": 0, "y": y})
            zone_style(z, "4")
        else:
            attrib = {"h": h, "id": zid, "name": what, "w": 100000, "x": 0, "y": y}
            if px:
                attrib = {"fixed-size": px, **attrib, "is-fixed": "true"}
            z = sub(flow, "zone", attrib)
            zone_style(z, "4")
        y += h
    zone_style(root, "8")


def worksheet_window(parent, name, legend_param=None, legend_pane="0"):
    # The one window with maximized='true' is the sheet Tableau opens on (exactly one per corpus workbook;
    # 9 of the 18.1 ones open on a worksheet). v3.1 opens on the simple 'Public share' line.
    attrib = {"class": "worksheet", "maximized": "true", "name": name} if name == OPEN_SHEET \
        else {"class": "worksheet", "name": name}
    win = sub(parent, "window", attrib)
    cards = sub(win, "cards")
    left = sub(cards, "edge", {"name": "left"})
    strip = sub(left, "strip", {"size": "160"})
    for t in ("pages", "filters", "marks"):
        sub(strip, "card", {"type": t})
    top = sub(cards, "edge", {"name": "top"})
    for t, size in (("columns", "2147483647"), ("rows", "2147483647"), ("title", "30")):
        sub(sub(top, "strip", {"size": size}), "card", {"type": t})
    if legend_param:
        right = sub(cards, "edge", {"name": "right"})
        sub(sub(right, "strip", {"size": "220"}), "card",
            {"pane-specification-id": legend_pane, "param": legend_param, "type": "color"})
    vp = sub(win, "viewpoint")
    sub(vp, "zoom", {"type": "entire-view"})


def build_windows(parent):
    wins = sub(parent, "windows", {"source-height": "30"})
    for name in SHEETS:
        worksheet_window(wins, name, *SHEET_LEGENDS.get(name, (None, "0")))
    for name, rows in DASHBOARDS.items():
        dw = sub(wins, "window", {"class": "dashboard", "name": name})
        vps = sub(dw, "viewpoints")
        for kind, _, what, *_ in rows:
            if kind == "sheet":
                sub(sub(vps, "viewpoint", {"name": what}), "zoom", {"type": "entire-view"})
        sub(dw, "active", {"id": "-1"})


# ---------------------------------------------------------------- assemble

def build_tree() -> ET.ElementTree:
    labels = read_ratchet_meta()
    check_fig_headers()
    wb = ET.Element("workbook", {"original-version": VERSION, "source-build": SOURCE_BUILD,
                                 "source-platform": "win", "upgrade-extracts": "false", "version": VERSION})
    prefs = sub(wb, "preferences")
    sub(prefs, "preference", {"name": "ui.encoding.shelf.height", "value": "24"})
    sub(prefs, "preference", {"name": "ui.shelf.height", "value": "26"})
    dss = sub(wb, "datasources")
    build_datasource(dss, labels)
    build_fig_datasources(dss)
    wss = sub(wb, "worksheets")
    build_main_sheet(wss, labels)
    build_public_sheet(wss)
    build_crisis_sheet(wss)
    build_collateral_sheets(wss)
    build_payment_sheet(wss)
    dbs = sub(wb, "dashboards")
    for name, rows in DASHBOARDS.items():
        build_dashboard(dbs, name, rows)
    build_windows(wb)
    return ET.ElementTree(wb)


def _esc(value: str, quote: bool) -> str:
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return value.replace("'", "&apos;") if quote else value


def _write(el: ET.Element, depth: int, out: list[str]) -> None:
    """Serialize like Tableau does: two-space indent, single-quoted attributes, &quot; in text."""
    pad = "  " * depth
    attrs = "".join(f" {k}='{_esc(v, True)}'" for k, v in el.attrib.items())
    if len(el) == 0 and el.text is None:
        out.append(f"{pad}<{el.tag}{attrs} />")
    elif len(el) == 0:
        out.append(f"{pad}<{el.tag}{attrs}>{_esc(el.text, False)}</{el.tag}>")
    else:
        out.append(f"{pad}<{el.tag}{attrs}>")
        for child in el:
            _write(child, depth + 1, out)
        out.append(f"{pad}</{el.tag}>")


def serialize(tree: ET.ElementTree) -> bytes:
    root = tree.getroot()
    out: list[str] = []
    _write(root, 0, out)
    out[0] = out[0].replace("<workbook ", "<workbook xmlns:user='http://www.tableausoftware.com/xml/user' ", 1) \
        if "xmlns:user" not in out[0] else out[0]
    header = ("<?xml version='1.0' encoding='utf-8' ?>\n\n"
              f"<!-- build {BUILD}                               -->\n")
    return (header + "\n".join(out) + "\n").encode("utf-8")


def write_outputs() -> None:
    import tempfile
    xml_bytes = serialize(build_tree())
    TWB.write_bytes(xml_bytes)
    stamp = (2026, 1, 1, 0, 0, 0)  # fixed timestamps -> reproducible zip
    tmp = TWBX.with_suffix(".twbx.tmp")
    with tempfile.TemporaryDirectory() as hdir, zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as z:
        hypers = write_hypers(Path(hdir))
        z.writestr(zipfile.ZipInfo(TWB.name, stamp), xml_bytes, compress_type=zipfile.ZIP_DEFLATED)
        for name in CSV_FILES:
            src = DATA_DIR / name
            if not src.exists():
                sys.exit(f"missing {src}; run `uv run hhdebt export-tableau` first")
            z.writestr(zipfile.ZipInfo(f"{PACKAGED_DIR}/{name}", stamp), src.read_bytes(),
                       compress_type=zipfile.ZIP_DEFLATED)
        for key, path in hypers.items():
            z.writestr(zipfile.ZipInfo(f"{EXTRACT_DIR}/{key}.hyper", stamp), path.read_bytes(),
                       compress_type=zipfile.ZIP_DEFLATED)
    tmp.replace(TWBX)
    print(f"wrote {TWB.relative_to(HERE.parent)} ({len(xml_bytes):,} bytes)")
    print(f"wrote {TWBX.relative_to(HERE.parent)} ({TWBX.stat().st_size:,} bytes)")


# Content model Tableau reported for <view> in error D2E8DA72 (v1). Tableau's message lists the members in
# order; real files show filter/sort interleaving ("filter sort filter"), so those two form one repeated group.
VIEW_MODEL = r"(datasources )?(mapsources )?(datasource-dependencies )*((filter|sort) )*(perspectives )?(slices )?(aggregation )?"


def check_view_order(root) -> list[str]:
    import re
    seqs = []
    for v in root.iter("view"):
        if v.find("datasources") is None:  # pane-level <view><breakdown/></view>
            continue
        seq = "".join(c.tag + " " for c in v)
        assert re.fullmatch(VIEW_MODEL, seq), f"<view> children out of content model: {seq}"
        seqs.append(seq.strip())
    return seqs


def self_check() -> None:
    """Stdlib checks: XML parses, names are consistent, element order, zip has the expected entries."""
    root = ET.parse(TWB).getroot()
    assert root.tag == "workbook" and root.get("version") == VERSION
    top = root.findall("datasources/datasource")
    ds_names = [SRC[k]["ds"] for k in SRC]
    assert [d.get("name") for d in top] == ds_names, [d.get("name") for d in top]
    ds = top[0]
    for d, k in zip(top, SRC):
        tc = d.find("connection/named-connections/named-connection/connection")
        assert (d.get("caption"), tc.get("filename"), tc.get("directory")) == (SRC[k]["caption"], f"{k}.csv",
                                                                              PACKAGED_DIR), k
    assert not list(root.iter("members")), "no Parameters datasource in v3.1"
    assert ds.get("name") == DS and ds.get("caption") == DS_CAPTION
    tc = ds.find("connection/named-connections/named-connection/connection")
    assert (tc.get("class"), tc.get("directory"), tc.get("filename")) == ("textscan", PACKAGED_DIR, "ratchet.csv")
    meta = [m.findtext("remote-name") for m in ds.iterfind("connection/metadata-records/metadata-record[@class='column']")]
    assert meta == list(RATCHET_FIELDS), meta
    assert ds.find("column[calculation]") is None, "ratchet has no calcs in v3.1"
    maxed = [w.get("name") for w in root.iterfind("windows/window") if w.get("maximized") == "true"]
    assert maxed == [OPEN_SHEET], maxed
    sheets = [w.get("name") for w in root.iterfind("worksheets/worksheet")]
    dashes = [d.get("name") for d in root.iterfind("dashboards/dashboard")]
    assert sheets == SHEETS and dashes == list(DASHBOARDS), (sheets, dashes)
    assert dashes == [DASHBOARD, "CrisisSmallMultiples", "Collateral", "PaymentPriority"]
    assert len(set(sheets + dashes)) == len(sheets) + len(dashes), "sheet and dashboard names must be unique"
    sizes = [d.find("size").attrib for d in root.iterfind("dashboards/dashboard")]
    assert all(sz == {"sizing-mode": "automatic"} for sz in sizes), sizes
    zone_names = {z.get("name") for z in root.iter("zone") if z.get("name")}
    assert zone_names <= set(sheets), zone_names
    marks = [m.get("class") for m in root.iter("mark")]
    assert marks == ["Area", "Automatic", "Line", "Area", "Line", "Line"], marks
    # every [ds].[instance] on any sheet is declared in that sheet's datasource-dependencies
    for w in root.iterfind("worksheets/worksheet"):
        t = w.find("table")
        decl = {f"[{d.get('datasource')}].{ci.get('name')}" for d in t.iterfind("view/datasource-dependencies")
                for ci in d.iterfind("column-instance")}
        import re as _re
        used = set(_re.findall(r"\[federated\.[a-z0-9]+\]\.\[[^\]]+\]", (t.findtext("rows") or "") + (t.findtext("cols") or "")))
        used |= {e.get(k) for e in t.iter() for k in ("column", "field", "y-axis-name")
                 if e.get(k, "").startswith("[federated.")}
        used |= {e.text for e in t.iterfind("view/slices/column")}
        assert used <= decl, (w.get("name"), used - decl)
    seqs = check_view_order(root)
    main = root.find(f"worksheets/worksheet[@name='{SHEET_MAIN}']/table")
    assert main.findtext("rows") == q(I_SHARE) and main.find("view/sort") is None
    assert [p.get("id") for p in main.iterfind("panes/pane")] == [None]
    legend = [z for z in root.iter("zone") if z.get("type") == "color"][0]
    assert legend.get("pane-specification-id") == "0" and legend.get("param") == q(I_BUCKET)
    with zipfile.ZipFile(TWBX) as z:
        names = z.namelist()
        assert z.testzip() is None
        assert z.read(TWB.name) == TWB.read_bytes()
    expected = [TWB.name] + [f"{PACKAGED_DIR}/{n}" for n in CSV_FILES] + [f"{EXTRACT_DIR}/{k}.hyper" for k in SRC]
    for d, k in zip(top, SRC):  # every source extract-backed, as [E]
        ex = d.find("extract")
        assert ex is not None and ex.get("enabled") == "true", k
        hc = ex.find("connection")
        assert (hc.get("class"), hc.get("dbname"), hc.find("relation").get("table")) == \
            ("hyper", f"{EXTRACT_DIR}/{k}.hyper", "[Extract].[Extract]"), k
        assert [m.findtext("remote-name") for m in hc.iterfind("metadata-records/metadata-record")] == \
            list(SRC[k]["fields"]), k
    assert names == expected, names
    print("self-check OK: XML parses;", f"datasources {[SRC[k]['caption'] for k in SRC]};",
          f"all dashboards sizing-mode=automatic; opens on {OPEN_SHEET!r}; Ratchet – main = v2 single-axis area;",
          f"worksheets {sheets}; dashboard {dashes}; zip entries {names}")
    print("  <view> child order fits the D2E8DA72 content model:", *seqs, sep="\n    ")


def corpus_order_check(corpus: Path) -> None:
    """Compare sibling ORDER in our .twb with real Tableau files (every *.twb under `corpus`): for each parent
    tag, every pair of child tags we write in order a, b must never appear as b-before-a in a real file under
    the same parent, and every (parent, child) we write must occur in some real file."""
    seen, before, attrs = set(), set(), set()
    files = sorted(corpus.rglob("*.twb"))
    for f in files:
        try:
            r = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for parent in r.iter():
            attrs.update((parent.tag, k) for k in parent.attrib)
            tags = [c.tag for c in parent]
            for i, a in enumerate(tags):
                seen.add((parent.tag, a))
                for b in tags[i + 1:]:
                    if a != b:
                        before.add((parent.tag, a, b))
    ours = ET.parse(TWB).getroot()
    unseen, conflicts, checked = set(), set(), 0
    new_attrs = {(e.tag, k) for e in ours.iter() for k in e.attrib if k != "xmlns:user"} - attrs
    for parent in ours.iter():
        tags = [c.tag for c in parent]
        for i, a in enumerate(tags):
            if (parent.tag, a) not in seen:
                unseen.add((parent.tag, a))
            for b in tags[i + 1:]:
                if a != b:
                    checked += 1
                    if (parent.tag, b, a) in before and (parent.tag, a, b) not in before:
                        conflicts.add((parent.tag, a, b))
    print(f"corpus order check: {len(files)} real .twb files; {checked} sibling pairs checked; "
          f"{len(conflicts)} order conflicts; {len(unseen)} parent/child pairs never seen; "
          f"{len(new_attrs)} element/attribute pairs never seen")
    for t in sorted(new_attrs):
        print("    UNSEEN ATTRIBUTE", t)
    for c in sorted(conflicts):
        print("    CONFLICT", c)
    for u in sorted(unseen):
        print("    UNSEEN", u)


def docapi_check() -> None:
    """Optional: load both files with tableaudocumentapi (pip install tableaudocumentapi)."""
    try:
        from tableaudocumentapi import Workbook
    except ImportError:
        print("tableaudocumentapi not installed; skipping (pip install tableaudocumentapi setuptools)")
        return
    for path in (TWB, TWBX):
        wb = Workbook(str(path))
        names = [d.name for d in wb.datasources]
        assert names == [SRC[k]["ds"] for k in SRC], names
        for d2, k in zip(wb.datasources, SRC):
            f2 = {f.id for f in d2.fields.values()}
            miss = [n for n in SRC[k]["fields"] if f"[{n}]" not in f2]
            assert d2.caption == SRC[k]["caption"] and d2.connections[0].dbclass == "textscan" and not miss, (k, miss)
        assert CALC_PTS in {f.id for f in wb.datasources[1].fields.values()}
        assert wb.dashboards == list(DASHBOARDS), wb.dashboards
        d = wb.datasources[0]
        assert d.caption == DS_CAPTION
        c = d.connections[0]
        assert c.dbclass == "textscan", c.dbclass
        fields = {f.id: f for f in d.fields.values()}
        missing = [n for n in RATCHET_FIELDS if f"[{n}]" not in fields] 
        assert not missing, missing
        for n, spec in RATCHET_FIELDS.items():
            f = fields[f"[{n}]"]
            assert f.datatype == spec[0], (n, f.datatype)
        assert wb.worksheets == SHEETS, wb.worksheets
        main_uses = {f.caption for f in fields.values() if SHEET_MAIN in f.worksheets}
        print(f"tableaudocumentapi OK: {path.name}: worksheets={wb.worksheets} dashboards={wb.dashboards} "
              f"datasources={[x.caption or x.name for x in wb.datasources]} "
              f"caption={d.caption!r} connection class={c.dbclass} fields={len(fields)}")
        print(f"    fields used on {SHEET_MAIN!r}: {sorted(main_uses)}")
        for n in ["recession", "crisis_id"]:
            f = fields[f"[{n}]"]
            extra = f" formula={f.calculation!r}" if f.calculation else ""
            print(f"    {f.id:<34} caption={f.caption!r:<26} datatype={f.datatype:<8} role={f.role}{extra}")


if __name__ == "__main__":
    write_outputs()
    self_check()
    hyper_check()
    if "--check" in sys.argv[1:]:
        docapi_check()
    if "--corpus" in sys.argv[1:]:  # --corpus DIR: folder of real Tableau .twb files (see V3 SOURCES)
        corpus_order_check(Path(sys.argv[sys.argv.index("--corpus") + 1]))
