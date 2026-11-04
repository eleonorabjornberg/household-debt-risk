# Regenerates this task's README numbers and register rows from its results files (run from the repo root:
#   uv run --project pipeline python research/b1_market_pricing/make_register_rows.py). Track rows go to claims/tracks/markets.csv; rows the coordinator has
# already folded into claims/register.csv must be removed from one of the two files to avoid duplicate ids.
import csv, json
R = json.load(open('research/b1_market_pricing/results.json'))
header = next(csv.reader(open('claims/register.csv')))
readme = open('research/b1_market_pricing/README.md').read().splitlines()
fence=False; ok=[]
for i,l in enumerate(readme):
    if l.startswith("```"): fence=not fence; continue
    if not fence: ok.append((i+1,l))
def loc(tok):
    L=[f"research/b1_market_pricing/README.md:{n}" for n,l in ok if tok in l]
    assert L, tok; return ";".join(L)
Z="z1:2026-09-11"; F="fred:2026-11-04"; ZF=Z+" "+F
SH="FL153165105 FL893065105 FL403065110 FL403065120 FL403065130 FL403065105 FL413065110 FL413065123 FL413065133 FL413065143 FL313065105 FL213065103"
HL=SH+" FL153166000 FL313066220 FL403066005"
GS="FL153165105 FL893065105 FL403065110 FL403065120 FL413065123 FL413065143"
CT="MORTGAGE30US DGS10 T10Y2Y BAA10Y"
P="research/b1_market_pricing/b1.py -> results.json "
def sg(x,nd=2): return ("−" if x<0 else "")+f"{abs(x):.{nd}f}"
rows=[]
def add(cid,claim,disp,val,unit,per,tok,comp,sids,vint,notes=""):
    rows.append(dict(zip(header,[cid,claim,disp,f"{val:.6g}",unit,per,loc(tok),comp,sids,vint,"UNVERIFIED","",notes])))
add("b1_ci_level","B1 intervals are 95% Newey-West HAC confidence intervals.","95%",0.95,"share","1986Q1-2026Q2","95%","research/b1_market_pricing/METHOD.md (fixed before results)","n/a","n/a","Method constant, not data.")
V=[("main","L","b1_main_l","levels, main",SH+" "+CT),("headline share","L","b1_headline_l","levels, headline share",HL+" "+CT),
   ("5y/10y blend","L","b1_blend_l","levels, 5y/10y blend",SH+" "+CT+" DGS5"),("ends 2022Q3","L","b1_pre2022_l","levels, sample ends 2022Q3",SH+" "+CT),
   ("main","D","b1_main_d","first differences, main",SH+" "+CT),("post-hoc: PMMS 2022Q4+ dummy","L","b1_ph_dummy_l","post-hoc levels with 2022Q4+ dummy",SH+" "+CT),
   ("post-hoc: Fannie+Freddie share","L","b1_ph_gse_l","post-hoc levels, Fannie+Freddie share",GS+" "+CT),("post-hoc: HAC lag 8","L","b1_ph_lag8_l","post-hoc levels, HAC lag 8",SH+" "+CT)]
for v,f,cid,lab,sids in V:
    x=R['public_share_coef'][v][f]; per=f"{x['start']}-{x['end']}"; base=P+f"public_share_coef['{v}']['{f}']"
    note=f"T={x['T']}, HAC lags {x['hac_lags']}."+(" Post-hoc check (METHOD.md, Changes after results)." if v.startswith("post") else "")
    for k,nm in [("coef","coefficient on public share"),("ci_lo","lower 95% HAC bound"),("ci_hi","upper 95% HAC bound")]:
        d=sg(x[k]); add(f"{cid}_{k.replace('ci_','')}",f"B1 {lab}: {nm} {d} pp of spread per unit of share.",d,x[k],"pp",per,d,base+"."+k,sids,ZF,note)
    if f=="L" and v!="post-hoc: HAC lag 8":
        d=sg(x['adf_resid']); add(f"{cid}_adf",f"B1 {lab}: residual ADF statistic {d}.",d,x['adf_resid'],"stat",per,d,base+".adf_resid",sids,ZF,"ADF with constant and 4 lags on the levels residuals.")
for k in ["N7","N8","N3"]:
    v=R['eg_crit_5pct'][k]; d=sg(v)
    add(f"b1_eg_crit_{k.lower()}",f"Engle-Granger 5% critical value ({k}, constant, 157 obs): {d}.",d,v,"stat","n/a",d,P+f"eg_crit_5pct.{k} (statsmodels mackinnoncrit, MacKinnon 2010)","n/a","n/a","Literature constant, not data; checked by the coordinator's quant review (coord-q2).")
