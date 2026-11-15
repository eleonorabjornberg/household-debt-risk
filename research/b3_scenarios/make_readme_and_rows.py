# Regenerates this task's README numbers and register rows from its results files (run from the repo root:
#   uv run --project pipeline python research/b3_scenarios/make_readme_and_rows.py). Track rows go to claims/tracks/markets.csv; rows the coordinator has
# already folded into claims/register.csv must be removed from one of the two files to avoid duplicate ids.
import json, csv, re
R = json.load(open('research/b3_scenarios/results_dfast2026.json'))
P = json.load(open('research/b3_scenarios/presets/dfast2026.json'))
m, w = R['dfast2026_proxy'], R['dfast2026_proxy_with_student']
B = lambda x: f"${x/1000:,.0f}B"
pc = lambda x: f"{100*x:.0f}%"
RR = json.load(open('research/b3_scenarios/results_replay_2008_2012.json'))
RP = json.load(open('research/b3_scenarios/presets/replay_2008_2012.json'))
rr = RR['replay_2008_2012_proxy']; cl = RR['cumulative_loss_pct']
sec2 = f"""## 2008–12 replay preset (Q-B3 (c), second family): labeled a proxy

**What it is.** The banks' realized net charge-off rates, quarter by quarter, from 2008Q1 to 2012Q4. They come from the Fed's charge-off release for all commercial banks, via FRED: `CORSFRMACBS` (single-family mortgages), `CORCCACBS` (cards), `COROCLACBS` (other consumer). The release defines them as "net charge-offs (gross charge-offs minus recoveries) during a quarter divided by the average level of its loans outstanding", multiplied by 400 to annualize (`sources.md`).
- Each quarter's loss is therefore rate ÷ 400, and the twenty-quarter path sets the timing.
- Over the window, cumulative charge-offs were {cl['mortgage']:.1f}% for mortgages and {cl['consumer_other']:.1f}% for other consumer credit (cards and other consumer, weighted as in the DFAST preset).
- Federal student loans are absent: there is no bank series for them.

| Preset | Total losses | Public | Private | Public share of losses |
|---|---|---|---|---|
| 2008–12 replay, bank charge-offs (proxy) | {B(rr['total_musd'])} | {B(rr['public_musd'])} | {B(rr['private_musd'])} | {pc(rr['public_share_of_losses'])} |

**Limits.**
- **Horizon.** The cumulative figure sums twenty quarterly loss rates, each a share of that quarter's average balance, and applies the sum to today's balances. It is an approximation, and it covers five years where DFAST covers nine quarters, so the two presets differ in horizon as well as severity.
- **Upper bound.** The public bucket includes Ginnie (FHA, VA) pools and the GSEs. Bank loss rates on those books likely overstate their losses, so the 42% public share is probably an upper bound.
- **Whose crisis.** This replays the banks' crisis. Bank mortgage books in 2008–12 included subprime and option-ARM loans that the GSEs did not guarantee, so applying bank charge-offs to the GSE book likely overstates public losses. The GSEs' own realized losses (from their 10-Ks) would be the better source for that book, and are a possible refinement. The figures apply one historical path to today's balances, so they are ESTIMATES.

"""
sec = f"""## DFAST preset (Q-B3, decided by Eleonora 2026-11-04): a recession case, labeled a proxy

**What it is.** The Fed's 2026 stress test gives projected loss rates by loan type for the largest banks under its severely adverse scenario, over the nine quarters 2026Q1–2028Q1 (`sources.md`). The preset applies those rates to **every** holder's balances at 2026Q2. That is a proxy: GSE, FHA/VA and federal books are not bank portfolios.
- **Mortgages** take the first-lien rate, 1.5%. Junior liens and HELOCs, at 3.2%, are part of Z.1's mortgages but are not separated, so mortgage losses are understated.
- **Other consumer credit** takes a blend: cards at 17.1% and "other consumer" at 7.3%, weighted by Z.1's revolving share ({pc(P['consumer_other_revolving_weight'])}). The blended rate is {P['consumer_other_rate_pct']:.1f}%.
- **Federal student loans** are not in DFAST, so the main preset leaves them out. A variant gives them the "other consumer" rate, a weak proxy.

| Preset | Total losses | Public | Private | Public share of losses |
|---|---|---|---|---|
| DFAST proxy (federal student loans absent) | {B(m['total_musd'])} | {B(m['public_musd'])} | {B(m['private_musd'])} | {pc(m['public_share_of_losses'])} |
| DFAST proxy, federal student loans at 7.3% (weak proxy) | {B(w['total_musd'])} | {B(w['public_musd'])} | {B(w['private_musd'])} | {pc(w['public_share_of_losses'])} |

**Reading.** In this proxy recession the public sector bears {pc(m['public_share_of_losses'])} of losses.
- **Like for like,** that compares with a public share of holdings of {100*R['public_share_of_holdings_ex_federal_student']:.1f}% once federal student loans are excluded, as they are from the losses ({100*R['public_share_of_holdings']:.1f}% with them).
- **Why the gap:** the public book is mostly mortgages, which have low stressed loss rates, while the high-loss consumer credit is privately held.
- **With federal student loans** at the weak proxy rate, the public share of losses rises to {pc(w['public_share_of_losses'])}.

These are ESTIMATES under a proxy, and three biases are known:
- **Junior liens.** Using the first-lien rate for every mortgage understates junior-lien and HELOC losses, which banks mostly hold. The public share of losses is therefore biased **up**.
- **FFEL loans.** Z.1's "private" student loans include federally guaranteed FFEL loans held by private lenders, whose credit risk is largely federal. The public share is biased **down** on that count. A split needs ED data, and ED is unreachable.
- **No transfer.** No CRT or mortgage-insurance cover is applied (the cap is 0); A2's bounds would lower the public figure.

"""
p = 'research/b3_scenarios/README.md'; s = open(p).read()
s = re.sub(r"## DFAST preset.*?(?=## Not done here)", "", s, flags=re.S)
s = s.replace("## Not done here", sec + sec2 + "## Not done here", 1)
s = s.replace("- **Presets.** A recession case, a 2008–12 replay and so on would each need sourced parameters. Candidate free sources are in Q-B3.", "- **GSE-specific replay.** Freddie Mac 10-K realized credit losses for 2008–12 for the GSE book (freddiemac.com reachable; Fannie blocked): not built.")
s = s.replace("No scenario has been run with real loss parameters, because each preset needs a primary source and Eleonora's sign-off (Q-B3 in `tracks/markets.md`).", "Its scenario presets follow Eleonora's Q-B3 decision (2026-11-04). The DFAST preset and the 2008–12 replay are built, both labeled proxies.")
s = s.replace("**PLAN task B3. Status: engine and tests done; presets and the in-app version wait on Q-B3 and the coordinator.**", "**PLAN task B3. Status: engine, tests and both preset families done (proxies); the in-app version is the coordinator's site work.**")
open(p, 'w').write(s)
header = next(csv.reader(open('claims/register.csv')))
lines = s.splitlines(); fence = False; ok = []
for i, l in enumerate(lines):
    if l.startswith("```"): fence = not fence; continue
    if not fence: ok.append((i + 1, l))
