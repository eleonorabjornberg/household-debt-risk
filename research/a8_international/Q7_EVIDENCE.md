# Q7 evidence note: do losses at Germany's publicly owned banks count as "public"?

> **Claude draft, not the author's text.** Evidence gathered for Eleonora's decision on Q7 (`tracks/analysis.md`). The choice is hers: this note sets each option against the evidence and does not pick one.

**Decision (Eleonora, 2026-11-04, card q7-2): option (c), a third category "publicly owned, not guaranteed" on the risk-bearer measure.** Applied in `compare.py`, `comparison.csv`, `results.json` and the README; its scope was narrowed to public-law banks by the q7-promo-2 decision below.

Context: A8's holder measure counts savings banks (Sparkassen), Landesbanken and promotional banks as publicly owned lenders (30.3% of German bank lending to individuals, Q4 2025). The question is whether, on the headline risk-bearer measure, a credit loss at one of these banks is a *public* loss.

## What the primary sources say

Retrieved 2026-11-04, 16:45–16:50 UTC, by a source scout (Sonnet); every quote below was re-found by the main session in the downloaded file. Raw files are not committed.

| Point | Source | URL | SHA-256 | Quote |
|---|---|---|---|---|
| State guarantees ended | Deutsche Bundesbank, Monatsbericht März 2006, p. 37 and fn. 1 | https://www.bundesbank.de/resource/blob/692560/1ad96264319a5a9024bd27a9b6908cc0/mL/2006-03-regulatorische-rahmenbedingungen-data.pdf | `b1de47a73481c2e124c511a3c97e4378e3368fd650449b9a46ea6242e00aefa0` | "Wegfall der Gewährträgerhaftung und Anstaltslast für öffentlich-rechtliche Kreditinstitute zum Juli 2005"; fn.: "Gemäß der Entscheidung der EU-Kommission vom 27. März 2004, zweiter Teil, wird die Anstaltslast dergestalt ersetzt, dass sich die finanzielle Beziehung zwischen Träger und öffentlich-rechtlichem Kreditinstitut nicht von einer normalen, privatwirtschaftlich ausgestalteten Beziehung unterscheidet. Die Gewährträgerhaftung wird nach einer Übergangsregelung abgeschafft." (umlauts restored; the PDF's text layer drops them) |
| Same, dated decision | Deutsche Bundesbank, Monatsbericht April 2015 | https://www.bundesbank.de/resource/blob/693290/91473a261edec5eb902d2ad974543f96/mL/2015-04-bankensektor-data.pdf | `b1970ffe8df7b372561e28310b6575bda75434541d646ff0fbcc8b13f779dabf` | "die im Jahr 2001 beschlossene Abschaffung der Gewährträgerhaftung und der Anstaltslast … die nach mehrjähriger Übergangsfrist im Juli 2005 in Kraft trat" |
| Protection schemes protect institutions, funded by members | Deutsche Bundesbank, Monthly Report December 2015, "Deposit protection in Germany" | https://www.bundesbank.de/resource/blob/622750/1beb518a3dfc077b1c5efb6751b9ff6c/mL/2015-12-deposit-protection-data.pdf | `4ef54197b1b12f20d59b6411ca890f4d25d791571ea711eab4c9106909789fd7` | institutional protection schemes' "main function is institutional protection, ie averting the bankruptcy of a member institution"; "all statutory and voluntary deposit guarantee schemes in Germany are funded by members' regular annual ex ante contributions" |
| 2008–12 losses were absorbed by public owners and the federal fund | Deutsche Bundesbank, Monthly Report October 2012 | https://www.bundesbank.de/resource/blob/707352/457ae453b8c6d1d821bf737c6df5160f/mL/2012-10-development-data.pdf | `689a14b238987fa43deb37e01dc631db01a85a8f2dfefa3684b0fdf99b8cffa3` | "capital injections totalling €10 billion into BayernLB in 2008 and 2009"; Hamburg and Schleswig-Holstein created "a joint agency to finance a €3 billion capital injection into HSH Nordbank in 2009"; "WestLB was recapitalised (by €3 billion) by the central government special fund SoFFin rather than North Rhine-Westphalia" |
| Later losses settled under a state guarantee | Deutsche Bundesbank, Annual Report 2016 | https://www.bundesbank.de/resource/blob/667854/cc3827288ada4404334b3d23fd156470/mL/2016-annual-report-data.pdf | `8a18af84c36ed72aab0a4f9ae3eaa5ae589c6f0f45ffc5d24460d8beafc7690d` | HSH Nordbank's "loss of €2.6 billion is settled under the second loss guarantee provided by the state governments"; the bad bank is "a public sector special-purpose entity established by the federal states of Hamburg and Schleswig-Holstein" |
| Promotional bank ownership (KfW) | KfW, Corporate Governance Report | https://www.kfw.de/About-KfW/Reporting-Portal/Corporate-Governance-Report/ | `8e7b7a197031bd2cd60c757a65e5aa91c0f3cdc4fccf5f4a4dbf972bf6fc4dc4` | "The Federal Government owns 80% of KfW's share capital, the German federal states 20%." |

