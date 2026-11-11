# Regenerates this task's README numbers and register rows from its results files (run from the repo root:
#   uv run --project pipeline python research/c1_nowcast/make_readme_and_rows.py). Track rows go to claims/tracks/markets.csv; rows the coordinator has
# already folded into claims/register.csv must be removed from one of the two files to avoid duplicate ids.
import json, re
R = json.load(open('research/c1_nowcast/results_dev.json'))
rel, rm, n, me = R['rel_rmse_vs_no_change'], R['rmse_pp'], R['n_scored'], R['bridge_mean_error_pp']
nr = R['n_scored_bridge_reg']
pt = {(t['k'], t['candidate'], t['benchmark']): t for t in R['primary_tests']}
f2 = lambda x: f"{x:.2f}"
fp = lambda x: "<0.01" if x < 0.005 else f"{x:.2f}"
def sg(x): return ("−" if x < 0 else "") + f"{abs(x):.2f}"
rows = []
for k in ["1", "2", "3"]:
    b_, r_ = pt[(int(k), 'bridge', 'no_change')], pt[(int(k), 'bridge_reg', 'no_change')]
    rows.append(f"| {k} | {int(n['RT'][k])} | {f2(rel['RT'][k]['bridge'])} | {fp(b_['p'])} / {fp(b_['p_holm'])} | {int(nr['RT'][k])} | {f2(rel['RT'][k]['bridge_reg'])} | {f2(rel['RT'][k]['bridge_on_reg_targets'])} | {fp(r_['p'])} / {fp(r_['p_holm'])} | {f2(rel['RT'][k]['ar1'])} | {f2(rel['RT'][k]['drift'])} |")
