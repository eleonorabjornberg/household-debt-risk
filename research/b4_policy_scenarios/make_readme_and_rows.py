# Regenerates this task's README and its register rows from results.json (run from the repo root:
#   uv run --project pipeline python research/b4_policy_scenarios/make_readme_and_rows.py). Track rows go to
# claims/tracks/markets.csv (every b4_ row there is replaced); rows the coordinator has already folded into
# claims/register.csv must be removed from one of the two files to avoid duplicate ids.
import csv
import json

R = json.load(open("research/b4_policy_scenarios/results.json"))
SP = json.load(open("research/b4_policy_scenarios/student_proxy.json"))   # card cbo-repo-55 (b), student_proxy.py
REC, G = R["recession"], R["gse_release"]
B = G["balances_musd"]
bn = lambda m: f"${m / 1e3:,.0f}B"
pc = lambda x: f"{100 * x:.0f}%"
bn1 = lambda m: f"${m / 1e3:,.1f}B"
PRESET_LABEL = {"dfast2026_proxy": "DFAST 2026 proxy", "replay_2008_2012_proxy": "2008–12 replay proxy"}
D, P = G["by_preset"]["dfast2026_proxy"], G["by_preset"]["replay_2008_2012_proxy"]
lo, hi = G["public_share_of_losses_range"]

grid_rows = "\n".join(
    f"| {pc(d['share_private'])} | {bn(d['public_musd'])} | {pc(d['public_share_of_losses'])} | {bn(p['public_musd'])} | {pc(p['public_share_of_losses'])} |"
    for d, p in zip(D, P))

