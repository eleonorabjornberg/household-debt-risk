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

# ---- v3: parameter + calculated fields (see V3 SOURCES [P] and [C] in the module docstring)
PARAMS = "Parameters"
PARAM_NAME = "[Active crisis]"  # caption == name, as geocoding.twbx's '[Base Salary]'; the site calls it by caption
PARAM_CAPTION = "Active crisis"
PARAM_DEFAULT = "none"
CALC_BAND = "[Calculation_" + str(int(hashlib.sha1(b"hhdebt-band").hexdigest(), 16))[:19] + "]"
CALC_ACTIVE = "[Calculation_" + str(int(hashlib.sha1(b"hhdebt-active-crisis").hexdigest(), 16))[:19] + "]"
CALCS = {  # name -> (caption, datatype, role, type, default-format, formula)
    CALC_BAND: ("Band", "integer", "measure", "quantitative", "p0%", "IF [recession] = 1 THEN 1 END"),
    CALC_ACTIVE: ("Is active crisis", "boolean", "dimension", "nominal", None,
                  f"[crisis_id] = [{PARAMS}].{PARAM_NAME}"),
}
BAND_COLORS = {"false": "#d9d9d9", "true": "#9a9a9a"}  # lowercase hex, as Tableau writes palette colours
BAND_TRANSPARENCY = "102"  # 0-255 alpha; 102/255 = 40% opacity (ServerTelemetry pane writes 126)


def q(field_instance: str) -> str:
    """Fully-qualified column reference, e.g. [federated.x].[sum:share_of_total:qk]."""
    return f"[{DS}].{field_instance}"


I_BUCKET = "[none:bucket_label:nk]"
I_QUARTER = "[tqr:date:qk]"
I_SHARE = "[sum:share_of_total:qk]"
I_PUBLIC = "[avg:public_share:qk]"
I_BAND = "[avg:" + CALC_BAND[1:-1] + ":qk]"
I_ACTIVE = "[none:" + CALC_ACTIVE[1:-1] + ":nk]"
PANE_BAND, PANE_SHARE = "1", "2"  # pane ids of the dual axis; the colour legend points at the share pane


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


def read_crisis_ids() -> list[str]:
    """Parameter members: every crisis_id in crises.csv, in file order."""
    with (DATA_DIR / "crises.csv").open(newline="", encoding="utf-8") as f:
        ids = [row["crisis_id"] for row in csv.DictReader(f)]
    if not ids or PARAM_DEFAULT in ids:
        sys.exit(f"crises.csv crisis_ids unusable for the parameter: {ids}")
    return ids


# ---------------------------------------------------------------- data source

def tq(value: str) -> str:
    """Tableau string literal as stored in XML values/formulas: "none" (the &quot; comes from escaping)."""
    return f'"{value}"'


def param_decl(parent, members=None):
    """String list parameter, modelled on geocoding.twbx 'Sort by' / ts_events_04.02.twb 'Tableau Server
    Protocol': attribute order caption, datatype, name, param-domain-type, role, type, value; children
    <calculation> then <members>. The copy inside a view's datasource-dependencies omits <members>
    (as geocoding.twbx does)."""
    col = sub(parent, "column", {"caption": PARAM_CAPTION, "datatype": "string", "name": PARAM_NAME,
                                 "param-domain-type": "list", "role": "measure", "type": "nominal",
                                 "value": tq(PARAM_DEFAULT)})
    sub(col, "calculation", {"class": "tableau", "formula": tq(PARAM_DEFAULT)})
    if members is not None:
        ms = sub(col, "members")
        for m in members:
            sub(ms, "member", {"value": tq(m)})
    return col


def build_parameters(parent, crisis_ids):
    """<datasource hasconnection='false' inline='true' name='Parameters' version='18.1'> + <aliases>, exactly
    the shape of geocoding.twbx line 36."""
    ds = sub(parent, "datasource", {"hasconnection": "false", "inline": "true", "name": PARAMS, "version": VERSION})
    sub(ds, "aliases", {"enabled": "yes"})
    param_decl(ds, [PARAM_DEFAULT] + crisis_ids)
    return ds


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

