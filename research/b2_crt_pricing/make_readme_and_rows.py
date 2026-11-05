# Regenerates this task's README numbers and register rows from its results files (run from the repo root:
#   uv run --project pipeline python research/b2_crt_pricing/make_readme_and_rows.py). Track rows go to claims/tracks/markets.csv; rows the coordinator has
# already folded into claims/register.csv must be removed from one of the two files to avoid duplicate ids.
import json, csv
R = json.load(open('research/b2_crt_pricing/results.json'))
B, M, C, Y = R['baseline'], R['multiple'], R['credit_cost_bp'], R['by_year']
f1 = lambda x: f"{x:.1f}"; f0 = lambda x: f"{x:.0f}"
rows_y = "\n".join(f"| {y} | {int(v['n_priced'])} of {int(v['n_deals'])} | {f1(v['upb_weighted_cost_bp'])} | {f1(v['cost_per_tranche_pct'])}% | {f0(100*v['sold_share_of_tranche'])}% | {f0(100*v['priced_share_of_crt_upb'])}% |" for y, v in sorted(Y.items()))
lo, hi = R['cost_per_tranche_pct_range']
import pandas as pd
FR = pd.read_csv('research/b2_crt_pricing/freddie_crt_cost.csv').set_index('year')
FN = pd.read_csv('research/b2_crt_pricing/fannie_crt_cost.csv').set_index('year')
m0 = lambda x: f"{x:,.0f}"; p1 = lambda x: f"{100*x:.1f}%"
fr_rows = "\n".join(f"| {y} | {r.scope} | {m0(r.ce_expense)} | {m0(r.crt_debt_interest) if pd.notna(r.crt_debt_interest) else 'not printed'} | "
                    f"{m0(r.gross_cost_musd) if pd.notna(r.gross_cost_musd) else 'n/a'} | {m0(r.net_cost_musd) if pd.notna(r.net_cost_musd) else 'n/a'} | "
                    f"{p1(r.gross_cost_per_maxcov) if pd.notna(r.gross_cost_per_maxcov) else 'n/a'} | {p1(r.ce_expense_per_maxcov)} |" for y, r in FR.iterrows())
