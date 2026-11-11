# Recorded tool calls

Recorded before 2026-11-11, when the `caveats` field was renamed `limits`.

Real calls made through an MCP stdio client against the snapshot backend (`web/public/data`, Z.1 vintage 2026-09-11). Output is verbatim JSON from the server. Regenerate with `uv run python examples/record_transcripts.py`.

## Public share, 2026Q2

`public_share({"start": "2026Q2", "end": "2026Q2"})`

```json
{
  "ok": true,
  "tool": "public_share",
  "backend": "snapshot",
  "source": "z1",
  "vintage": {
    "source_vintage": "2026-09-11",
    "all": {
      "fred": "2026-10-27",
      "nyfed": "2026-10-27",
      "z1": "2026-09-11",
      "snapshot_generated_at": "2026-10-27T22:13:44+00:00",
      "source": "meta.json (database export)"
    }
  },
  "units": {
    "public_share": "fraction 0-1 (display as %)",
    "public_musd": "USD millions, end of quarter, not seasonally adjusted (Z.1 levels)",
    "scope_total_musd": "USD millions, end of quarter, not seasonally adjusted (Z.1 levels)",
    "measure": "total"
  },
  "series_ids": [
    "FL154104015",
    "FL153165105",
    "FL153166000",
    "FL313065105",
    "FL403065105",
    "FL413065105",
    "FL213065103",
    "FL313066220",
    "FL403066005"
  ],
  "caveats": [
    "Z.1 levels are end-of-quarter and not seasonally adjusted.",
    "Holding is not a guarantee: a public holder owning a loan is not the same as the public guaranteeing it, and a private holder may be protected by a guarantee.",
    "Mortgage holders are reported for ALL 1-4 family mortgages (incl. business borrowers) and apportioned to households by each holder's share; this is a method, not a published Z.1 holder split for households.",
    "Scope = household and nonprofit 1-4 family mortgages + consumer credit (FL154104015), about 87% of total household liabilities; it excludes HELOCs-as-separate-line, business debt and other liabilities.",
    "Public = federal government (direct) + GSEs & agency pools + state & local governments. Dollars are nominal.",
    "fed_mbs_musd (Fed MBS, WSHOMCB) is a QE overlay already inside agency pools; never add it."
  ],
  "data": [
    {
      "quarter": "2026Q2",
      "date": "2026-06-30",
      "public_share": 0.5638311569,
      "public_share_display": "56.4%",
      "public_musd": 10767594.115,
      "public_usd_display": "$10.77T",
      "scope_total_musd": 19097196,
      "scope_usd_display": "$19.10T",
      "fed_mbs_musd": 1961590
    }
  ]
}
```

## Risk buckets, 2007Q4

`holdings_by_bucket({"quarter": "2007Q4"})`

