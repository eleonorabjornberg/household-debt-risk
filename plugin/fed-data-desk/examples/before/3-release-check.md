# Job 3, before: "Is there a new Z.1 release, and what moved?", by hand

```
$ curl -sSI https://www.federalreserve.gov/releases/z1/data/FRB_Z1_csv.zip | grep -i "last-modified\|content-length"
content-length: 64219006
last-modified: Fri, 11 Sep 2026 16:00:03 GMT
$ python3 -c "import json; print(json.load(open('web/public/data/meta.json'))['vintages'])"
{'fred': '2026-10-27', 'nyfed': '2026-10-27', 'z1': '2026-09-11'}
```

Then, by hand: decide whether the dates mean a new release; download and parse a 3 GB CSV; recompute the headlines; diff them against the last release; and search the copy for every number that might now be stale.
