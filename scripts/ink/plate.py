"""Cream wash and stray current-legs behind the letters."""

from __future__ import annotations

import cairo

from .geom import pts
from .tentacle import tentacle

CREAM = (0xFF / 255, 0xF9 / 255, 0xEF / 255)
TAUPE = (0x6A / 255, 0x5C / 255, 0x4E / 255)
FOAM = (0xE4 / 255, 0xEB / 255, 0xF0 / 255)
INK_SOFT = (0x1B / 255, 0x55 / 255, 0x7A / 255)


def wash(cr: cairo.Context) -> None:
    cr.set_source_rgb(*CREAM)
    cr.paint()
    currents = [
        pts(40, 220, 280, 160, 520, 240, 780, 140, 1060, 210),
        pts(-20, 480, 240, 560, 500, 430, 760, 540, 1100, 470),
        pts(20, 820, 300, 760, 560, 880, 840, 790, 1100, 860),
        pts(80, 40, 400, 80, 700, 20, 1000, 90),
        pts(200, 1000, 480, 940, 720, 1010, 980, 930),
    ]
    for i, a in enumerate(currents):
        tentacle(
            cr,
            a,
            root=22 - i * 2,
            tip=5,
            amp=12,
            freq=1.3 + i * 0.18,
            phase=i * 1.1,
            sucker_side=1 if i % 2 else -1,
            ink=FOAM,
            with_suckers=False,
        )


def footer(cr: cairo.Context, w: int = 1080) -> None:
    cr.select_font_face("Noto Serif CJK KR", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(18)
    cr.set_source_rgb(*TAUPE)
    t = "© 수영 책방 Swimming Bookstore"
    xb, _yb, tw, _th, _xa, _ya = cr.text_extents(t)
    cr.move_to((w - tw) / 2 - xb, 1048)
    cr.show_text(t)
