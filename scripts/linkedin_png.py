#!/usr/bin/env python3
"""Two LinkedIn 1080×1080 plates: tentacle letters for verse 1 (Float)."""

from __future__ import annotations

import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ink.geom import V, pts
from ink.layout import draw_line, draw_wrapped, measure
from ink.plate import INK_SOFT, footer, wash
from ink.tentacle import INK, tentacle

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
W = H = 1080


def surface() -> tuple[cairo.ImageSurface, cairo.Context]:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cr = cairo.Context(surf)
    wash(cr)
    return surf, cr


def stray_legs(cr: cairo.Context, legs: list[tuple]) -> None:
    for anchors, root, tip, phase, side in legs:
        tentacle(
            cr,
            anchors,
            root=root,
            tip=tip,
            amp=root * 0.22,
            freq=1.5,
            phase=phase,
            sucker_side=side,
            ink=INK_SOFT,
        )


def verse_card(path: Path) -> None:
    surf, cr = surface()
    # extra arms that do not belong to letters — the page is a creature
    stray_legs(
        cr,
        [
            (pts(80, 80, 160, 240, 90, 420, 180, 620), 28, 5, 0.3, 1),
            (pts(1000, 60, 920, 220, 1040, 400, 910, 580), 26, 5, 1.7, -1),
            (pts(40, 900, 200, 980, 360, 900, 500, 1020), 20, 4, 2.4, 1),
            (pts(1040, 940, 880, 1010, 720, 930), 18, 4, 0.8, -1),
        ],
    )

    title = "FLOAT"
    size = 168
    tw = measure(title, size, tracking=0.02)
    draw_line(cr, title, V((W - tw) / 2, 210), size, tracking=0.02, ink=INK, wave=18, wave_freq=1.6)

    verse = "To swim first is to float."
    vs = 58
    draw_wrapped(cr, verse, 70, 520, 940, vs, tracking=0.05, leading=1.35, wave=14, ink=INK)

    footer(cr)
    surf.write_to_png(str(path))


def note_card(path: Path) -> None:
    surf, cr = surface()
    # one long arm: a C-curl that holds the note the way water holds a body
    tentacle(
        cr,
        pts(
            980, 70,
            720, 40,
            220, 90,
            70, 280,
            90, 560,
            180, 820,
            460, 980,
            820, 940,
            1020, 780,
        ),
        root=42,
        tip=7,
        amp=14,
        freq=1.15,
        phase=0.6,
        sucker_side=1,
        ink=INK_SOFT,
    )
    # a quieter second arm, just a tip in the corner
    tentacle(
        cr,
        pts(1040, 420, 980, 560, 1040, 700),
        root=16,
        tip=4,
        amp=6,
        freq=1.4,
        phase=2.1,
        sucker_side=-1,
        ink=INK_SOFT,
    )

    label = "FLOAT"
    ls = 36
    lw = measure(label, ls, tracking=0.14)
    draw_line(
        cr,
        label,
        V((W - lw) / 2, 168),
        ls,
        tracking=0.14,
        ink=INK,
        wave=4,
        with_suckers=False,
    )

    lines = ("The water is", "there to help", "you to swim.")
    ns = 72
    y = 310
    for i, line in enumerate(lines):
        tw = measure(line, ns, tracking=0.04)
        draw_line(
            cr,
            line,
            V((W - tw) / 2, y),
            ns,
            tracking=0.04,
            ink=INK,
            wave=10,
            wave_freq=1.2 + i * 0.15,
        )
        y += ns * 1.42

    footer(cr)
    surf.write_to_png(str(path))


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    a = DOCS / "linkedin-ch1-float.png"
    b = DOCS / "linkedin-ch1-float-note.png"
    verse_card(a)
    note_card(b)
    print(a)
    print(b)


if __name__ == "__main__":
    main()