x=R['pmms_dummy_coef']; dd=f"{x['coef']:.2f} pp"; add("b1_pmms_dummy",f"B1 post-hoc: the 2022Q4+ dummy coefficient is {dd}.",dd,x['coef'],"pp","1986Q1-2026Q2",dd,P+"pmms_dummy_coef.coef",SH+" "+CT,ZF,"Post-hoc.")
x=R['D_mde80_over_rise_pp']; dd=f"{x:.2f} pp"; add("b1_d_mde80_pp",f"At 5% size and 80% power the first-differences regression detects about {dd} of spread change over the rise in the share.",dd,x,"pp","1986Q1-2026Q2",dd,P+"D_mde80_over_rise_pp (2.8 x SE of main D coefficient x change in mean mort_share)",SH+" "+CT,ZF,"Power statement (coord-q3); assumes short-run = long-run response.")
x=R['S1_mean_change_first_to_last_pp']; dd=f"{x:.2f} pp"; add("b1_s1_mean_change_pp",f"The mean PMMS-Treasury spread rose {dd} from 1986Q1-2008Q2 to 2020Q1-2026Q2.",dd,x,"pp","1986Q1-2026Q2",dd,P+"S1_mean_change_first_to_last_pp","MORTGAGE30US DGS10",F)
for key,pk,per in [("1986_2008q2","1986Q1-2008Q2","1986Q1-2008Q2"),("2008q3_2019","2008Q3-2019Q4","2008Q3-2019Q4"),("2020_latest","2020Q1-latest","2020Q1-2026Q2")]:
    s=R[f"mort_share_mean_{key}"]; m=R[f"S1_mean_{key}"]
    add(f"b1_mort_share_mean_{key}",f"Mean public share of household 1-4 family mortgages, {per}: {100*s:.1f}%.",f"{100*s:.1f}%",s,"share",per,f"{100*s:.1f}%",P+f"mort_share_mean_{key}",SH,Z)
    add(f"b1_s1_mean_{key}",f"Mean 30-year PMMS rate minus 10-year Treasury, {per}: {m:.2f} pp.",f"{m:.2f} pp",m,"pp",per,f"{m:.2f} pp",P+f"S1_mean_{key}","MORTGAGE30US DGS10",F,"Quarterly means of weekly PMMS and daily DGS10.")
d=100*(R['mort_share_mean_2020_latest']-R['mort_share_mean_1986_2008q2'])
add("b1_mort_share_rise_pp",f"The mean mortgage public share rose by about {d:.0f} points from 1986Q1-2008Q2 to 2020Q1-2026Q2.",f"{d:.0f} points",d,"pp","1986Q1-2026Q2",f"{d:.0f} points",P+"mort_share_mean_2020_latest - mort_share_mean_1986_2008q2",SH,Z,f"Unrounded {d:.2f}.")
O="OBMMIJUMBO30YF OBMMIC30YF"
add("b1_s2_jumbo_mean","Jumbo minus conforming 30-year rate (Optimal Blue) averaged 0.03 pp, 2017Q1-2026Q2.","0.03 pp",R['S2_jumbo_conf_mean_2017_latest'],"pp","2017Q1-2026Q2","0.03 pp",P+"S2_jumbo_conf_mean_2017_latest",O,F)
add("b1_s2_jumbo_min","Lowest quarterly jumbo minus conforming spread, 2017Q1-2026Q2: −0.48 pp.","−0.48",R['S2_jumbo_conf_min_2017_latest'],"pp","2017Q1-2026Q2","0.48",P+"S2_jumbo_conf_min_2017_latest",O,F)
add("b1_s2_jumbo_max","Highest quarterly jumbo minus conforming spread, 2017Q1-2026Q2: 0.38 pp.","0.38 pp",R['S2_jumbo_conf_max_2017_latest'],"pp","2017Q1-2026Q2","0.38 pp",P+"S2_jumbo_conf_max_2017_latest",O,F)
add("b1_s2_fha_mean","FHA minus conforming 30-year rate (Optimal Blue) averaged −0.05 pp, 2017Q1-2026Q2.","−0.05 pp",R['S2_fha_conf_mean_2017_latest'],"pp","2017Q1-2026Q2","0.05 pp",P+"S2_fha_conf_mean_2017_latest","OBMMIFHA30YF OBMMIC30YF",F)
ids=[r['claim_id'] for r in rows]; assert len(ids)==len(set(ids))
with open('claims/tracks/markets.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=header); w.writeheader(); w.writerows(rows)
print(len(rows))