def column_decl(parent, name, with_format=True):
    dtype, role, typ, caption, fmt = RATCHET_FIELDS[name]
    attrib = {"caption": caption, "datatype": dtype}
    if fmt and with_format:
        attrib["default-format"] = fmt
    attrib.update({"name": f"[{name}]", "role": role, "type": typ})
    return sub(parent, "column", attrib)


def build_datasource(parent, labels):
    ds = sub(parent, "datasource", {"caption": DS_CAPTION, "inline": "true", "name": DS, "version": VERSION})
    fed = sub(ds, "connection", {"class": "federated"})
    ncs = sub(fed, "named-connections")
    nc = sub(ncs, "named-connection", {"caption": "ratchet", "name": CONN})
    sub(nc, "connection", {"class": "textscan", "directory": PACKAGED_DIR, "filename": "ratchet.csv",
                           "password": "", "server": ""})
    rel = sub(fed, "relation", {"connection": CONN, "name": "ratchet.csv", "table": "[ratchet#csv]",
                                "type": "table"})
    cols = sub(rel, "columns", {"character-set": "UTF-8", "header": "yes", "locale": "en_US", "separator": ","})
    for i, (name, spec) in enumerate(RATCHET_FIELDS.items()):
        sub(cols, "column", {"datatype": spec[0], "name": name, "ordinal": i})
    cmap = sub(fed, "cols")
    for name in RATCHET_FIELDS:
        sub(cmap, "map", {"key": f"[{name}]", "value": f"[ratchet.csv].[{name}]"})

    mrs = sub(fed, "metadata-records")
    cap = sub(mrs, "metadata-record", {"class": "capability"})
    sub(cap, "remote-name")
    sub(cap, "remote-type", text="0")
    sub(cap, "parent-name", text="[ratchet.csv]")
    sub(cap, "remote-alias")
    sub(cap, "aggregation", text="Count")
    sub(cap, "contains-null", text="true")
    attrs = sub(cap, "attributes")
    for k, v in [("character-set", "UTF-8"), ("collation", "en_US"), ("field-delimiter", ","),
                 ("header-row", "true"), ("locale", "en_US"), ("single-char", "")]:
        sub(attrs, "attribute", {"datatype": "string", "name": k}, f'"{v}"')
    for i, (name, spec) in enumerate(RATCHET_FIELDS.items()):
        dtype = spec[0]
        mr = sub(mrs, "metadata-record", {"class": "column"})
        sub(mr, "remote-name", text=name)
        sub(mr, "remote-type", text=str(REMOTE_TYPE[dtype]))
        sub(mr, "local-name", text=f"[{name}]")
        sub(mr, "parent-name", text="[ratchet.csv]")
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
    for name in RATCHET_FIELDS:
        column_decl(ds, name)
    for name in CALCS:
        calc_decl(ds, name)
    sub(ds, "column-instance", {"column": "[bucket_label]", "derivation": "None", "name": I_BUCKET,
                                "pivot": "key", "type": "nominal"})
    sub(ds, "layout", {"dim-ordering": "alphabetic", "dim-percentage": "0.5", "measure-ordering": "alphabetic",
                       "measure-percentage": "0.4", "show-structure": "true"})
    style = sub(ds, "style")
    rule = sub(style, "style-rule", {"element": "mark"})
    enc = sub(rule, "encoding", {"attr": "color", "field": I_BUCKET, "type": "palette"})
    for _, bucket, color in BUCKET_COLORS:
        m = sub(enc, "map", {"to": color})
        sub(m, "bucket", text=f'"{labels[bucket]}"')
    # v3 band colours: palette on the boolean calc, buckets unquoted true/false (V3 SOURCES [C]).
    enc = sub(rule, "encoding", {"attr": "color", "field": I_ACTIVE, "type": "palette"})
    for bucket, color in BAND_COLORS.items():
        sub(sub(enc, "map", {"to": color}), "bucket", text=bucket)
    sv = sub(ds, "semantic-values")
    sub(sv, "semantic-value", {"key": "[Country].[Name]", "value": '"United States"'})
    return ds


