#!/usr/bin/env python3
"""A5 figures: DFA borrower shares over time (chart-from-sql skill) and state tile maps (NY Fed state data).

    uv run --project pipeline --with matplotlib python research/a5_distribution/figures.py

Run distribution.py first (it downloads the inputs into data/a5/ and writes state_2025.csv).
The tile map is a grid with one equal square per state (no shapefile needed); colours are the project's
sequential ramp from .claude/skills/chart-from-sql/scripts/style.py. Values come straight from state_2025.csv.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "chart-from-sql" / "scripts"))
sys.path.insert(0, str(HERE))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap  # noqa: E402

import style  # noqa: E402
from chart import make_chart  # noqa: E402
from distribution import DATA, read_dfa  # noqa: E402

FIG = HERE / "figures"
DFA_VINTAGE = "DFA 2026-09-15 (through 2026Q2)"
STATE_VINTAGE = "NY Fed state statistics, Feb 2026 (Q4 2025)"

# Standard US tile-grid layout (row, col).
TILES = {
    "AK": (0, 0), "ME": (0, 11), "VT": (1, 10), "NH": (1, 11), "WA": (2, 1), "ID": (2, 2), "MT": (2, 3), "ND": (2, 4),
    "MN": (2, 5), "IL": (2, 6), "WI": (2, 7), "MI": (2, 8), "NY": (2, 9), "RI": (2, 10), "MA": (2, 11),
    "OR": (3, 1), "NV": (3, 2), "WY": (3, 3), "SD": (3, 4), "IA": (3, 5), "IN": (3, 6), "OH": (3, 7), "PA": (3, 8),
    "NJ": (3, 9), "CT": (3, 10), "CA": (4, 1), "UT": (4, 2), "CO": (4, 3), "NE": (4, 4), "MO": (4, 5), "KY": (4, 6),
    "WV": (4, 7), "VA": (4, 8), "MD": (4, 9), "DE": (4, 10), "AZ": (5, 2), "NM": (5, 3), "KS": (5, 4), "AR": (5, 5),
    "TN": (5, 6), "NC": (5, 7), "SC": (5, 8), "DC": (5, 9), "OK": (6, 4), "LA": (6, 5), "MS": (6, 6), "AL": (6, 7),
    "GA": (6, 8), "HI": (7, 0), "TX": (7, 4), "FL": (7, 8),
}


def dfa_series(stem: str, col: str) -> pd.DataFrame:
    d = read_dfa(DATA / "dfa.zip", f"dfa-{stem}-shares.csv")
    w = d.pivot(index="Date", columns="Category", values=col)
    w.index = [s.replace(":", "") for s in w.index]
    return w.reset_index(names="quarter")


def tile_map(values: pd.Series, title: str, unit_label: str, out: Path, fmt) -> dict:
    assert set(values.index) == set(TILES), "tile layout and data disagree on states"
    th = style.theme("light")
    with plt.rc_context(style.rc_params("light")):
        fig, ax = plt.subplots(figsize=(8, 5.4))
        qs = values.quantile([0, 1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6, 1]).to_numpy(copy=True)
        qs[-1] += 1e-9
        cmap, norm = ListedColormap(style.SEQUENTIAL), BoundaryNorm(qs, len(style.SEQUENTIAL))
        for st, (r, c) in TILES.items():
            v = values[st]
            col = cmap(norm(v))
            ax.add_patch(plt.Rectangle((c, -r), 0.92, 0.92, color=col))
            dark = norm(v) >= 3
            ax.text(c + 0.46, -r + 0.58, st, ha="center", va="center", fontsize=8, fontweight="bold",
                    color="#ffffff" if dark else th["ink"])
            ax.text(c + 0.46, -r + 0.28, fmt(v), ha="center", va="center", fontsize=6.5,
                    color="#ffffff" if dark else th["ink"])
        ax.set_xlim(-0.2, 12.2)
        ax.set_ylim(-7.3, 1.2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, loc="left", fontsize=12, color=th["ink"])
        labels = [f"{fmt(qs[i])}–{fmt(qs[i + 1])}".replace("$", r"\$") for i in range(6)]
        handles = [plt.Rectangle((0, 0), 1, 1, color=style.SEQUENTIAL[i]) for i in range(6)]
        ax.legend(handles, labels, title=f"{unit_label} (sextiles)", loc="lower left", bbox_to_anchor=(0.0, -0.08),
                  ncol=3, frameon=False, fontsize=7, title_fontsize=7.5)
        fig.text(0.01, 0.01, f"Source: FRBNY Consumer Credit Panel / Equifax, State Level Household Debt Statistics "
                 f"({STATE_VINTAGE}). 50 states + DC. {style.SOURCE_SUFFIX}", fontsize=6.5, color=th["muted"])
        out.parent.mkdir(parents=True, exist_ok=True)
        for ext in ("png", "svg"):
            fig.savefig(out.with_suffix(f".{ext}"), dpi=200, bbox_inches="tight", facecolor=th["paper"])
        plt.close(fig)
    hi, lo = values.idxmax(), values.idxmin()
    alt = (f"{title}. Tile map of the 50 states and DC, one square per state, shaded in six quantile bands. "
           f"Highest: {hi} ({fmt(values[hi])}); lowest: {lo} ({fmt(values[lo])}); median {fmt(values.median())}.")
    out.with_suffix(".alt.txt").write_text(alt + "\n")
    side = {"title": title, "source_line": f"FRBNY CCP/Equifax ({STATE_VINTAGE})", "vintage": STATE_VINTAGE,
            "data_source": {"file": "research/a5_distribution/state_2025.csv", "column": values.name},
            "rows": int(len(values)), "unit": unit_label, "alt": alt}
    out.with_suffix(".json").write_text(json.dumps(side, indent=1) + "\n")
    return side


def main() -> int:
    FIG.mkdir(exist_ok=True)
    mort = dfa_series("networth", "Home mortgages")
    labels = {"TopPt1": "Top 0.1%", "RemainingTop1": "Next 0.9%", "Next9": "Next 9%", "Next40": "Next 40%", "Bottom50": "Bottom 50%"}
    make_chart(mort, kind="area", x="quarter", y=list(labels), labels=labels, ylabel="Percent of all home mortgages (%)",
               unit="%", title="Who owes the mortgages: share of home mortgage debt by wealth group",
               source="Fed Distributional Financial Accounts, dfa-networth-shares.csv", vintage=DFA_VINTAGE,
               out=FIG / "dfa_mortgage_share_by_wealth", data_source={"file": "data/a5/dfa.zip:dfa-networth-shares.csv"})
    b50 = pd.DataFrame({"quarter": mort["quarter"],
                        "mortgages": mort["Bottom50"],
                        "consumer_credit": dfa_series("networth", "Consumer credit")["Bottom50"],
                        "net_worth": dfa_series("networth", "Net worth")["Bottom50"]})
    make_chart(b50, kind="line", x="quarter", y=["mortgages", "consumer_credit", "net_worth"],
               labels={"mortgages": "Home mortgages", "consumer_credit": "Consumer credit", "net_worth": "Net worth"},
               ylabel="Bottom 50% by wealth: percent of aggregate (%)", unit="%", recessions=True,
               title="The bottom half by wealth owes half the consumer credit and a fifth of mortgages",
               source="Fed Distributional Financial Accounts, dfa-networth-shares.csv", vintage=DFA_VINTAGE,
               out=FIG / "dfa_bottom50_shares", data_source={"file": "data/a5/dfa.zip:dfa-networth-shares.csv"})
    st = pd.read_csv(HERE / "state_2025.csv", index_col=0)
    usd = lambda v: f"${v / 1000:,.1f}k"  # noqa: E731
    tile_map(st["mortgage_pc_2025"], "Mortgage debt per person with a credit file, Q4 2025", "USD", FIG / "state_mortgage_pc_2025", usd)
    tile_map(st["studentloan_pc_2025"], "Student loan debt per person with a credit file, Q4 2025", "USD",
             FIG / "state_studentloan_pc_2025", usd)
    tile_map(st["mortgage_delinq_2025"], "Mortgage balances 90+ days delinquent, Q4 2025", "% of balance",
             FIG / "state_mortgage_delinq_2025", lambda v: f"{v:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
