# Track register files

Each parallel track (see PLAN.md "Parallel tracks") adds its register rows to `claims/tracks/<track>.csv`, with the same header as `claims/register.csv`. `check_register.py` reads these files together with the main register, so a track's write-ups pass the pre-commit check without editing the shared register. When the coordinator merges a track, it moves the rows into `register.csv` and deletes the track file.