```json
{
  "ok": true,
  "tool": "holdings_by_bucket",
  "backend": "snapshot",
  "source": "z1",
  "vintage": {
    "source_vintage": "2026-09-11",
    "all": {
      "fred": "2026-10-27",
      "nyfed": "2026-10-27",
      "z1": "2026-09-11",
      "snapshot_generated_at": "2026-10-27T22:13:44+00:00",
      "source": "meta.json (database export)"
    }
  },
  "units": {
    "nominal_musd": "USD millions, end of quarter, not seasonally adjusted (Z.1 levels)",
    "real_musd": "USD millions, constant dollars of the latest CPI quarter (CPIAUCSL, FRED); an estimate",
    "share_of_scope": "fraction 0-1 of mortgages + consumer credit"
  },
  "series_ids": [
    "FL154104015",
    "FL153165105",
    "FL153166000",
    "FL313065105",
    "FL403065105",
    "FL413065105",
    "FL213065103",
    "FL763065105",
    "FL753065103",
    "FL743065103",
    "FL473065100",
    "FL673065105",
    "FL643065173",
    "FL153065103",
    "FL103065105",
    "FL113065103",
    "FL543065105",
    "FL573065103",
    "FL223065143",
    "FL613065105",
    "FL313066220",
    "FL403066005",
    "FL763066005",
    "FL473066000",
    "FL673066000",
    "FL613066005",
    "FL103066003",
    "FL113066003",
    "FL163066223"
  ],
  "caveats": [
    "Z.1 levels are end-of-quarter and not seasonally adjusted.",
    "Holding is not a guarantee: a public holder owning a loan is not the same as the public guaranteeing it, and a private holder may be protected by a guarantee.",
    "Mortgage holders are reported for ALL 1-4 family mortgages (incl. business borrowers) and apportioned to households by each holder's share; this is a method, not a published Z.1 holder split for households.",
    "Scope = household and nonprofit 1-4 family mortgages + consumer credit (FL154104015), about 87% of total household liabilities; it excludes HELOCs-as-separate-line, business debt and other liabilities.",
    "Six risk buckets are this project's grouping of Z.1 holder sectors (catalog).",
    "real_musd uses a CPI deflator and is not a published Z.1 number."
  ],
  "data": [
    {
      "risk_bucket": "federal_direct",
      "label": "Federal government (direct)",
      "is_public": true,
      "mortgage_musd": 12839.505,
      "consumer_credit_musd": 115657.0,
      "nominal_musd": 128496.505,
      "real_musd": 204147.932,
      "share_of_scope": 0.009744467699999999,
      "share_display": "1.0%",
      "usd_display": "$0.13T",
      "series_ids": [
        "FL313065105",
        "FL313066220"
      ]
    },
    {
      "risk_bucket": "gse_agency",
      "label": "GSEs & agency pools",
      "is_public": true,
      "mortgage_musd": 4549778.17,
      "consumer_credit_musd": 0.0,
      "nominal_musd": 4549778.17,
      "real_musd": 7228428.555,
      "share_of_scope": 0.3450301347,
      "share_display": "34.5%",
      "usd_display": "$4.55T",
      "series_ids": [
        "FL403065105",
        "FL413065105",
        "FL403066005"
      ]
    },
    {
      "risk_bucket": "state_local",
      "label": "State & local governments",
      "is_public": true,
      "mortgage_musd": 84135.052,
      "consumer_credit_musd": 0.0,
      "nominal_musd": 84135.052,
      "real_musd": 133668.981,
      "share_of_scope": 0.0063803393,
      "share_display": "0.6%",
      "usd_display": "$0.08T",
      "series_ids": [
        "FL213065103"
      ]
    },
    {
      "risk_bucket": "banks_credit_unions",
      "label": "Banks & credit unions",
      "is_public": false,
      "mortgage_musd": 3152625.596,
      "consumer_credit_musd": 1131453.0,
      "nominal_musd": 4284078.596,
      "real_musd": 6806300.197,
      "share_of_scope": 0.3248809415,
      "share_display": "32.5%",
      "usd_display": "$4.28T",
      "series_ids": [
        "FL763065105",
        "FL753065103",
        "FL743065103",
        "FL473065100",
        "FL763066005",
        "FL473066000"
      ]
    },
    {
      "risk_bucket": "private_securitization",
      "label": "Private securitization & mortgage REITs",
      "is_public": false,
      "mortgage_musd": 2185095.626,
      "consumer_credit_musd": 652513.0,
      "nominal_musd": 2837608.626,
      "real_musd": 4508231.051,
      "share_of_scope": 0.2151886202,
      "share_display": "21.5%",
      "usd_display": "$2.84T",
      "series_ids": [
        "FL673065105",
        "FL643065173",
        "FL673066000"
      ]
    },
    {
      "risk_bucket": "nonbank_other",
      "label": "Finance companies & other private",
      "is_public": false,
      "mortgage_musd": 592660.051,
      "consumer_credit_musd": 709854.0,
      "nominal_musd": 1302514.051,
      "real_musd": 2069360.176,
      "share_of_scope": 0.09877549669999999,
      "share_display": "9.9%",
      "usd_display": "$1.30T",
      "series_ids": [
        "FL153065103",
        "FL103065105",
        "FL113065103",
        "FL543065105",
        "FL573065103",
        "FL223065143",
        "FL613065105",
        "FL613066005",
        "FL103066003",
        "FL113066003",
        "FL163066223"
      ]
    }
  ],
  "summary": {
    "quarter": "2007Q4",
    "scope_total_musd": 13186611.0,
    "scope_usd_display": "$13.19T",
    "public_musd": 4762409.727,
    "public_share": 0.3611549417056437,
    "public_share_display": "36.1%"
  }
}
```