bp = R['bridge_mean_error_by_period_pp']['RT']; span = R['regression_target_span']['RT']
sig_reg = [k for k in "123" if pt[(int(k), 'bridge_reg', 'no_change')]['p_holm'] < 0.05]
txt = f"""## Results: development sample only (targets to 2023Q2; holdout not run)

> **Claude draft, not the author's text.** The scores below follow [`EVALUATION.md`](EVALUATION.md), which was committed before any score existed (7ae4afb). Changes made after the first scores, in response to the quant-reviewer and skeptic, are listed there under "Deviations"; the first scores are in commit 58a93d8. The holdout (2023Q3–2026Q2, as frozen in C2) is untouched. So under C2's wording rule, nothing here can yet be called "beats".

**Real time (RT)** means: the Z.1 base comes from the Fed's release archive (all 41 releases from 2016-09-16), the indicators from ALFRED as of each instant, and the target is the first release. Monthly instants run from October 2016; targets run 2016Q3–2023Q2. Each target is scored once per instant index k (k = 1 is the first monthly instant after a Z.1 release). A rare fourth instant before the next release is kept but not scored. RMSE relative to no-change (below 1 is better):

| k | n | Accounting bridge | DM-HLN p / Holm p | n (regression) | Bridge regression | Bridge on the regression's targets | Clark–West p / Holm p | AR(1) | Drift |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

- **The accounting bridge** has an RMSE of {f2(rm['RT']['all']['bridge'])} pp, against {f2(rm['RT']['all']['no_change'])} pp for no-change, pooled over k: about a quarter lower. After the Holm correction the difference is not significant at any k. Under C2's wording it is so far "comparable to the benchmark". Errors at consecutive quarters are autocorrelated within each k, so the lag-0 p-values are, if anything, too small. A post-hoc lag-1 version is in `tests_dev.csv`.
- **The bridge is biased downward.** Its mean error is {sg(me['RT']['all'])} pp. The bias is concentrated in 2020–21 ({sg(bp['2020-21'])}, against {sg(bp['to 2019'])} to 2019 and {sg(bp['2022-23'])} in 2022–23, in pp), and it does not shrink as more monthly data arrive ({sg(me['RT']['1'])} at k = 1, {sg(me['RT']['3'])} at k = 3). Two explanations are open, and neither is tested:
  - The public mortgage holders (agency pools, GSEs) have no monthly indicator in set 2b and are carried flat, while banks' mortgages and consumer credit move with H.8 and G.19.
  - All cells are NSA, so carrying any cell flat across a quarter ignores its seasonal pattern.
- **The bridge regression** fits its intercept to past errors. It is scored only on {span[0]}–{span[1]}, because it needs 12 past first-release pairs. Those years include the 2020–21 period in which the bias was largest, and the regression carries the earlier bias forward.
  - On its own targets it is about half of no-change.
  - The bridge itself, on the same targets, is {f2(min(rel['RT'][k]['bridge_on_reg_targets'] for k in '123'))}–{f2(max(rel['RT'][k]['bridge_on_reg_targets'] for k in '123'))}.
  - After Holm the regression is significant at k = {" and ".join(sig_reg)} only. These are the same targets read at different instants, so they are not independent confirmations.
- **AR(1)** is close to no-change ({f2(min(rel['RT'][k]['ar1'] for k in '123'))}–{f2(max(rel['RT'][k]['ar1'] for k in '123'))}). **Drift** is slightly better ({f2(min(rel['RT'][k]['drift'] for k in '123'))}–{f2(max(rel['RT'][k]['drift'] for k in '123'))}), but worse than the bridge.
- **Against the latest vintage instead of the first release** (RT-latest), the bridge's relative RMSE is {f2(rel['RT-latest']['all']['bridge'])}.

**Pseudo-real-time comparisons** use latest-vintage Z.1, cut at each release's last quarter, so they are *not real-time* for Z.1. Their bridge regression also trains on revised targets. The indicators are still point-in-time. With indicator set 2b, targets 2015Q1–2023Q2, the bridge's relative RMSE is {f2(rel['P2b']['all']['bridge'])}. With set 2a (G.19 federal and total only), targets 2010Q2–2023Q2, it is {f2(rel['P2a']['all']['bridge'])}. All scores are in `scores_dev.csv`, all tests in `tests_dev.csv`, and every nowcast in `nowcasts_dev.csv`.

**What this does not show.**
- It does not show accuracy on unseen data: the holdout has not been run.
- The samples are small (about 20–28 targets per k in RT). All p-values are descriptive.
- C2's placebo and outcome leakage checks are not implemented for C1 (see Deviations).
- The bias finding suggests adding the agency monthly summaries (indicator set 2c), but that would be a new, separately pre-registered run and never a change to this one.

"""
p = 'research/c1_nowcast/README.md'; s = open(p).read()
s = re.sub(r"## Results: development sample only.*?(?=## How \"what was public)", "", s, flags=re.S)
s = s.replace("## How \"what was public on day t\" is answered", txt + "## How \"what was public on day t\" is answered", 1)
s = s.replace("# C1: Nowcasting the public share between Z.1 releases (data plumbing)", "# C1: Nowcasting the public share between Z.1 releases")
s = s.replace("**PLAN task C1. Status: plumbing built; evaluation blocked on Eleonora's design choice.**", "**PLAN task C1. Status: development-sample evaluation done; holdout pending the coordinator.**")
s = s.replace("> **Claude draft, not the author's text.** This describes the plumbing only. The evaluation design is Eleonora's choice: which indicators, the vintage rule, the benchmarks and the metrics. The options, with a recommendation, are in [`tracks/markets.md`](../../tracks/markets.md) under \"Questions for Eleonora\". No nowcast has been computed or evaluated.",
 "> **Claude draft, not the author's text.** The evaluation design is Eleonora's (her Q-C1 decisions of 2026-11-04, recorded in PLAN.md). The implementation details Claude added are marked in `EVALUATION.md`.")
open(p, 'w').write(s)

# ---- register rows for every number in the README, from the same values
import csv
header = next(csv.reader(open('claims/register.csv')))
lines = open(p).read().splitlines()
fence = False; ok = []
for i, l in enumerate(lines):
    if l.startswith("```"): fence = not fence; continue
    if not fence: ok.append((i + 1, l))
def loc(tok):
    L = [f"research/c1_nowcast/README.md:{i}" for i, l in ok if tok in l]
    assert L, tok; return ";".join(L)