def loc(tok):
    L = [f"research/b3_scenarios/README.md:{i}" for i, l in ok if tok in l]
    assert L, tok; return ";".join(L)
rows = []
SRC = "Fed 2026 Supervisory Stress Test Results, Table 9"
Z = "FL153165105 FL893065105 FL153166000 FL153166100 FL153166400 FL153166220 FL153166205 FL313066220 + catalog holders"
def add(cid, claim, disp, val, unit, comp, sids, vint, status, tok=None, notes="", period=None):
    per = period or ("2008Q1-2012Q4 path on 2026Q2 balances" if cid.startswith("b3_replay") else "2026Q1-2028Q1 rates on 2026Q2 balances")
    rows.append(dict(zip(header, [cid, claim, disp, f"{val:.6g}", unit, per, loc(tok or disp), comp, sids, vint, status, "", notes])))
for k, v in [("first_lien", 1.5), ("junior", 3.2), ("cards", 17.1), ("other_consumer", 7.3)]:
    add(f"b3_dfast_rate_{k}", f"DFAST 2026 severely adverse portfolio loss rate, {k}: {v}%.", f"{v}%", v/100, "share", "sources.md (Table 9, checked against the rendered page)", SRC, "n/a", "UNVERIFIED", notes="Source value, quoted.")