fn_rows = "\n".join(f"| {y} | {m0(r.cas)} | {m0(r.cirt)} | {m0(r.cas_cirt_musd)} | {p1(r.cas_cirt_per_rif) if pd.notna(r.cas_cirt_per_rif) else 'n/a'} |" for y, r in FN.iterrows())
g4 = FR.loc[2017:2020, 'gross_cost_per_maxcov']
EL = R['zero_attach_el_bp']; CR = R['credit_cost_bp_range_zero_attach']
txt = f"""# B2: What the market charges for the credit risk the GSEs pass back

> **Claude draft, not the author's text.** Evidence and a proposed reading for Eleonora's own write-up. The numbers are checked and registered; the wording, framing and conclusions are hers to write. The method is Claude's proposal ([`METHOD.md`](METHOD.md), committed before any number), listed for her decision under Q-B2 in `tracks/markets.md`.

**PLAN task B2. Status: ready for review; the write-up is a Claude draft.** Sources and hashes are in [`sources.md`](sources.md). The code is `b2.py`; its tests in `test_b2.py` check transcription against the rendered PDF, include a planted typo, and test the loss engine. Every number in this file has a row in `claims/tracks/markets.csv`.

## What could be priced

Only one free source gives numbers for the price of CRT: FHFA's *CRT Progress Report* of December 2016. For each CAS (Fannie Mae) and STACR (Freddie Mac) deal from 2013 to 2016, it gives an "estimated credit cost", an estimated guarantee fee, and the deal's structure. FHFA estimated each cost from issuance pricing under one baseline loss scenario: 10% prepayment, 0.2% annual defaults, 25% loss given default, and redemption at 10 years. {R['n_deals_priced']} deals have a published cost.

Later FHFA reports show issuance spreads only as charts. Deal-level data from the GSEs and SEC filings are blocked from this environment, and secondary-market spreads are paywalled (`sources.md`). So B2's deal-level pricing covers 2013–2016 deals only. For 2017–2023 the GSEs' 10-Ks give a coarser, aggregate annual cost (section below).

## Result

**At issuance, transferred first-loss risk was priced at several times FHFA's own baseline expected loss.** These are ex-ante model estimates of what the deals cost, not realised payments. Under the baseline scenario a pool loses about {f0(B['cum_pool_loss_bp_at_120m'])} bps of its original balance over ten years. In the {M['n_zero_attach']} deals where the GSE sold the first loss (attachment point 0), the investors' slice absorbs all of it.
- **Credit cost:** a median {f0(C['zero_attach_median'])} bps a year (range {f0(CR[0])}–{f0(CR[1])}).
- **Multiple of the slice's baseline expected loss:** a median {f1(M['zero_attach_median'])} (range {f1(M['zero_attach_min'])} to {f1(M['zero_attach_max'])}), when expected loss is put per year of the average outstanding balance ({f1(EL['outstanding_basis'])} bps). That is the footing on which guarantee fees are charged.
- **On the original balance instead** ({f1(EL['original_basis'])} bps a year), the median multiple is {f1(M['zero_attach_median_original_basis'])}.
- **What the range means:** every zero-attach slice has the same baseline loss, so the range of the multiple is just the range of the cost.

**Unit check.** In every deal with both figures, FHFA's estimated guarantee fee equals the credit cost plus {R['gfee_identity_gaps_bp'][0]} or {R['gfee_identity_gaps_bp'][1]} bps (Treasury allocation, administrative cost and residual risk, per FHFA's footnote). That confirms the cost is in bps a year on the guarantee-fee footing. It also means the cost's share of the fee is an identity, not a finding.

**Deals that kept the first loss** (attachment at 30–100 bps) were cheaper, with a median cost of {f0(C['positive_attach_median'])} bps. Their slice starts at or above the baseline's cumulative loss, so a multiple of expected loss is unstable or undefined for them. {M['n_positive_attach_absent']} of them have no baseline loss at all, and their multiple is recorded as absent.

**By issue year** (`by_year.csv`). "Deals priced" counts the deals in FHFA's cost tables that have a printed credit cost, out of all deals in those tables. FHFA left two seasoned STACR deals (2015-DNA1, 2015-HQ2) out of its cost table, so they are not counted, and CAS 2016-6 is in the table with no printed cost.

| Year | Deals priced | Credit cost, weighted by reference UPB (bps a year) | Cost per dollar of tranche (a year) | Share of tranche actually sold | Priced deals' share of the year's CRT reference UPB |
|---|---|---|---|---|---|
{rows_y}

On FHFA's basis (the whole slice sold), protection cost about {f1(lo)}–{f1(hi)}% a year per dollar of tranche. The GSEs actually sold {f0(100*R['sold_share_of_tranche_range'][0])}–{f0(100*R['sold_share_of_tranche_range'][1])}% of the tranches and kept the rest.

The weighted cost rose from 2014 to 2016. Over that period the GSEs moved to selling the first loss, which costs more throughout (above). FHFA gives two reasons for 2016:
- For CAS: "The estimated credit cost of CAS issuances increased in 2016 because Fannie Mae sold the first loss position to investors."
- For STACR: costs "increased modestly over the first half of 2016 primarily due to widening spreads in the credit markets, but then moderated".

## What this does and does not show

- **This is FHFA's estimate, not a market spread series.** The cost is derived from issuance pricing under one scenario, and it assumes the whole slice is sold.
- **A multiple above 1 is the premium over FHFA's baseline, not over expected losses in general.** It mixes investors' risk aversion with any belief that losses will exceed the baseline, and the two cannot be separated here. It also depends on the loss basis (about {f1(M['zero_attach_median'])} or {f1(M['zero_attach_median_original_basis'])}).
- **Tie to A2.** The priced deals cover most of each year's CRT reference UPB (last column). The rest is insurance (CIRT, ACIS) and unpriced deals. The two sources are not reconciled deal by deal. A2's net-exposure bounds (`research/a2_net_exposure/`) are the quantity this price applies to. B2 does not recompute them.
- **2017 onward has no deal-level prices.** Only the aggregate 10-K measure above. Reading issuance spreads off FHFA's charts would be an estimate with a stated reading error; it was not done.

## 2017–2023: aggregate annual cost from the GSEs' 10-Ks

Eleonora's choice (card b2-1723, option (i), 2026-11-05). After 2016 FHFA no longer prints deal-level credit costs, and the GSEs' deal data are not reachable from here (crt.freddiemac.com, capitalmarkets.freddiemac.com; `sources.md`). What the 10-Ks give instead is the yearly cost of each GSE's whole CRT programme. It is a coarser measure than the deal table above: a cost per dollar of protection outstanding, pooled over every vintage still in force, not a price set at issuance. It is not set against FHFA's expected loss. Code: `gse_10k.py`; data: `freddie_crt_cost.csv`, `fannie_crt_cost.csv`.

**Freddie Mac** ($ millions a year; each year from the first 10-K that prints it):

| Year | Scope | Credit-enhancement expense | Interest on CRT debt | Total | Total less Freddie's reinvestment estimate | Total per dollar of CRT maximum coverage | Credit-enhancement expense per dollar of cover |
|---|---|---|---|---|---|---|---|
{fr_rows}

**Fannie Mae** (cash paid or transferred to investors, $ millions a year):

| Year | CAS | CIRT | CAS + CIRT | Per dollar of CRT risk in force |
|---|---|---|---|---|
{fn_rows}

- **Freddie's series breaks in 2021.** From its FY2021 10-K on, Freddie no longer prints the interest on its CRT debt (STACR debt notes), which was ${m0(FR.loc[2020, 'crt_debt_interest'])} million in 2020. From 2021 only the credit-enhancement expense is shown, and for 2022–2023 only the consolidated figure, which includes a small multifamily part. So 2021–2023 are lower bounds and are not comparable with 2017–2020. The last column is the one measure that runs through all seven years, and it rises partly because Freddie moved from debt notes to trust and insurance structures whose cost is booked as credit-enhancement expense (FY2019 10-K: "We no longer issue debt with embedded credit enhancements as part of our primary CRT strategy").
- **Gross against net.** Freddie's interest on CRT debt is gross interest; Fannie's CAS figure is interest net of LIBOR or SOFR, plus CAS REMIC and CLN payments. Freddie prints its own estimate of reinvestment income on the debt proceeds, shown in the "less" column. The two GSEs are not compared directly.
- **Different denominators.** Freddie: maximum coverage of its CRT, from the 10-K coverage tables (A2, `research/a2_net_exposure/freddie_ce_outstanding.csv`), averaged over the two year ends. Fannie: CRT risk in force, printed rounded to whole billions and found at both year ends only for 2021–2023 (A2, `fannie_ce_outstanding.csv`); other years are n/a.
- **Excluded.** Fannie's lender risk-sharing payments (in `fannie_crt_cost.csv`) and mortgage insurance.
- **Restatements kept, not smoothed.** Freddie's FY2020 10-K restates its 2018 and 2019 credit-enhancement expense; the table shows first publication, the CSV both.
- **Against 2013–2016.** Freddie's 2017–2020 total per dollar of cover, {p1(g4.min())}–{p1(g4.max())} a year, falls inside the {f1(lo)}–{f1(hi)}% range of FHFA's 2013–2016 cost per dollar of tranche. The bases differ (outstanding cover of all vintages against an issuance estimate for the whole slice), so this is a consistency check, not a test of the earlier result.

## Reproduce

```bash
uv run --project pipeline python research/b2_crt_pricing/b2.py
uv run --project pipeline python research/a2_net_exposure/freddie_10k.py      # Freddie 10-K PDFs (freddiemac.com)
SEC_USER_AGENT='<declared>' uv run --project pipeline python research/a2_net_exposure/fannie_10k.py   # Fannie 10-Ks (EDGAR)
uv run --project pipeline python research/b2_crt_pricing/gse_10k.py
uv run --project pipeline pytest -q research/b2_crt_pricing
```
"""
open('research/b2_crt_pricing/README.md', 'w').write(txt)
# register rows
header = next(csv.reader(open('claims/register.csv')))
lines = txt.splitlines(); fence = False; ok = []
for i, l in enumerate(lines):
    if l.startswith("```"): fence = not fence; continue
    if not fence: ok.append((i + 1, l))