V = "z1:2016-09-16 z1:2026-09-11 fred:2026-11-04"
SH = "FL313065105 FL403065105 FL413065105 FL213065103 FL313066220 FL403066005 FL153165105 FL153166000 FL893065105 FL763065105 FL763066005 FL763066000 FL613066005 FL473066000"
IND = "TOTALGOV TOTALDI TOTALFC TOTALTCU TOTALNS RREACBW027NBOG"
P = "research/c1_nowcast/nowcast.py -> results_dev.json "
out = []; seen = set()
def add(cid, claim, disp, val, comp, tok=None, unit="ratio", period="2016Q3-2023Q2", sids=SH + " " + IND, notes="Development sample only; holdout not run. Z.1: every archived release 2016-09-16 to 2026-09-11 (z1_vintage_notes.csv)."):
    if cid in seen: return
    seen.add(cid)
    out.append(dict(zip(header, [cid, claim, disp, f"{val:.6g}", unit, period, loc(tok or disp), comp, sids, "n/a" if 'n/a' in sids else V, "UNVERIFIED", "", notes])))
for k in "123":
    kk = int(k)
    for m in ["bridge", "bridge_reg", "bridge_on_reg_targets", "ar1", "drift"]:
        x = rel['RT'][k][m]; add(f"c1_rt_k{k}_relrmse_{m}", f"C1 RT, k={k}: {m} RMSE relative to no-change {f2(x)}.", f2(x), x, P + f"rel_rmse_vs_no_change.RT.{k}.{m}")
    for cand, bench in [("bridge", "no_change"), ("bridge_reg", "no_change")]:
        t = pt[(kk, cand, bench)]
        for key in ["p", "p_holm"]:
            d = fp(t[key])
            if d == "<0.01": continue   # '<0.01' carries the decimal 0.01 token; registered once below
            add(f"c1_rt_k{k}_{cand}_{key}", f"C1 RT, k={k}: {t['test']} {key} for {cand} vs no-change {d}.", d, t[key], P + f"primary_tests[k={k},{cand},{bench}].{key}", unit="p")
add("c1_p_floor", "C1 p-values below 0.005 are printed as <0.01.", "<0.01", 0.01, "display convention", tok="<0.01", unit="p", sids="n/a", notes="Display threshold, not data.")
for m in ["bridge", "no_change"]:
    x = rm['RT']['all'][m]; add(f"c1_rt_rmse_{m}", f"C1 RT pooled RMSE of {m}: {f2(x)} pp.", f"{f2(x)} pp", x, P + f"rmse_pp.RT.all.{m}", unit="pp")
for per in ["2020-21", "to 2019", "2022-23"]:
    x = bp[per]; add(f"c1_rt_bias_{per.replace(' ', '_').replace('-', '_')}", f"C1 RT bridge mean error, {per}: {sg(x)} pp.", sg(x), x, P + f"bridge_mean_error_by_period_pp.RT.{per}", tok=sg(x), unit="pp", notes="Descriptive diagnostic (post-hoc, quant-reviewer q13).")
for k in ["all", "1", "3"]:
    x = me['RT'][k]; add(f"c1_rt_bias_{k}", f"C1 RT bridge mean error (k={k}): {sg(x)} pp.", sg(x) if k != "all" else sg(x) + " pp", x, P + f"bridge_mean_error_pp.RT.{k}", tok=sg(x), unit="pp", notes="Descriptive diagnostic.")
for smp in ["RT-latest", "P2b", "P2a"]:
    x = rel[smp]['all']['bridge']; add(f"c1_{smp.lower().replace('-', '_')}_relrmse_bridge", f"C1 {smp}: bridge RMSE relative to no-change {f2(x)}.", f2(x), x, P + f"rel_rmse_vs_no_change.{smp}.all.bridge",
        period={"RT-latest": "2016Q3-2023Q2", "P2b": "2015Q1-2023Q2", "P2a": "2010Q2-2023Q2"}[smp],
        notes="Development sample only." + ("" if smp == "RT-latest" else " Pseudo-real-time: latest-vintage Z.1, point-in-time indicators."))
cw = csv.DictWriter(open('claims/tracks/markets.csv', 'a', newline=''), fieldnames=header)
for r in out: cw.writerow(r)
print(len(out), "C1 rows")
