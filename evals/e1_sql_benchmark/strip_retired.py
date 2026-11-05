"""Rewrite the `retired:` list of questions.yaml without checks (freeze step). Usage: strip_retired.py IN OUT"""
import json, sys, yaml
src, dst = sys.argv[1], sys.argv[2]
text = open(src).read()
head, _ = text.split("\nretired:\n")
keep = ("id", "replaced_by", "retired_on", "family", "difficulty", "question")
lines = []
for r in yaml.safe_load(text)["retired"]:
    lines.append("- {" + ", ".join(f"{k}: {json.dumps(r[k]) if k in ('question', 'retired_on') else r[k]}" for k in keep) + "}")
open(dst, "w").write(head + "\nretired:\n" + "\n".join(lines) + "\n")
