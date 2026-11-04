# Sources: licence terms (F4)

Retrieved 2026-11-04 ~01:07 UTC from the cloud sandbox with curl. Raw HTML kept outside git (scratchpad).

| What | URL | Bytes | SHA-256 |
|---|---|---|---|
| Fed Board website policies | https://www.federalreserve.gov/disclaimer.htm | 85306 | 08f979fe2219c1372c9a57d5521deb0c7e5983b1b5c11c7f3a39c0f94f03e39f |
| FRED legal / terms | https://fred.stlouisfed.org/legal/ | 132259 | 6e3e5a91f4b3d01c61bdd60a01172877570c46755c13286d4266a95440675f6a |
| NY Fed Terms of Use (last updated 6/9/2023) | https://www.newyorkfed.org/privacy/termsofuse.html | 143906 | f90d7835c92c9a0c771f6c799a9bc266c00bef73fdc5f802faf359c5d7088128 |
| NY Fed HHDC landing page | https://www.newyorkfed.org/microeconomics/hhdc | 104722 | 6c55eb9a7f40e0329a43a18a2e4eb677f1f2fc744a61f6a567d430662f70196b |

## Quoted passages

**Fed Board:** "Unless otherwise indicated, information on Board's website is in the public domain and may be
copied and distributed without permission. Please cite to the Board as the source of the information."

**FRED:** "Public Domain: Citation requested. These series may be under copyright or in the public domain and
may be used without permission, provided you do not engage in any prohibited use. When using, please cite
the data source and acknowledge that you obtained the data from FRED (example, "Source: BLS via FRED")."
And: "Series with a copyright notice are owned by third parties and have special restrictions. Before using
data with a copyright notice for anything other than your own personal use, you must contact the data owner
to obtain permission."

**NY Fed:** "In general, the New York Fed intends for Website visitors to have permission to use and share
Content. Some conditions apply to all Content." ... "If you distribute the Content, you must make the Content
available with the same permissions, conditions, and restrictions set forth in these Terms. You may not impose
more restrictive terms or conditions on the Content." ... "Otherwise, follow this format: "© [year] Federal
Reserve Bank of New York. Content from the New York Fed subject to the Terms of Use at newyorkfed.org.""

Checked later the same day in the HHDC workbook itself (section below). The HHDC web page loads its
content with JavaScript, so the fetched HTML does not show page-level notices.

## HHDC use-restriction check (decision F4-1, 2026-11-04 ~04:30 UTC)

`data/nyfed/HHD_C_Report_2026Q2.xlsx` (the file the pipeline downloads; 962,992 bytes, SHA-256
ddfba16b87e187848ed591a1283f310188e7bdeebe5cf409b70a35b058d99237; 73 sheets) was scanned cell by cell with
openpyxl for copyright, terms, permission, restriction, licence, reproduction and redistribution wording.
Result: no use restriction beyond the general Terms of Use. The only notice is the source identifier on the
data sheets, "Source: New York Fed Consumer Credit Panel/Equifax", which the terms require us to keep
("you must include any copyright notice and other source identifiers that the New York Fed includes with
that Content"). The downloads carry it next to the attribution line.
