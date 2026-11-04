# Trigger examples for `z1-release-update`

## Should trigger

| Prompt | Why |
|---|---|
| "The Fed put out the December Z.1, run the update." | Names a new Z.1 release and asks for the update. |
| "Refresh the data for the new Financial Accounts release." | "Financial Accounts of the United States" is the Z.1. |
| "Is there a new Z.1 yet? If so, pull it in and tell me what moved." | Detect step first, then the full flow; stops at "nothing new" if there is none. |
| "z1 came out today, can you run extract, transform and validation against last quarter's file?" | Spells out the skill's steps with a previous vintage. |
| "Do the quarterly Z.1 refresh and tell me which numbers on the site are now out of date." | Needs the what-moved note and the stale-claims scan. |
| "Prepare the commit for the March 2027 Z.1 data, but don't load the database." | Matches step 7: draft the commit, hold the load. |
| "New Fed flow of funds data is out; update public share and give me a release note." | "Flow of funds" is the older name; the output is the what-moved note. |

## Should NOT trigger

| Prompt | Why |
|---|---|
| "Update the NY Fed numbers." | HHDC refresh: different source, no Z.1 gate. |
| "Pull the latest FRED series (unemployment, house prices)." | FRED-only refresh. |
| "What was the public share in 1990?" | A data question; answer from the snapshot or `mart.public_share`. |
| "Why did the validation check E8 warn on 2003Q4?" | Investigating an existing report, no new release. |
| "Add a new series to the catalog and make the transform handle it." | Code change to the pipeline. |
| "Load the already-approved data into Supabase." | A single load command, not a release run. |
| "Fix the failing identity check A3 in validation/run.py." | Code change to the validation suite. |
| "Make the hero chart on the web page show 2026Q2." | Front-end work; the data is already in. |