## Risk buckets, 2011Q4

`holdings_by_bucket({"quarter": "2011Q4"})`

```json
{
  "ok": true,
  "tool": "holdings_by_bucket",
  "backend": "snapshot",
  "source": "z1",
  "vintage": {
    "source_vintage": "2026-09-11",
    "all": {
      "fred": "2026-10-27",
      "nyfed": "2026-10-27",
      "z1": "2026-09-11",
      "snapshot_generated_at": "2026-10-27T22:13:44+00:00",
      "source": "meta.json (database export)"
    }
  },
  "units": {
    "nominal_musd": "USD millions, end of quarter, not seasonally adjusted (Z.1 levels)",
    "real_musd": "USD millions, constant dollars of the latest CPI quarter (CPIAUCSL, FRED); an estimate",
    "share_of_scope": "fraction 0-1 of mortgages + consumer credit"
  },
  "series_ids": [
    "FL154104015",
    "FL153165105",
    "FL153166000",
    "FL313065105",
    "FL403065105",
    "FL413065105",
    "FL213065103",
    "FL763065105",
    "FL753065103",
    "FL743065103",
    "FL473065100",
    "FL673065105",
    "FL643065173",
    "FL153065103",
    "FL103065105",
    "FL113065103",
    "FL543065105",
    "FL573065103",
    "FL223065143",
    "FL613065105",
    "FL313066220",
    "FL403066005",
    "FL763066005",
    "FL473066000",
    "FL673066000",
    "FL613066005",
    "FL103066003",
    "FL113066003",
    "FL163066223"
  ],
  "caveats": [
    "Z.1 levels are end-of-quarter and not seasonally adjusted.",
    "Holding is not a guarantee: a public holder owning a loan is not the same as the public guaranteeing it, and a private holder may be protected by a guarantee.",
    "Mortgage holders are reported for ALL 1-4 family mortgages (incl. business borrowers) and apportioned to households by each holder's share; this is a method, not a published Z.1 holder split for households.",
    "Scope = household and nonprofit 1-4 family mortgages + consumer credit (FL154104015), about 87% of total household liabilities; it excludes HELOCs-as-separate-line, business debt and other liabilities.",
    "Six risk buckets are this project's grouping of Z.1 holder sectors (catalog).",
    "real_musd uses a CPI deflator and is not a published Z.1 number."
  ],
  "data": [
    {
      "risk_bucket": "federal_direct",
      "label": "Federal government (direct)",
      "is_public": true,
      "mortgage_musd": 22099.776,
      "consumer_credit_musd": 494759.0,
      "nominal_musd": 516858.776,
      "real_musd": 761272.146,
      "share_of_scope": 0.041311805699999996,
      "share_display": "4.1%",
      "usd_display": "$0.52T",
      "series_ids": [
        "FL313065105",
        "FL313066220"
      ]
    },
    {
      "risk_bucket": "gse_agency",
      "label": "GSEs & agency pools",
      "is_public": true,
      "mortgage_musd": 5529586.092,
      "consumer_credit_musd": 0.0,
      "nominal_musd": 5529586.092,
      "real_musd": 8144429.517,
      "share_of_scope": 0.4419721532,
      "share_display": "44.2%",
      "usd_display": "$5.53T",
      "series_ids": [
        "FL403065105",
        "FL413065105",
        "FL403066005"
      ]
    },
    {
      "risk_bucket": "state_local",
      "label": "State & local governments",
      "is_public": true,
      "mortgage_musd": 111685.567,
      "consumer_credit_musd": 0.0,
      "nominal_musd": 111685.567,
      "real_musd": 164499.696,
      "share_of_scope": 0.0089268726,
      "share_display": "0.9%",
      "usd_display": "$0.11T",
      "series_ids": [
        "FL213065103"
      ]
    },
    {
      "risk_bucket": "banks_credit_unions",
      "label": "Banks & credit unions",
      "is_public": false,
      "mortgage_musd": 2705653.805,
      "consumer_credit_musd": 1415602.0,
      "nominal_musd": 4121255.805,
      "real_musd": 6070124.757,
      "share_of_scope": 0.3294062652,
      "share_display": "32.9%",
      "usd_display": "$4.12T",
      "series_ids": [
        "FL763065105",
        "FL753065103",
        "FL743065103",
        "FL473065100",
        "FL763066005",
        "FL473066000"
      ]
    },
    {
      "risk_bucket": "private_securitization",
      "label": "Private securitization & mortgage REITs",
      "is_public": false,
      "mortgage_musd": 1084700.939,
      "consumer_credit_musd": 46208.0,
      "nominal_musd": 1130908.939,
      "real_musd": 1665695.766,
      "share_of_scope": 0.0903919842,
      "share_display": "9.0%",
      "usd_display": "$1.13T",
      "series_ids": [
        "FL673065105",
        "FL643065173",
        "FL673066000"
      ]
    },
    {
      "risk_bucket": "nonbank_other",
      "label": "Finance companies & other private",
      "is_public": false,
      "mortgage_musd": 301212.821,
      "consumer_credit_musd": 799656.0,
      "nominal_musd": 1100868.821,
      "real_musd": 1621450.208,
      "share_of_scope": 0.0879909192,
      "share_display": "8.8%",
      "usd_display": "$1.10T",
      "series_ids": [
        "FL153065103",
        "FL103065105",
        "FL113065103",
        "FL543065105",
        "FL573065103",
        "FL223065143",
        "FL613065105",
        "FL613066005",
        "FL103066003",
        "FL113066003",
        "FL163066223"
      ]
    }
  ],
  "summary": {
    "quarter": "2011Q4",
    "scope_total_musd": 12511164.0,
    "scope_usd_display": "$12.51T",
    "public_musd": 6158130.435,
    "public_share": 0.4922108314622045,
    "public_share_display": "49.2%"
  }
}
```