X = "research/b3_scenarios/presets.py -> "
add("b3_rev_weight", "Revolving share of non-federal consumer credit, 2026Q2.", pc(P['consumer_other_revolving_weight']), P['consumer_other_revolving_weight'], "share", X+"presets/dfast2026.json consumer_other_revolving_weight", Z, "z1:2026-09-11", "UNVERIFIED")
add("b3_cons_rate", "Blended DFAST rate for other consumer credit.", f"{P['consumer_other_rate_pct']:.1f}%", P['consumer_other_rate_pct']/100, "share", X+"presets/dfast2026.json consumer_other_rate_pct", Z, "z1:2026-09-11", "ESTIMATE")
add("b3_hold_share_ex_fed_student", "Public share of holdings excluding federal student loans, 2026Q2.", f"{100*R['public_share_of_holdings_ex_federal_student']:.1f}%", R['public_share_of_holdings_ex_federal_student'], "share", X+"results_dfast2026.json public_share_of_holdings_ex_federal_student", Z, "z1:2026-09-11", "UNVERIFIED", period="2026Q2")
for nm, x in [("main", m), ("student", w)]:
    for k in ["total_musd", "public_musd", "private_musd"]:
        add(f"b3_dfast_{nm}_{k.split('_')[0]}", f"DFAST proxy ({nm}): {k.split('_')[0]} losses {B(x[k])}.", B(x[k]), x[k], "usd_m", X+f"results_dfast2026.json {'dfast2026_proxy' if nm=='main' else 'dfast2026_proxy_with_student'}.{k}", Z+"; "+SRC, "z1:2026-09-11", "ESTIMATE", notes="Proxy: bank loss rates on all holders.")
    add(f"b3_dfast_{nm}_pubshare", f"DFAST proxy ({nm}): public share of losses {pc(x['public_share_of_losses'])}.", pc(x['public_share_of_losses']), x['public_share_of_losses'], "share", X+f"results_dfast2026.json {'dfast2026_proxy' if nm=='main' else 'dfast2026_proxy_with_student'}.public_share_of_losses", Z+"; "+SRC, "z1:2026-09-11", "ESTIMATE")
for k in ["mortgage", "consumer_other"]:
    add(f"b3_replay_cum_{k}", f"2008Q1-2012Q4 cumulative bank net charge-offs, {k}: {cl[k]:.1f}%.", f"{cl[k]:.1f}%", cl[k]/100, "share", X+f"results_replay_2008_2012.json cumulative_loss_pct.{k}", "CORSFRMACBS CORCCACBS COROCLACBS FL153166100", "fred:2026-11-04 z1:2026-09-11", "ESTIMATE")
for k in ["total_musd", "public_musd", "private_musd"]:
    add(f"b3_replay_{k.split('_')[0]}", f"2008-12 replay proxy: {k.split('_')[0]} losses {B(rr[k])}.", B(rr[k]), rr[k], "usd_m", X+f"results_replay_2008_2012.json replay_2008_2012_proxy.{k}", Z+"; CORSFRMACBS CORCCACBS COROCLACBS", "fred:2026-11-04 z1:2026-09-11", "ESTIMATE")
add("b3_replay_pubshare", f"2008-12 replay proxy: public share of losses {pc(rr['public_share_of_losses'])}.", pc(rr['public_share_of_losses']), rr['public_share_of_losses'], "share", X+"results_replay_2008_2012.json replay_2008_2012_proxy.public_share_of_losses", Z+"; CORSFRMACBS CORCCACBS COROCLACBS", "fred:2026-11-04 z1:2026-09-11", "ESTIMATE")
p2 = 'claims/tracks/markets.csv'
import os
old = list(csv.DictReader(open(p2))) if os.path.exists(p2) else []
old = [r for r in old if not r['claim_id'].startswith('b3_')]
with open(p2, 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=header); wr.writeheader(); wr.writerows(old + rows)
print(len(rows))