NEW = next(i for i, l in ok if l.startswith("## 2017–2023: aggregate annual cost"))
def loc(tok):   # the 2013-2016 rows point only at lines above the 2017-2023 section
    L = [f"research/b2_crt_pricing/README.md:{i}" for i, l in ok if tok in l and i < NEW]
    assert L, tok; return ";".join(L)
P = "research/b2_crt_pricing/b2.py -> results.json "
SRC = "FHFA CRT Progress Report Dec 2016 (deal and credit-cost tables)"
out = []
def add(cid, claim, disp, val, comp, unit, period="2013-2016", sids=SRC, vint="n/a", status="UNVERIFIED", notes="", tok=None):
    out.append(dict(zip(header, [cid, claim, disp, f"{val:.6g}", unit, period, loc(tok or disp), comp, sids, vint, status, "", notes])))
add("b2_n_priced", f"{R['n_deals_priced']} CAS/STACR deals have a published FHFA credit cost.", str(R['n_deals_priced']), R['n_deals_priced'], P+"n_deals_priced", "count", tok=f"{R['n_deals_priced']} deals")
add("b2_baseline_cum_loss", f"Baseline cumulative pool loss over ten years: about {f0(B['cum_pool_loss_bp_at_120m'])} bps.", f"{f0(B['cum_pool_loss_bp_at_120m'])} bps", B['cum_pool_loss_bp_at_120m'], P+"baseline.cum_pool_loss_bp_at_120m", "bp", notes="Computed from FHFA's stated scenario; ESTIMATE of FHFA's baseline, not a forecast.", status="ESTIMATE")
add("b2_cost_zero_attach", f"Median credit cost, zero-attach deals: {f0(C['zero_attach_median'])} bps.", f"{f0(C['zero_attach_median'])} bps", C['zero_attach_median'], P+"credit_cost_bp.zero_attach_median", "bp", tok=f"{f0(C['zero_attach_median'])} bps a year")
add("b2_multiple_median", f"Median multiple of baseline EL, zero-attach deals (outstanding basis): {f1(M['zero_attach_median'])}.", f1(M['zero_attach_median']), M['zero_attach_median'], P+"multiple.zero_attach_median", "ratio", status="ESTIMATE")
add("b2_multiple_min", f"Lowest multiple, zero-attach deals: {f1(M['zero_attach_min'])}.", f1(M['zero_attach_min']), M['zero_attach_min'], P+"multiple.zero_attach_min", "ratio", status="ESTIMATE")
add("b2_multiple_max", f"Highest multiple, zero-attach deals: {f1(M['zero_attach_max'])}.", f1(M['zero_attach_max']), M['zero_attach_max'], P+"multiple.zero_attach_max", "ratio", status="ESTIMATE")
add("b2_multiple_orig", f"Median multiple on the original-balance basis: {f1(M['zero_attach_median_original_basis'])}.", f1(M['zero_attach_median_original_basis']), M['zero_attach_median_original_basis'], P+"multiple.zero_attach_median_original_basis", "ratio", status="ESTIMATE")
add("b2_el_outstanding", f"Zero-attach slice baseline EL, outstanding basis: {f1(EL['outstanding_basis'])} bps a year.", f"{f1(EL['outstanding_basis'])} bps", EL['outstanding_basis'], P+"zero_attach_el_bp.outstanding_basis", "bp", status="ESTIMATE")
add("b2_el_original", f"Zero-attach slice baseline EL, original basis: {f1(EL['original_basis'])} bps a year.", f"{f1(EL['original_basis'])} bps", EL['original_basis'], P+"zero_attach_el_bp.original_basis", "bp", status="ESTIMATE")
for nm, x in [("lo", CR[0]), ("hi", CR[1])]:
    add(f"b2_cost_range_{nm}", f"Zero-attach credit cost range, {'low' if nm=='lo' else 'high'}: {f0(x)} bps.", f0(x), x, P+f"credit_cost_bp_range_zero_attach[{0 if nm=='lo' else 1}]", "bp", tok=f"(range {f0(CR[0])}–" if nm=='lo' else f"–{f0(CR[1])})")