Earlier in A8 (`sources.md`): KfW's home-ownership programme sheet puts the liability for passed-through loans on the on-lending bank.

**Not found or not reachable (2026-11-04):** the text of the 17 July 2001 understanding and the exact grandfathering rules (European Commission and EUR-Lex hosts did not answer); the Commission's state-aid decisions for WestLB, HSH Nordbank and BayernLB; a primary statement of who owns Sparkassen and Landesbanken (DSGV and the state Sparkassen laws did not answer; the Bundesbank speech found mentions the Träger only in passing). No source was used from memory.

## The three options against the evidence

**(a) Count losses at publicly owned banks as public on the risk-bearer measure.**
- *For:* in 2008–12 the large Landesbank losses were in fact absorbed by public money: Länder capital injections (BayernLB, HSH) and the federal fund SoFFin (WestLB), and later HSH losses under a state guarantee. On the record, public owners bore the losses.
- *Against:* since July 2005 there is no legal guarantee; the relationship between owner and bank must be like a private one (Bundesbank 2006, citing the Commission's 2004 decision). Counting all their loans as public treats an ex-post choice to recapitalise as a standing guarantee.

**(b) Count them as private on the risk-bearer measure, and public only on the holder measure.**
- *For:* matches the post-2005 legal position: the bank's own capital, and then its protection scheme funded by member banks, take the first losses.
- *Against:* ignores what actually happened in 2008–12, when public owners and the federal fund paid; the losses did not stay inside the banks or the scheme.

**(c) A third category, "publicly owned, not guaranteed".**
- *For:* records both facts the sources establish, no legal guarantee since 2005 and public money in practice in 2008–12, without forcing them into one bucket.
- *Against:* the US has no direct counterpart, so the cross-country headline loses one-number comparability for Germany; the category's size would need its own row in A8's table.

## Follow-up: do promotional banks carry a state guarantee? (Eleonora, card q7-promo, option iii)

Retrieved 2026-11-04 17:34 UTC by the main session; details and the hosts that did not answer in `sources.md`.

- **KfW: yes, for KfW's own obligations.** KfW law, Article 1a (KfW's English version, `e32bf2c7…`): "The Federal Republic guarantees all obligations of KfW in respect of loans extended to and debt securities issued by KfW, fixed forward transactions or options entered into by KfW, and other credits extended to KfW …". This guarantees KfW's creditors and funding, not the households KfW lends to. A loss on a KfW loan is KfW's, and KfW's obligations are backed by the federal government. On this source, the "not guaranteed" label does not fit KfW, although no household borrower is guaranteed either. On KfW's on-lent programme loans, the on-lending bank takes the liability (KfW programme sheet 124/134, above).
- **Länder promotional banks: not established.** No statute or Commission text could be reached (gesetze-im-internet.de, EUR-Lex, the Commission, NRW.BANK, L-Bank and the Länder law portals did not answer), so whether they carry a state guarantee is unsourced here.
- **Size: not split.** The 1.1% is the Bundesbank category "banks with special, development and other central support tasks". No source here lists its members or gives KfW's share of its lending to individuals.