txt = f"""# B4: Policy-regime scenarios

> **Claude draft, not the author's text.** The status of each policy debate was looked up from primary sources on 2026-11-04 ([`sources.md`](sources.md)), not assumed. How each scenario maps onto the B3 engine is Eleonora's choice: the recession range follows her Q-B3 decision, the GSE range her card b4-gse (a). The student-loan scenario is left out for now (card b4-student-2 (iii)). Method: [`METHOD.md`](METHOD.md).

**PLAN task B4. Status: recession range and GSE-release range done; the student-loan scenario has a CBO budget-side proxy (card cbo-repo-55 (b), 2026-11-11); whether it feeds the loss engine waits on Eleonora.**

| Scenario | Status of the debate (as looked up, 2026-11-04) | Result |
|---|---|---|
| Recession | — | Losses from {bn(REC['total_musd'][0])} to {bn(REC['total_musd'][1])} on 2026Q2 balances. The public share of losses is {pc(REC['public_share_of_losses'][0])} to {pc(REC['public_share_of_losses'][1])} (federal student loans excluded: no loss rate in either preset). The range runs from B3's DFAST proxy to its 2008–12 replay; both are proxies. |
| GSEs released from conservatorship | FHFA's conservatorship page, retrieved 2026-11-04, says "Fannie Mae and Freddie Mac continue to operate under conservatorship, as they have since 2008". The page carries no date of its own and cites the 2025 Scorecard, so it may lag. Only the first page of FHFA news releases (10 items) was checked, and none concerned an exit. So the status is **unconfirmed beyond those two pages**. | Public share of mortgage and other consumer-credit losses (federal student loans excluded) from {pc(lo)} to {pc(hi)} across both recession proxies and 0–100% of the Fannie and Freddie book turning private (below). |
| Student-loan reform | P.L. 119-21, approved July 4, 2025: no Federal Direct PLUS loans for graduate and professional students for periods from July 1, 2026, subject to the statute's transition exception ("Subject to paragraph (8)"); new limits; a Repayment Assistance Plan. | Budget-side proxy only (Eleonora, card cbo-repo-55 (b), 2026-11-11; section below). CBO's projected outlays of the Direct Loan program account over FY{SP['fy_first']}–FY{SP['fy_last']} fell from {bn(SP['sum_before_musd'])} in its January 2025 baseline to {bn(SP['sum_after_musd'])} in its February 2026 baseline. These outlays are the subsidy cost of federal direct loans, not the amount lent, and the change is not a CBO estimate of the law's effect or of lending moving to private lenders. No public share changes. |

- **No transfer.** Neither range applies a CRT or mortgage-insurance transfer. With A2's cover as an input, the public figures would be lower.
- **Two kinds of bound.** The two recession ends differ in horizon as well as severity: nine quarters of stressed bank loss rates against five years of realised bank charge-offs. The upper end is probably an upper bound for the public book (`research/b3_scenarios/README.md`).

## GSE release: who bears the losses (card b4-gse (a))

**What moves.** On release, a share of the losses on Fannie Mae's and Freddie Mac's books (portfolio and pools) turns private: 0% (losses stay on the GSEs' and Treasury's side, as under conservatorship), then 25%, 50%, 75% and 100% (fully private, no backstop). These are scenario points, not forecasts of release terms. Balances and loss rates stay as in B3; only the side of the losses changes.

**What stays public.** Ginnie Mae and FmHA pools, the FHLBs and the other GSEs. The Ginnie pools are federally insured or guaranteed loans (FHA, VA, USDA); VA and USDA guaranties are partial and issuers bear part of the loss, so counting the whole pool as public is a holder-based simplification (see A1's caveat). The split of B3's "GSEs & agency pools" mortgage book ({bn(B['bucket_total'])}, household-apportioned, 2026Q2, from the 2026-09-11 Z.1 release):
- Fannie Mae and Freddie Mac, the book that is released: {bn(B['released_total'])} (Fannie {bn(B['Fannie Mae (portfolio + pools)'])}, Freddie {bn(B['Freddie Mac (portfolio + pools)'])}).
- Ginnie Mae and FmHA pools: {bn(B['Ginnie Mae and FmHA pools'])}.
- FHLBs and other GSEs: {bn(B['FHLBs and other GSEs'])}.

**Result.** Public losses and the public share of losses on mortgages and other consumer credit, by share of the Fannie/Freddie book's losses that turns private. Federal student loans are excluded: neither B3 preset gives them a loss rate, so they add no loss.

| Share turning private | DFAST 2026 proxy: public losses | Public share of losses | 2008–12 replay proxy: public losses | Public share of losses |
|---|---|---|---|---|
{grid_rows}

Total losses do not change with the share: {bn(D[0]['total_musd'])} under the DFAST proxy and {bn(P[0]['total_musd'])} under the replay. At 0% the figures equal the recession range above.

**Caveats.**
- **What "public" means here.** Losses on the books of the GSEs, the federal government and other public holders. Under conservatorship the GSEs' own capital takes losses first and Treasury's Senior Preferred Stock Purchase Agreements stand behind them, so "public" is not the same as taxpayer outlay.
- **Gross of existing risk transfer.** The shares are measured before CRT and mortgage insurance. Fannie and Freddie already pass part of their losses to private investors and insurers today (A2, `research/a2_net_exposure/`), so on a net basis today's arrangement already sits above 0%.
- **One loss rate per class.** B3 applies one mortgage loss rate to every holder, so Fannie and Freddie lose at the same rate as Ginnie's FHA and VA pools. If Ginnie's pools lose more per dollar than the GSE book, the public share at each point is understated, and overstated if they lose less. Relative loss rates are not estimated here.
- **Proxies.** Both loss paths are bank-portfolio proxies (B3).
- **Release is not the same as loss-bearing.** A released GSE would hold more capital and could buy more CRT. The share turning private stands in for those terms, which are not known (option (c) of the card, a specific proposal, was not chosen).

## Student-loan reform: a CBO budget-side proxy (card cbo-repo-55 (b))

> **Claude draft.** Eleonora chose (2026-11-11) to add CBO's data repository as a source for budget-side context only, and to use the Direct Loan account's outlays as a labelled proxy here. Method: `METHOD.md` section 3b. Sources, commit and hashes: [`sources.md`](sources.md).

**What the number is.** CBO's baseline projections of spending by budget account, for the "Federal Direct Student Loan Program Account" (TIN 091-0243-0-1-502). Under the Federal Credit Reform Act, a credit program account receives "an appropriation to cover the cost" of the loans, and that cost is their net present value to the government (2 U.S.C. 661a). So these outlays measure the **subsidy cost** of federal direct loans. They are not the amount lent: loans are paid out through a separate financing account that is not in this file.

**PROXY.** Projected outlays, January 2025 baseline (the last before P.L. 119-21) against February 2026 baseline (the first after), FY{SP['fy_first']}–FY{SP['fy_last']}:

| Fiscal year | January 2025 baseline | February 2026 baseline |
|---|---|---|
{"\n".join(f"| FY{y} | {bn1(SP['path_musd']['2025-01'][str(y)])} | {bn1(SP['path_musd']['2026-02'][str(y)])} |" for y in range(SP['fy_first'], SP['fy_last'] + 1))}
| Total | {bn(SP['sum_before_musd'])} | {bn(SP['sum_after_musd'])} |

The total fell by {bn(-SP['change_musd'])}, or {pc(-SP['change_share'])}.

**What this does not show.**
- **Not the law's effect alone.** A change between two baselines also carries every economic and technical revision CBO made in the thirteen months between them. The repository does not separate them.
- **Not a shift to private lending.** Neither the CBO repository nor this proxy says how much graduate borrowing moves to private lenders. ED's final rule estimates the fall in federal disbursements (`sources.md`), not where the borrowing goes.
- **Not a loss.** The B3 loss engine is not run for this scenario, so no public share of losses changes. Whether and how this proxy should feed the engine is open (proposed card to Eleonora, `METHOD.md` 3b).
- **Projections, not outturns.** Both baselines are forecasts. Program-account outlays also move with reestimates and loan modifications, which can be large in a single year.

## Reproduce

```bash
uv run --project pipeline python research/b3_scenarios/engine.py        # exposures (Z.1 2026-09-11)
uv run --project pipeline python research/b4_policy_scenarios/b4.py
uv run --project pipeline python research/b4_policy_scenarios/cbo_extract.py      # CBO repo at commit 284a956 (github.com)
uv run --project pipeline python research/b4_policy_scenarios/student_proxy.py
uv run --project pipeline python research/b4_policy_scenarios/make_readme_and_rows.py
```
"""
open("research/b4_policy_scenarios/README.md", "w").write(txt)