for i, g in enumerate(R['gfee_identity_gaps_bp']):
    add(f"b2_gfee_gap_{g}", f"FHFA estimated guarantee fee = credit cost + {g} bps on some deals.", f"{g} bps" if i else str(g), g, P+"gfee_identity_gaps_bp", "bp", tok=f"{g} bps" if i else f"plus {g} or")
for nm, x in [("lo", R['sold_share_of_tranche_range'][0]), ("hi", R['sold_share_of_tranche_range'][1])]:
    add(f"b2_sold_share_{nm}", f"Share of tranche actually sold, {'lowest' if nm=='lo' else 'highest'} year: {f0(100*x)}%.", f"{f0(100*x)}" if nm=='lo' else f"{f0(100*x)}%", x, P+f"sold_share_of_tranche_range[{0 if nm=='lo' else 1}]", "share", tok=f"{f0(100*x)}–" if nm=='lo' else f"–{f0(100*x)}%")
add("b2_cost_pos_attach", f"Median credit cost, positive-attach deals: {f0(C['positive_attach_median'])} bps.", f"{f0(C['positive_attach_median'])} bps", C['positive_attach_median'], P+"credit_cost_bp.positive_attach_median", "bp")
for y, v in sorted(Y.items()):
    add(f"b2_{y}_wcost", f"{y}: UPB-weighted credit cost {f1(v['upb_weighted_cost_bp'])} bps.", f1(v['upb_weighted_cost_bp']), v['upb_weighted_cost_bp'], P+f"by_year.{y}.upb_weighted_cost_bp", "bp", period=y)
    add(f"b2_{y}_per_tranche", f"{y}: cost per dollar of tranche {f1(v['cost_per_tranche_pct'])}% a year.", f"{f1(v['cost_per_tranche_pct'])}%", v['cost_per_tranche_pct']/100, P+f"by_year.{y}.cost_per_tranche_pct", "share", period=y, status="ESTIMATE", notes="FHFA basis: 100% of the slice sold.")
    add(f"b2_{y}_sold_share", f"{y}: share of tranche actually sold {f0(100*v['sold_share_of_tranche'])}%.", f"{f0(100*v['sold_share_of_tranche'])}%", v['sold_share_of_tranche'], P+f"by_year.{y}.sold_share_of_tranche", "share", period=y)
    add(f"b2_{y}_priced_share", f"{y}: priced deals cover {f0(100*v['priced_share_of_crt_upb'])}% of the year's CRT reference UPB.", f"{f0(100*v['priced_share_of_crt_upb'])}%", v['priced_share_of_crt_upb'], P+f"by_year.{y}.priced_share_of_crt_upb", "share", period=y, sids=SRC+"; A2 crt_fhfa.csv annual_ref_upb_musd")