## Claim lookup

`lookup_claim({"text_or_id": "public_share_2026q2"})`

```json
{
  "ok": true,
  "tool": "lookup_claim",
  "backend": "snapshot",
  "source": "z1",
  "vintage": {
    "source_vintage": "2026-09-11",
    "all": {
      "fred": "2026-10-27",
      "nyfed": "2026-10-27",
      "z1": "2026-09-11",
      "snapshot_generated_at": "2026-10-27T22:13:44+00:00",
      "source": "meta.json (database export)"
    }
  },
  "units": "as stated per claim",
  "series_ids": [
    "FL153165105",
    "FL153166000",
    "FL154104015",
    "FL213065103",
    "FL313065105",
    "FL313066220",
    "FL403065105",
    "FL403066005",
    "FL413065105"
  ],
  "caveats": [
    "Source is claims/register.csv (read from the repository, not the database).",
    "Only validation=PASS rows are verified. UNVERIFIED rows are registered but not yet checked; ESTIMATE rows are labelled estimates. Do not present non-PASS rows as fact.",
    "Vintage shown is each claim's own vintage."
  ],
  "data": [
    {
      "claim_id": "public_share_2026q2",
      "claim": "The public share of household mortgages and consumer credit was 56.4% in 2026Q2.",
      "display": "56.4%",
      "value": "0.5638",
      "unit": "share",
      "period": "2026Q2",
      "check_id": "C2",
      "series_ids": [
        "FL154104015",
        "FL153165105",
        "FL153166000",
        "FL313065105",
        "FL403065105",
        "FL413065105",
        "FL213065103",
        "FL313066220",
        "FL403066005"
      ],
      "vintage": "z1:2026-09-11",
      "validation": "PASS",
      "computation": "C2",
      "notes": "Atlas 'Today' step and the first 'What does this mean?' stat use the {share} token (latest quarter, fmtPct of public_share). web/app/page.tsx renders it from the mart snapshot with pct(.,1).",
      "quotable_as_verified": true
    }
  ]
}
```