# ------------------------------------------------------------------ register rows
lines = txt.split("\n")


def loc(display, start=0):
    for i, l in enumerate(lines[start:], start + 1):
        if display in l:
            return f"research/b4_policy_scenarios/README.md:{i}"
    raise SystemExit(f"{display} not in README")


V = "z1:2026-09-11 fred:2026-11-04"
SRC = "research/b3_scenarios results (dfast2026_proxy, replay_2008_2012_proxy)"
GSER = "FL403065110 FL413065143 FL403065120 FL413065123 FL413065110 FL413065133 FL403065105 FL413065105 FL153165105 FL893065105"
rows = []


def add(cid, claim, display, value, unit, comp, series, note, start=0, val="ESTIMATE", vintage=V):
    rows.append({"claim_id": cid, "claim": claim, "display": display, "value": f"{value:.6g}", "unit": unit,
                 "period": "2026Q2 balances", "locations": loc(display.split(" | ")[0], start),
                 "computation": f"research/b4_policy_scenarios/b4.py -> results.json {comp}", "series_ids": series,
                 "vintage": vintage, "validation": val, "check_id": "", "notes": note})


rec_line = next(i for i, l in enumerate(lines) if l.startswith("| Recession"))
for i, nm in [(0, "lo"), (1, "hi")]:
    add(f"b4_recession_total_{nm}", f"B4 recession range bound: {bn(REC['total_musd'][i])}.", bn(REC["total_musd"][i]),
        REC["total_musd"][i], "usd_m", f"recession.total_musd[{i}]", SRC, "Range from two B3 proxy presets.", rec_line)
    add(f"b4_recession_pubshare_{nm}", f"B4 recession range bound: {pc(REC['public_share_of_losses'][i])}.",
        pc(REC["public_share_of_losses"][i]), REC["public_share_of_losses"][i], "share",
        f"recession.public_share_of_losses[{i}]", SRC, "Range from two B3 proxy presets.", rec_line)
