"""Project chart style: one palette, validated for contrast, light and dark.

Colours are the sites' own (web/app/globals.css --s1..--s6, ink, paper), with two light-mode
steps darkened (amber, green-teal kept) so that every series colour reaches >= 3:1 against BOTH the
light paper (#f7f8f9) and the dark paper (#101215); body text reaches >= 4.5:1. The test suite
(tests/test_style.py) recomputes these ratios; do not edit a colour without re-running it.
"""
from __future__ import annotations

THEMES = {
    "light": {
        "paper": "#f7f8f9", "ink": "#111418", "ink2": "#474e57", "muted": "#5b626c",
        "grid": "#e3e6ea", "axis": "#b9bfc7", "band": "#111418", "band_alpha": 0.07,
    },
    "dark": {
        "paper": "#101215", "ink": "#eceef1", "ink2": "#b6bcc4", "muted": "#8b929b",
        "grid": "#22262b", "axis": "#3a4048", "band": "#ffffff", "band_alpha": 0.09,
    },
}

# Six holder buckets, fixed order and fixed colour per entity (pipeline/series_catalog.yaml risk_buckets).
BUCKET_ORDER = ["federal_direct", "gse_agency", "state_local",
                "banks_credit_unions", "private_securitization", "nonbank_other"]
BUCKET_LABELS = {
    "federal_direct": "Federal government (direct)",
    "gse_agency": "GSEs & agency pools",
    "state_local": "State & local governments",
    "banks_credit_unions": "Banks & credit unions",
    "private_securitization": "Private securitization & mortgage REITs",
    "nonbank_other": "Finance companies & other private",
}
# Series colours work on both backgrounds (>= 3:1 each); order is the categorical order.
CATEGORICAL = ["#2a78d6", "#d95926", "#199e70", "#b07800", "#d55181", "#008300"]
BUCKET_COLORS = dict(zip(BUCKET_ORDER, CATEGORICAL))

# Sequential: one hue (blue), light to dark. Diverging: blue (negative pole) / orange (positive pole)
# around a neutral grey midpoint. Both are for fills; ends are checked in tests against 3:1 only for
# the strong end (light end is intentionally pale).
SEQUENTIAL = ["#dbe8f8", "#a9c9f0", "#6da7ec", "#2a78d6", "#1c5cab", "#143f78"]
DIVERGING = ["#1c5cab", "#6da7ec", "#cfd3d8", "#f0a27d", "#d95926"]

PUBLIC = "#2a78d6"     # public-sector blue (site accent)
PRIVATE = "#d95926"    # private-side orange
CRISIS_LABEL = "NBER recession"
SOURCE_SUFFIX = "chart: household-debt-risk"


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    ch = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255
        ch.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast(a: str, b: str) -> float:
    """WCAG 2.x contrast ratio between two #rrggbb colours."""
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def theme(mode: str = "light") -> dict:
    if mode not in THEMES:
        raise ValueError(f"mode must be 'light' or 'dark', got {mode!r}")
    return THEMES[mode]


def rc_params(mode: str = "light") -> dict:
    t = theme(mode)
    return {
        "figure.facecolor": t["paper"], "axes.facecolor": t["paper"], "savefig.facecolor": t["paper"],
        "axes.edgecolor": t["axis"], "axes.labelcolor": t["ink2"], "axes.titlecolor": t["ink"],
        "text.color": t["ink"], "xtick.color": t["muted"], "ytick.color": t["muted"],
        "axes.grid": True, "grid.color": t["grid"], "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.axisbelow": True, "axes.prop_cycle": __import__("cycler").cycler(color=CATEGORICAL),
        "font.family": "sans-serif",
        "font.sans-serif": ["Public Sans", "DejaVu Sans"],
        "font.size": 10, "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9,
        "lines.linewidth": 2.0, "lines.solid_capstyle": "round",
        "legend.frameon": False, "legend.fontsize": 9, "legend.labelcolor": t["ink2"],
        "svg.fonttype": "none",
    }