# ---------------------------------------------------------------- worksheets

def view_header(table, fields, instances, calcs=(), params=False):
    view = sub(table, "view")
    dss = sub(view, "datasources")
    sub(dss, "datasource", {"caption": DS_CAPTION, "name": DS})
    if params:  # data source first, then Parameters; dependencies: Parameters first (V3 SOURCES [P])
        sub(dss, "datasource", {"name": PARAMS})
        param_decl(sub(view, "datasource-dependencies", {"datasource": PARAMS}))
    dep = sub(view, "datasource-dependencies", {"datasource": DS})
    for name in fields:
        column_decl(dep, name)
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
    ws = sub(parent, "worksheet", {"name": SHEET_MAIN})
    title(ws, "Share of US household mortgages + consumer credit, by who holds the risk")
    table = sub(ws, "table")
    view = view_header(table, ["bucket_label", "crisis_id", "date", "recession", "share_of_total"], [
        ("bucket_label", "None", I_BUCKET, "nominal"),
        (CALC_BAND[1:-1], "Avg", I_BAND, "quantitative"),
        (CALC_ACTIVE[1:-1], "None", I_ACTIVE, "nominal"),
        ("share_of_total", "Sum", I_SHARE, "quantitative"),
        ("date", "Quarter-Trunc", I_QUARTER, "quantitative"),
    ], calcs=list(CALCS), params=True)
    # No sort element (deliberately, v3): the stack order stays a hand step (GETTING_STARTED.md "Updating to
    # v3": Bucket label -> Sort by Field Sort order, Minimum, Descending). V3 SOURCES [S] records the
    # <sort class='computed'> form that would fit here, but it was left out to keep the risk minimal.
    sub(view, "aggregation", {"value": "true"})

    # Dual axis (V3 SOURCES [D]). Band is the FIRST measure so its bars are drawn underneath; its (left) axis
    # stays visible, fixed 0-1, formatted as a percentage and titled like the v2 axis. Share of total is the
    # second measure: synchronised to the first and its (right) axis hidden.
    style = sub(table, "style")
    rule = sub(style, "style-rule", {"element": "axis"})
    sub(rule, "encoding", {"attr": "space", "class": "0", "field": q(I_BAND), "field-type": "quantitative",
                           "max": "1.0", "min": "0.0", "range-type": "fixed", "scope": "rows", "type": "space"})
    sub(rule, "encoding", {"attr": "space", "class": "0", "field": q(I_SHARE), "field-type": "quantitative",
                           "fold": "true", "scope": "rows", "synchronized": "true", "type": "space"})
    sub(rule, "format", {"attr": "title", "class": "0", "field": q(I_BAND), "scope": "rows",
                         "value": "Share of total"})
    sub(rule, "format", {"attr": "display", "class": "0", "field": q(I_SHARE), "scope": "rows", "value": "false"})

    panes = sub(table, "panes")
    # "All" pane (no id), as ClusterController/Hyper write it; per-measure panes override its mark.
    pane = sub(panes, "pane", {"selection-relaxation-option": "selection-relaxation-allow"})
    sub(sub(pane, "view"), "breakdown", {"value": "auto"})
    sub(pane, "mark", {"class": "Automatic"})
    # Band pane: grey bars, one quarter wide (V3 SOURCES [B]), 40% opacity, darker when Is active crisis.
    pane = sub(panes, "pane", {"id": PANE_BAND, "selection-relaxation-option": "selection-relaxation-allow",
                               "y-axis-name": q(I_BAND)})
    sub(sub(pane, "view"), "breakdown", {"value": "auto"})
    sub(pane, "mark", {"class": "Bar"})
    sub(pane, "mark-sizing", {"custom-mark-size-in-axis-units": "1.0", "mark-alignment": "mark-alignment-left",
                              "mark-sizing-setting": "marks-scaling-on", "use-custom-mark-size": "false"})
    sub(sub(pane, "encodings"), "color", {"column": q(I_ACTIVE)})
    mrule = sub(sub(pane, "style"), "style-rule", {"element": "mark"})
    sub(mrule, "format", {"attr": "mark-transparency", "value": BAND_TRANSPARENCY})
    # Share pane: the v2 stacked area, unchanged.
    pane = sub(panes, "pane", {"id": PANE_SHARE, "selection-relaxation-option": "selection-relaxation-allow",
                               "y-axis-name": q(I_SHARE)})
    sub(sub(pane, "view"), "breakdown", {"value": "auto"})
    sub(pane, "mark", {"class": "Area"})
    sub(sub(pane, "encodings"), "color", {"column": q(I_BUCKET)})
    sub(table, "rows", text=f"({q(I_BAND)} + {q(I_SHARE)})")
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


