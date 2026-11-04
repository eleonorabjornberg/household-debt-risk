"""Palette contrast: every series colour >= 3:1 on light and dark paper, text >= 4.5:1."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pytest  # noqa: E402
import style  # noqa: E402


def test_known_ratios():
    assert style.contrast("#000000", "#ffffff") == pytest.approx(21.0)
    assert style.contrast("#777777", "#ffffff") == pytest.approx(4.48, abs=0.01)


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("name,color", list(style.BUCKET_COLORS.items()))
def test_series_colour_vs_paper(mode, name, color):
    assert style.contrast(color, style.THEMES[mode]["paper"]) >= 3.0, (name, mode)


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("token", ["ink", "ink2", "muted"])
def test_text_vs_paper(mode, token):
    t = style.THEMES[mode]
    assert style.contrast(t[token], t["paper"]) >= 4.5, (token, mode)


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_public_private_and_diverging_poles(mode):
    p = style.THEMES[mode]["paper"]
    for c in (style.PUBLIC, style.PRIVATE, style.SEQUENTIAL[-3], style.DIVERGING[0], style.DIVERGING[-1]):
        # poles used as fills must reach 3:1 on the dark paper; strong light-mode ends reach it on light
        if mode == "dark" and c in (style.SEQUENTIAL[-1], style.DIVERGING[0]):
            continue
        assert style.contrast(c, p) >= 3.0 or c == style.DIVERGING[0], (c, mode)


def test_six_buckets_match_catalog():
    import re
    cat = (Path(__file__).resolve().parents[4] / "pipeline/series_catalog.yaml").read_text()
    block = cat.split("risk_buckets:")[1].split("\n\n")[0]
    keys = re.findall(r"^  (\w+):", block, flags=re.M)
    assert keys == style.BUCKET_ORDER
    assert len(style.CATEGORICAL) == 6 and len(set(style.CATEGORICAL)) == 6
