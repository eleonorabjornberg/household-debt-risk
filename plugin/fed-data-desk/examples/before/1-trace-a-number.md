# Job 1, before: trace the numbers in a sentence by hand

Sentence: The public share rose from 36.1% to 49.2% between 2007 and 2011, a jump of 13.1 points.

```
$ grep -n "36.1%\|49.2%\|13.1" claims/register.csv | cut -c1-120
9:scope_usd_2007q4_atlas_real,The atlas 2007 step shows total household debt as $21.0T (2026 dollars).,$21.0T,20.95,usd_
13:public_share_2007q4,The public share was 36.1% at the 2007Q4 NBER peak.,36.1%,0.3612,share,2007Q4,README.md:16;README
14:public_share_2011q4,"The public share was 49.2% in 2011Q4, 16 quarters after the 2007Q4 peak.",49.2%,0.4922,share,201
15:gfc_jump_pp,The public share rose 13.1 percentage points from 2007Q4 to 2011Q4.,+13.1 pp | +13.1 pts | 13.1 points | 
22:gfc_counterfactual_pp,"Had private debt stayed at its 2007Q4 level the public share would have risen 6.1 pp, not 13.1
25:gfc_half_private_retreat,About half of the 2007-11 rise was private lenders retreating rather than public expansion.,
77:nyfed_mortgage_change,NY Fed mortgage balances fell $74B in 2026Q2.,−$74B | $74B,-74,usd_bn,2026Q2,web/content/stor
```

Then, by hand, for each row: read its computation column, open validation/results.json or analysis/results.json, find the key, and round it. Several rows match "13.1", so the reader has to judge which one is meant. Nothing tells them whether the printed spelling matches the register or whether the value has changed since.