# ---------------------------------------------------------------- dashboard + windows

W, H = 1000, 700
ROWS = [("title", 50), ("main", 430), ("legend", 50), ("public", 170)]  # px, sums to H


def zone_style(parent, margin):
    zs = sub(parent, "zone-style")
    for attr, val in [("border-color", "#000000"), ("border-style", "none"), ("border-width", "0"),
                      ("margin", margin)]:
        sub(zs, "format", {"attr": attr, "value": val})


def build_dashboard(parent):
    db = sub(parent, "dashboard", {"name": DASHBOARD})
    sub(db, "style")
    sub(db, "size", {"maxheight": H, "maxwidth": W, "minheight": H, "minwidth": W})
    zones = sub(db, "zones")
    root = sub(zones, "zone", {"h": 100000, "id": 1, "type": "layout-basic", "w": 100000, "x": 0, "y": 0})
    flow = sub(root, "zone", {"h": 100000, "id": 2, "param": "vert", "type": "layout-flow", "w": 100000,
                              "x": 0, "y": 0})
    y = 0
    for zid, (kind, px) in enumerate(ROWS, start=3):
        h = round(px * 100000 / H)
        if kind == "title":
            z = sub(flow, "zone", {"fixed-size": px, "h": h, "id": zid, "is-fixed": "true", "type": "text",
                                   "w": 100000, "x": 0, "y": y})
            ft = sub(z, "formatted-text")
            sub(ft, "run", {"bold": "true", "fontcolor": "#0b0b0b", "fontsize": "18"}, TITLE)
            zone_style(z, "8")
        elif kind == "legend":
            z = sub(flow, "zone", {"fixed-size": px, "h": h, "id": zid, "is-fixed": "true",
                                   "leg-item-layout": "horz", "name": SHEET_MAIN, "pane-specification-id": PANE_SHARE,
                                   "param": q(I_BUCKET), "type": "color", "w": 100000, "x": 0, "y": y})
            zone_style(z, "4")
        else:
            name = SHEET_MAIN if kind == "main" else SHEET_PUBLIC
            attrib = {"h": h, "id": zid, "name": name, "w": 100000, "x": 0, "y": y}
            if kind == "public":
                attrib = {"fixed-size": px, **attrib, "is-fixed": "true"}
            z = sub(flow, "zone", attrib)
            zone_style(z, "4")
        y += h
    zone_style(root, "8")


def worksheet_window(parent, name, legend_param=None, legend_pane="0"):
    win = sub(parent, "window", {"class": "worksheet", "name": name})
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
    worksheet_window(wins, SHEET_MAIN, q(I_BUCKET), PANE_SHARE)
    worksheet_window(wins, SHEET_PUBLIC)
    dw = sub(wins, "window", {"class": "dashboard", "maximized": "true", "name": DASHBOARD})
    vps = sub(dw, "viewpoints")
    for name in (SHEET_MAIN, SHEET_PUBLIC):
        sub(sub(vps, "viewpoint", {"name": name}), "zoom", {"type": "entire-view"})
    sub(dw, "active", {"id": "-1"})


