# Job 2, before: "What share of household mortgages did the public sector hold in 2026Q2?", by hand

```
$ python3 -c "import json; r=[x for x in json.load(open('web/public/data/public_share.json')) if x['date']=='2026-06-30'][0]; print(r['public_share_mortgage'])"
0.6555413006
```

A bare fraction. To report it, the analyst still has to find out, by reading pipeline code and meta.json: which series it combines; which vintage it is; that "public" means federal + GSE/agency pools + state and local (not the Fed); that it is holdings, not guarantees; and whether a register row exists for it.