## Refusal 1: auto loans held by banks (holder x type)

`check_answerable({"question": "How much of auto loans are held by banks?"})`

```json
{
  "ok": false,
  "refused": true,
  "tool": "check_answerable",
  "backend": "snapshot",
  "reason_code": "holder_by_type_not_available",
  "reason": "Z.1 reports consumer credit by holder OR by loan type, never both together, so the number cannot be read from the data.",
  "nearest_answerable": [
    {
      "tool": "holdings_by_bucket",
      "args": {},
      "gives": "consumer credit by holder (all types combined)"
    },
    {
      "tool": "collateral_coverage",
      "args": {},
      "gives": "consumer credit by type (all holders combined)"
    },
    {
      "tool": "nyfed_by_type",
      "args": {},
      "gives": "NY Fed balances/delinquency by type (not Z.1)"
    }
  ],
  "note": "No number was returned: the data cannot answer this question."
}
```

## Refusal 2: a forecast

`check_answerable({"question": "Forecast the public share for 2028"})`

```json
{
  "ok": false,
  "refused": true,
  "tool": "check_answerable",
  "backend": "snapshot",
  "reason_code": "forecast",
  "reason": "Forecasts and future values are not available; the server only reports published history.",
  "nearest_answerable": [
    {
      "tool": "public_share",
      "args": {
        "measure": "total"
      }
    },
    {
      "tool": "crisis_windows",
      "args": {}
    }
  ],
  "note": "No number was returned: the data cannot answer this question."
}
```

## Refusal 3: a quarter outside coverage (tool-level)

`public_share({"start": "2027Q1", "end": "2027Q4"})`

```json
{
  "ok": false,
  "refused": true,
  "tool": "public_share",
  "backend": "snapshot",
  "reason_code": "future_or_unpublished",
  "reason": "Latest quarter in the data is 2026Q2. Later quarters are future or unpublished values; this server reports published history only and does not forecast.",
  "nearest_answerable": [
    {
      "tool": "public_share",
      "args": {
        "start": "2026Q2",
        "end": "2026Q2"
      }
    }
  ],
  "note": "No number was returned: the data cannot answer this question."
}
```

## Refusal 4: state split

`check_answerable({"question": "Household debt by state"})`

```json
{
  "ok": false,
  "refused": true,
  "tool": "check_answerable",
  "backend": "snapshot",
  "reason_code": "geography",
  "reason": "The data is national. There are no state, county or regional splits.",
  "nearest_answerable": [
    {
      "tool": "public_share",
      "args": {
        "measure": "total"
      }
    }
  ],
  "note": "No number was returned: the data cannot answer this question."
}
```

## Refusal 5: borrower-level

`check_answerable({"question": "Which borrowers have the highest loan-level delinquency?"})`

```json
{
  "ok": false,
  "refused": true,
  "tool": "check_answerable",
  "backend": "snapshot",
  "reason_code": "loan_or_borrower_level",
  "reason": "The data is aggregate sector totals. There is no loan-level or borrower-level information.",
  "nearest_answerable": [
    {
      "tool": "holdings_by_bucket",
      "args": {}
    },
    {
      "tool": "nyfed_by_type",
      "args": {}
    }
  ],
  "note": "No number was returned: the data cannot answer this question."
}
```