for nm, disp, val in [("cpr", "10%", 0.10), ("cdr", "0.2%", 0.002), ("lgd", "25%", 0.25)]:
    add(f"b2_fhfa_{nm}", f"FHFA baseline scenario / assumption: {nm} = {disp} (Dec 2016 report, credit-cost footnote).", disp, val,
        "sources.md quote (FHFA CRT Progress Report Dec 2016, report pages 13-14)", "share", notes="Source constant, quoted.", tok=disp if nm != "cpr" else "10% prepayment")
for y, v in sorted(Y.items()):
    t = f"{int(v['n_priced'])} of {int(v['n_deals'])}"
    add(f"b2_{y}_n_priced", f"{y}: {t} deals have a published credit cost.", t, v['n_priced'], P+f"by_year.{y}.n_priced / n_deals", "count", period=y)
for nm, x in [("lo", lo), ("hi", hi)]:
    add(f"b2_per_tranche_{nm}", f"Cost per dollar of tranche, {'lowest' if nm=='lo' else 'highest'} year: {f1(x)}%.", f1(x) if nm=='lo' else f"{f1(x)}%", x/100, P+f"cost_per_tranche_pct_range[{0 if nm=='lo' else 1}]", "share", status="ESTIMATE", tok=f"{f1(x)}–" if nm=='lo' else f"–{f1(x)}%")
def loc_after(head, key):
    st = next(i for i, l in ok if l.startswith(head))
    L = [f"research/b2_crt_pricing/README.md:{i}" for i, l in ok if i > st and l.startswith(key)]
    assert L, (head, key); return L[0]
FS, NS = "Freddie Mac 10-K FY2019 Table 22, FY2020 Table 24, FY2021 segment table, FY2022-23 statements", "Fannie Mae 10-K FY2017-2023 (SEC EDGAR)"
def add2(cid, claim, disp, val, comp, unit, period, line, sids, status="UNVERIFIED", notes=""):
    out.append(dict(zip(header, [cid, claim, disp, f"{val:.6g}", unit, period, line, comp, sids, "10k:2026-11-04", status, "", notes])))