gse_line = next(i for i, l in enumerate(lines) if l.startswith("| GSEs released"))
for i, (nm, x) in enumerate([("lo", lo), ("hi", hi)]):
    add(f"b4_gse_pubshare_{nm}", f"B4 GSE release: public share of mortgage and other consumer-credit losses (federal student loans excluded), range bound {pc(x)}.", pc(x), x, "share",
        f"gse_release.public_share_of_losses_range[{i}]", SRC + "; " + GSER,
        "Over both B3 proxy presets and 0-100% of the Fannie/Freddie book's losses turning private (card b4-gse (a)).", gse_line)
sec = next(i for i, l in enumerate(lines) if l.startswith("**What stays public.**"))
for key, cid in [("bucket_total", "bucket"), ("released_total", "released"), ("Fannie Mae (portfolio + pools)", "fannie"),
                 ("Freddie Mac (portfolio + pools)", "freddie"), ("Ginnie Mae and FmHA pools", "ginnie"),
                 ("FHLBs and other GSEs", "fhlb_other")]:
    add(f"b4_gse_bal_{cid}", f"B4 GSE release: {key} mortgage balance, household-apportioned, {bn(B[key])}.", bn(B[key]),
        B[key], "usd_m", f"gse_release.balances_musd['{key}']", GSER,
        "Z.1 2026-09-11, 2026Q2, apportioned with FL153165105/FL893065105 as B3. Recomputed independently from Z1.csv by the skeptic (R-20261104-mkt-s36).", sec, val="UNVERIFIED", vintage="z1:2026-09-11")
tab = next(i for i, l in enumerate(lines) if l.startswith("| Share turning private"))
for j, (d, p) in enumerate(zip(D, P)):
    x = int(round(100 * d["share_private"]))
    rows.append({"claim_id": f"b4_gse_param_{x}", "claim": f"B4 GSE release scenario point: {x}% of Fannie/Freddie losses turn private.",
                 "display": pc(d["share_private"]), "value": f"{d['share_private']:.6g}", "unit": "share",
                 "period": "scenario parameter", "locations": loc(f"| {pc(d['share_private'])} |", tab),
                 "computation": "research/b4_policy_scenarios/b4.py SHARES", "series_ids": "n/a", "vintage": "n/a",
                 "validation": "UNVERIFIED", "check_id": "", "notes": "Scenario parameter set by Eleonora's decision (card b4-gse (a)), not data."})
    for nm, r in [("dfast", d), ("replay", p)]:
        add(f"b4_gse_{nm}_{x}_public", f"B4 GSE release, {nm} proxy, {x}% private: public losses {bn(r['public_musd'])}.",
            bn(r["public_musd"]), r["public_musd"], "usd_m", f"gse_release.by_preset[{nm}][{j}].public_musd", SRC + "; " + GSER,
            "Proxy loss rates (B3); scenario share.", tab)
        add(f"b4_gse_{nm}_{x}_pubshare", f"B4 GSE release, {nm} proxy, {x}% private: public share of losses {pc(r['public_share_of_losses'])} (federal student loans excluded).",
            pc(r["public_share_of_losses"]), r["public_share_of_losses"], "share",
            f"gse_release.by_preset[{nm}][{j}].public_share_of_losses", SRC + "; " + GSER, "Proxy loss rates (B3); scenario share.", tab)
tot = next(i for i, l in enumerate(lines) if l.startswith("Total losses do not change"))
add("b4_gse_total_dfast", f"B4 GSE release: total losses under the DFAST proxy {bn(D[0]['total_musd'])}.", bn(D[0]["total_musd"]),
    D[0]["total_musd"], "usd_m", "gse_release.by_preset[dfast][0].total_musd", SRC, "Equals the recession lower bound.", tot)
add("b4_gse_total_replay", f"B4 GSE release: total losses under the replay proxy {bn(P[0]['total_musd'])}.", bn(P[0]["total_musd"]),
    P[0]["total_musd"], "usd_m", "gse_release.by_preset[replay][0].total_musd", SRC, "Equals the recession upper bound.", tot)