# ---------------------------------------------------------------- assemble

def build_tree() -> ET.ElementTree:
    labels = read_ratchet_meta()
    crisis_ids = read_crisis_ids()
    wb = ET.Element("workbook", {"original-version": VERSION, "source-build": SOURCE_BUILD,
                                 "source-platform": "win", "version": VERSION})
    prefs = sub(wb, "preferences")
    sub(prefs, "preference", {"name": "ui.encoding.shelf.height", "value": "24"})
    sub(prefs, "preference", {"name": "ui.shelf.height", "value": "26"})
    dss = sub(wb, "datasources")
    build_parameters(dss, crisis_ids)  # 'Parameters' is always the first datasource (V3 SOURCES [P])
    build_datasource(dss, labels)
    wss = sub(wb, "worksheets")
    build_main_sheet(wss, labels)
    build_public_sheet(wss)
    dbs = sub(wb, "dashboards")
    build_dashboard(dbs)
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
    xml_bytes = serialize(build_tree())
    TWB.write_bytes(xml_bytes)
    stamp = (2026, 1, 1, 0, 0, 0)  # fixed timestamps -> reproducible zip
    tmp = TWBX.with_suffix(".twbx.tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(zipfile.ZipInfo(TWB.name, stamp), xml_bytes, compress_type=zipfile.ZIP_DEFLATED)
        for name in CSV_FILES:
            src = DATA_DIR / name
            if not src.exists():
                sys.exit(f"missing {src}; run `uv run hhdebt export-tableau` first")
            z.writestr(zipfile.ZipInfo(f"{PACKAGED_DIR}/{name}", stamp), src.read_bytes(),
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
    assert [d.get("name") for d in top] == [PARAMS, DS], [d.get("name") for d in top]
    params, ds = top
    assert params.get("hasconnection") == "false" and params.find("connection") is None
    pcol = params.find("column")
    members = [m.get("value") for m in pcol.iterfind("members/member")]
    assert (pcol.get("caption"), pcol.get("value")) == (PARAM_CAPTION, tq(PARAM_DEFAULT))
    assert members == [tq(x) for x in [PARAM_DEFAULT] + read_crisis_ids()], members
    assert ds.get("name") == DS and ds.get("caption") == DS_CAPTION
    tc = ds.find("connection/named-connections/named-connection/connection")
    assert (tc.get("class"), tc.get("directory"), tc.get("filename")) == ("textscan", PACKAGED_DIR, "ratchet.csv")
    meta = [m.findtext("remote-name") for m in ds.iterfind("connection/metadata-records/metadata-record[@class='column']")]
    assert meta == list(RATCHET_FIELDS), meta
    calcs = {c.get("caption"): c.find("calculation").get("formula") for c in ds.iterfind("column[calculation]")}
    assert calcs == {"Band": "IF [recession] = 1 THEN 1 END",
                     "Is active crisis": "[crisis_id] = [Parameters].[Active crisis]"}, calcs
    sheets = [w.get("name") for w in root.iterfind("worksheets/worksheet")]
    dashes = [d.get("name") for d in root.iterfind("dashboards/dashboard")]
    assert sheets == [SHEET_MAIN, SHEET_PUBLIC] and dashes == [DASHBOARD]
    assert len(set(sheets + dashes)) == 3, "sheet and dashboard names must be unique"
    zone_names = {z.get("name") for z in root.iter("zone") if z.get("name")}
    assert zone_names <= set(sheets), zone_names
    marks = [m.get("class") for m in root.iter("mark")]
    assert marks == ["Automatic", "Bar", "Area", "Automatic"], marks
    seqs = check_view_order(root)
    # main sheet: every [ds].[instance] it references is declared in its datasource-dependencies
    main = root.find(f"worksheets/worksheet[@name='{SHEET_MAIN}']/table")
    declared = {f"[{d.get('datasource')}].{ci.get('name')}" for d in main.iterfind("view/datasource-dependencies")
                for ci in d.iterfind("column-instance")}
    refs = {main.findtext("rows")[1:-1].split(" + ")[0], main.findtext("rows")[1:-1].split(" + ")[1],
            main.findtext("cols")}
    refs |= {e.get(k) for e in main.iter() for k in ("column", "field", "y-axis-name")
             if e.get(k, "").startswith(f"[{DS}].")}
    assert refs <= declared, refs - declared
    assert main.find("view/sort") is None and not list(root.iter("manual-sort"))
    pane_ids = [p.get("id") for p in main.iterfind("panes/pane")]
    legend = [z for z in root.iter("zone") if z.get("type") == "color"][0]
    assert pane_ids == [None, PANE_BAND, PANE_SHARE] and legend.get("pane-specification-id") == PANE_SHARE
    share_pane = main.find(f"panes/pane[@id='{PANE_SHARE}']")
    assert share_pane.find("encodings/color").get("column") == legend.get("param") == q(I_BUCKET)
    with zipfile.ZipFile(TWBX) as z:
        names = z.namelist()
        assert z.testzip() is None
        assert z.read(TWB.name) == TWB.read_bytes()
    expected = [TWB.name] + [f"{PACKAGED_DIR}/{n}" for n in CSV_FILES]
    assert names == expected, names
    print("self-check OK: XML parses;", f"datasources {[PARAMS, DS_CAPTION]};",
          f"parameter {PARAM_CAPTION!r} default {PARAM_DEFAULT!r} + {len(members) - 1} crisis ids;",
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
        assert names == [PARAMS, DS], names
        d = wb.datasources[1]
        assert d.caption == DS_CAPTION
        c = d.connections[0]
        assert c.dbclass == "textscan", c.dbclass
        fields = {f.id: f for f in d.fields.values()}
        missing = [n for n in RATCHET_FIELDS if f"[{n}]" not in fields] + [n for n in CALCS if n not in fields]
        assert not missing, missing
        for n, spec in RATCHET_FIELDS.items():
            f = fields[f"[{n}]"]
            assert f.datatype == spec[0], (n, f.datatype)
        for n, spec in CALCS.items():
            f = fields[n]
            assert (f.caption, f.datatype, f.calculation) == (spec[0], spec[1], spec[5]), (n, f.caption)
        pfields = {f.caption: f for f in wb.datasources[0].fields.values()}
        assert PARAM_CAPTION in pfields, list(pfields)
        assert set(wb.worksheets) == {SHEET_MAIN, SHEET_PUBLIC}, wb.worksheets
        main_uses = {f.caption for f in fields.values() if SHEET_MAIN in f.worksheets}
        print(f"tableaudocumentapi OK: {path.name}: worksheets={wb.worksheets} datasources={names} "
              f"caption={d.caption!r} connection class={c.dbclass} fields={len(fields)} "
              f"parameter={pfields[PARAM_CAPTION].caption!r} (worksheets {pfields[PARAM_CAPTION].worksheets})")
        print(f"    fields used on {SHEET_MAIN!r}: {sorted(main_uses)}")
        for n in list(RATCHET_FIELDS) + list(CALCS):
            f = fields[n if n in CALCS else f"[{n}]"]
            extra = f" formula={f.calculation!r}" if f.calculation else ""
            print(f"    {f.id:<34} caption={f.caption!r:<26} datatype={f.datatype:<8} role={f.role}{extra}")


if __name__ == "__main__":
    write_outputs()
    self_check()
    if "--check" in sys.argv[1:]:
        docapi_check()
    if "--corpus" in sys.argv[1:]:  # --corpus DIR: folder of real Tableau .twb files (see V3 SOURCES)
        corpus_order_check(Path(sys.argv[sys.argv.index("--corpus") + 1]))