FH, NH = "| Year | Scope", "| Year | CAS |"
for y, r in FR.iterrows():
    ln = loc_after(FH, f"| {y} |")
    C = "research/b2_crt_pricing/gse_10k.py -> freddie_crt_cost.csv "
    add2(f"b2_fre_{y}_ce", f"Freddie {y}: credit-enhancement expense ${m0(r.ce_expense)}M ({r.scope}).", m0(r.ce_expense), r.ce_expense, C+"ce_expense", "usd_m", str(y), ln, FS)
    for col, nm in [("crt_debt_interest", "interest on CRT debt"), ("gross_cost_musd", "total CRT cost"), ("net_cost_musd", "total less reinvestment estimate")]:
        if pd.notna(r[col]):
            add2(f"b2_fre_{y}_{col}", f"Freddie {y}: {nm} ${m0(r[col])}M.", m0(r[col]), r[col], C+col, "usd_m", str(y), ln, FS)
    if pd.notna(r.gross_cost_per_maxcov):
        add2(f"b2_fre_{y}_gross_rate", f"Freddie {y}: total CRT cost per dollar of CRT maximum coverage {p1(r.gross_cost_per_maxcov)}.", p1(r.gross_cost_per_maxcov), r.gross_cost_per_maxcov, C+"gross_cost_per_maxcov", "share", str(y), ln, FS+"; A2 freddie_ce_outstanding.csv", "ESTIMATE")
    add2(f"b2_fre_{y}_ce_rate", f"Freddie {y}: credit-enhancement expense per dollar of CRT maximum coverage {p1(r.ce_expense_per_maxcov)}.", p1(r.ce_expense_per_maxcov), r.ce_expense_per_maxcov, C+"ce_expense_per_maxcov", "share", str(y), ln, FS+"; A2 freddie_ce_outstanding.csv", "ESTIMATE",
         "2021-23 not comparable with 2017-20 (series break)" if y >= 2021 else "")
for y, r in FN.iterrows():
    ln = loc_after(NH, f"| {y} |")
    C = "research/b2_crt_pricing/gse_10k.py -> fannie_crt_cost.csv "
    for col, nm in [("cas", "CAS cash paid"), ("cirt", "CIRT cash paid"), ("cas_cirt_musd", "CAS + CIRT cash paid")]:
        add2(f"b2_fnm_{y}_{col}", f"Fannie {y}: {nm} ${m0(r[col])}M.", m0(r[col]), r[col], C+col, "usd_m", str(y), ln, NS)
    if pd.notna(r.cas_cirt_per_rif):
        add2(f"b2_fnm_{y}_rate", f"Fannie {y}: CAS + CIRT cash per dollar of CRT risk in force {p1(r.cas_cirt_per_rif)}.", p1(r.cas_cirt_per_rif), r.cas_cirt_per_rif, C+"cas_cirt_per_rif", "share", str(y), ln, NS+"; A2 fannie_ce_outstanding.csv", "ESTIMATE")
brk = next(i for i, l in ok if l.startswith("- **Freddie's series breaks in 2021.**"))
add2("b2_fre_2020_crt_debt_interest_note", f"Freddie 2020 interest on CRT debt ${m0(FR.loc[2020, 'crt_debt_interest'])}M (series-break note).", f"${m0(FR.loc[2020, 'crt_debt_interest'])} million", FR.loc[2020, 'crt_debt_interest'], "research/b2_crt_pricing/gse_10k.py -> freddie_crt_cost.csv crt_debt_interest", "usd_m", "2020", f"research/b2_crt_pricing/README.md:{brk}", FS)
ag = next(i for i, l in ok if l.startswith("- **Against 2013–2016.**"))
add2("b2_fre_1720_rate_lo", f"Freddie 2017-2020 total CRT cost per dollar of cover, lowest year {p1(g4.min())}.", p1(g4.min()), g4.min(), "gse_10k.py -> freddie_crt_cost.csv min(gross_cost_per_maxcov, 2017-2020)", "share", "2017-2020", f"research/b2_crt_pricing/README.md:{ag}", FS, "ESTIMATE")
add2("b2_fre_1720_rate_hi", f"Freddie 2017-2020 total CRT cost per dollar of cover, highest year {p1(g4.max())}.", p1(g4.max()), g4.max(), "gse_10k.py -> freddie_crt_cost.csv max(gross_cost_per_maxcov, 2017-2020)", "share", "2017-2020", f"research/b2_crt_pricing/README.md:{ag}", FS, "ESTIMATE")
assert all(float(r['value']) >= 0 for r in out)
p = 'claims/tracks/markets.csv'
old = [r for r in csv.DictReader(open(p)) if not r['claim_id'].startswith('b2_')]
# Rows the coordinator has already folded into claims/register.csv stay there (no duplicate ids); they must still
# match what this script would write, apart from the location if the README moved (checked, not silently kept).
reg = {r['claim_id']: r for r in csv.DictReader(open('claims/register.csv'))}
for r in out:
    if r['claim_id'] in reg:
        g = reg[r['claim_id']]
        assert (g['display'], g['value'], g['locations']) == (r['display'], r['value'], r['locations']), (r['claim_id'], g['locations'], r['locations'])
out = [r for r in out if r['claim_id'] not in reg]
with open(p, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=header); w.writeheader(); w.writerows(old + out)
print(len(out), "B2 rows")