CV = "cbo:2026-06-12"
SPC = "research/b4_policy_scenarios/student_proxy.py -> student_proxy.json "
SPS = "CBO cbo-data spending_detail 091-0243-0-1-502"
SPN = "PROXY (card cbo-repo-55 (b)): Direct Loan program-account outlays are subsidy cost, not loan volume; a change between baselines is not a CBO estimate of P.L. 119-21's effect."


def add_sp(cid, claim, display, value, unit, comp, period, start, note=SPN):
    rows.append({"claim_id": cid, "claim": claim, "display": display, "value": f"{value:.6g}", "unit": unit,
                 "period": period, "locations": loc(display, start), "computation": SPC + comp, "series_ids": SPS,
                 "vintage": CV, "validation": "UNVERIFIED", "check_id": "", "notes": note})


per = f"FY{SP['fy_first']}-FY{SP['fy_last']}"
stu = next(i for i, l in enumerate(lines) if l.startswith("| Student-loan reform"))
add_sp("b4_student_cbo_before", f"B4 student-loan proxy: CBO January 2025 baseline Direct Loan program-account outlays, {per}, {bn(SP['sum_before_musd'])}.",
       bn(SP["sum_before_musd"]), SP["sum_before_musd"], "usd_m", "sum_before_musd", per, stu)
add_sp("b4_student_cbo_after", f"B4 student-loan proxy: CBO February 2026 baseline Direct Loan program-account outlays, {per}, {bn(SP['sum_after_musd'])}.",
       bn(SP["sum_after_musd"]), SP["sum_after_musd"], "usd_m", "sum_after_musd", per, stu)
tab2 = next(i for i, l in enumerate(lines) if l.startswith("| Fiscal year | January 2025 baseline"))
for y in range(SP["fy_first"], SP["fy_last"] + 1):
    yl = next(i for i, l in enumerate(lines) if l.startswith(f"| FY{y} |"))
    for b, nm in (("2025-01", "jan2025"), ("2026-02", "feb2026")):
        v = SP["path_musd"][b][str(y)]
        rows.append({"claim_id": f"b4_student_cbo_{nm}_fy{y}", "claim": f"B4 student-loan proxy: CBO {b} baseline, Direct Loan program-account outlays FY{y}, {bn1(v)}.",
                     "display": bn1(v), "value": f"{v:.6g}", "unit": "usd_m", "period": f"FY{y}",
                     "locations": f"research/b4_policy_scenarios/README.md:{yl + 1}",
                     "computation": SPC + f"path_musd['{b}']['{y}'] (cbo_direct_loan_outlays.csv)", "series_ids": SPS,
                     "vintage": CV, "validation": "UNVERIFIED", "check_id": "", "notes": SPN})
tot2 = next(i for i, l in enumerate(lines) if l.startswith("| Total | "))
for key, cid in (("sum_before_musd", "total_before"), ("sum_after_musd", "total_after")):
    add_sp(f"b4_student_cbo_{cid}", f"B4 student-loan proxy table total ({key}), {bn(SP[key])}.", bn(SP[key]), SP[key], "usd_m", key, per, tot2)
fell = next(i for i, l in enumerate(lines) if l.startswith("The total fell by"))
add_sp("b4_student_cbo_fall", f"B4 student-loan proxy: fall in projected outlays between baselines, {per}, {bn(-SP['change_musd'])}.",
       bn(-SP["change_musd"]), -SP["change_musd"], "usd_m", "-change_musd", per, fell)
add_sp("b4_student_cbo_fall_share", f"B4 student-loan proxy: fall in projected outlays between baselines, {per}, {pc(-SP['change_share'])}.",
       pc(-SP["change_share"]), -SP["change_share"], "share", "-change_share", per, fell)

# Signs (the register checker ignores minus signs): every value here is non-negative
assert all(float(r["value"]) >= 0 for r in rows)
import sys
sys.path.insert(0, "research/common")
from track_rows import write_track_rows  # noqa: E402
new = write_track_rows(rows, "b4_")
print(f"README written; {len(rows)} b4 rows, {len(new)} not yet in claims/register.csv")
