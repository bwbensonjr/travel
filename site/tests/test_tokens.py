"""WCAG contrast checks for the design tokens in both themes."""
import re

import pytest

TEXT_TOKENS = ["--color-text", "--color-text-muted", "--color-accent", "--color-warn", "--color-ok"]
BACKGROUNDS = ["--color-bg", "--color-surface", "--color-surface-2"]


def parse_blocks(css):
    light_block = re.search(r":root\s*\{(.*?)\n\}", css, re.S).group(1)
    dark_block = re.search(r"prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{(.*?)\}", css, re.S).group(1)

    def vars_of(block):
        return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{6})", block))

    light = vars_of(light_block)
    dark = {**light, **vars_of(dark_block)}
    return {"light": light, "dark": dark}


def luminance(hex_color):
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


@pytest.fixture(scope="module")
def themes(site_dir):
    return parse_blocks((site_dir / "static" / "tokens.css").read_text())


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_text_meets_wcag_aa(themes, theme):
    t = themes[theme]
    failures = []
    for fg in TEXT_TOKENS:
        for bg in BACKGROUNDS:
            ratio = contrast(t[fg], t[bg])
            if ratio < 4.5:
                failures.append(f"{fg} on {bg}: {ratio:.2f}")
    assert failures == []


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_accent_button_text(themes, theme):
    t = themes[theme]
    assert contrast(t["--color-accent-text"], t["--color-accent"]) >= 4.5