**Decision (Eleonora, 2026-11-04, card q7-promo-2): option (c).** The category "publicly owned, not guaranteed" holds the public-law banks only (savings banks and Landesbanken, 29.1% of bank lending to individuals). Promotional banks (1.1%) stay unclassified until the Länder promotional-bank statutes can be reached; KfW's Art. 1a guarantee is kept as context. Applied in `compare.py` (`public_owned_not_guaranteed`, `promotional_banks_unclassified`), `results.json` and the README. Reaching the statute hosts needs her separate approval.

## Follow-up 2: Länder promotional-bank statutes (2026-11-04, 20:38–20:45 UTC)

> **Claude draft.** Source summary for Eleonora's card; not her text. The 1.1% is **not** reclassified: it is still one Bundesbank category with no member list, and any change is her call.

Sources and hashes in `sources.md` ("Q7 follow-up 2" rows).

- **NRW.BANK: state backing of the bank, by statute.** NRW.BANK law § 4 (consolidated text as of 1 Jan 2024, the bank's own copy) and statute § 2 (11 March 2024): the Land NRW is *Gewährträger*; it "stellt sicher, dass die NRW.BANK ihre Aufgaben erfüllen kann (Anstaltslast)"; it is liable for NRW.BANK's obligations once the bank's own assets cannot satisfy them, and liable *directly* for the bank's borrowing, bonds, derivatives and "andere Kredite an die NRW.BANK". So NRW.BANK carries all three mechanisms the question named: Anstaltslast, Gewährträgerhaftung and an explicit guarantee of its refinancing. As with KfW, the guarantee runs to the bank and its creditors. Nothing in these texts guarantees the households NRW.BANK lends to; a loss on a household loan falls on NRW.BANK, which the Land must keep able to perform its tasks.
- **Landwirtschaftliche Rentenbank: same structure, federal.** § 1a "Haftung des Bundes", wording parallel to KfW § 1a. Whether Rentenbank sits in the Bundesbank category is not confirmed by any source on file (no member list).
- **KfW: German text of § 1a now on file**, agreeing with the English version already recorded.
- **L-Bank: not reached.** l-bank.de has product pages only and links its legal pages to l-bank.info (not allowed); landesrecht-bw.de's document service refused a plain request. Not worked around.
- **Verständigung II (2002): not reached.** EUR-Lex returns a JavaScript bot challenge to every request. Whether the 2002 understanding let promotional banks keep these guarantees is therefore not sourced here, although NRW.BANK's 2004 law shows that at least one does keep them today.

**What this does and does not settle.** For the three banks whose statutes are on file (KfW, Rentenbank, NRW.BANK), the label "not guaranteed" does not fit: each has a statutory state guarantee of its own obligations. None guarantees the borrower. The sources do not say who the category's other members are, how the 1.1% splits among them, or what L-Bank and the other Länder promotional banks' statutes say. So the evidence points one way for the members documented, but it covers an unknown share of the 1.1%.

**Options for Eleonora's card (no recommendation; the sources do not settle the whole category):**
1. Keep (c) as applied: the 1.1% stays unclassified; add NRW.BANK and Rentenbank to the KfW context note.
2. Label the 1.1% "publicly owned, state-backed institution (creditor guarantee, not borrower guarantee)", with a caveat that only three members' statutes were checked and no member list exists.
3. Keep it unclassified and ask for further access first (l-bank.info, EUR-Lex access without the bot challenge (her call, via the environment settings), a Bundesbank member list for the category) before deciding.

## What would make the choice firmer

- The Commission's 2001 understanding and 2004 decision texts (EUR-Lex), and the state-aid decisions for the three banks (Commission case pages), once those hosts answer.
- Whether any 2008–12 public support went to Sparkassen (as opposed to Landesbanken); none was found in the sources above.
