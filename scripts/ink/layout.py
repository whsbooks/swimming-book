"""Lay tentacle letters on a line or a swell."""

from __future__ import annotations

import hashlib
import math

import cairo

from .alphabet import glyph, map_stroke
from .geom import V
from .tentacle import INK, tentacle


def _seed(ch: str, i: int) -> float:
    h = hashlib.md5(f"{ch}:{i}".encode()).digest()
    return (h[0] / 255.0) * math.tau


def letter_width(ch: str, size: float, tracking: float) -> float:
    if ch == " ":
        return size * 0.38
    g = glyph(ch)
    if not g:
        return size * 0.2
    return size * g.width + size * tracking


def measure(text: str, size: float, tracking: float = 0.06) -> float:
    return sum(letter_width(ch, size, tracking) for ch in text)


def draw_letter(
    cr: cairo.Context,
    ch: str,
    origin: V,
    size: float,
    index: int,
    ink=INK,
    with_suckers: bool = True,
) -> None:
    g = glyph(ch)
    if not g:
        return
    phase0 = _seed(ch, index)
    cell_w, cell_h = size * g.width, size
    for k, st in enumerate(g.strokes):
        anchors = map_stroke(st, origin, cell_w, cell_h)
        tentacle(
            cr,
            anchors,
            root=st.root * size,
            tip=st.tip * size,
            amp=st.amp * size,
            freq=st.freq,
            phase=phase0 + k * 0.9,
            sucker_side=st.side,
            closed=st.closed,
            ink=ink,
            with_suckers=with_suckers,
        )


def draw_line(
    cr: cairo.Context,
    text: str,
    left: V,
    size: float,
    *,
    tracking: float = 0.06,
    ink=INK,
    wave: float = 0.0,
    wave_freq: float = 1.0,
    with_suckers: bool = True,
) -> float:
    x = 0.0
    total = measure(text, size, tracking) or 1.0
    for i, ch in enumerate(text):
        adv = letter_width(ch, size, tracking)
        y = left.y + wave * math.sin(wave_freq * math.pi * (x / total))
        if glyph(ch):
            draw_letter(cr, ch, V(left.x + x, y), size, i, ink=ink, with_suckers=with_suckers)
        x += adv
    return x


def wrap_lines(text: str, size: float, max_w: float, tracking: float = 0.06) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if measure(trial, size, tracking) > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(
    cr: cairo.Context,
    text: str,
    box_left: float,
    box_top: float,
    max_w: float,
    size: float,
    *,
    tracking: float = 0.06,
    leading: float = 1.28,
    ink=INK,
    wave: float = 0.0,
    center: bool = True,
) -> None:
    lines = wrap_lines(text, size, max_w, tracking)
    y = box_top
    for line in lines:
        w = measure(line, size, tracking)
        x = box_left + ((max_w - w) * 0.5 if center else 0.0)
        draw_line(cr, line, V(x, y), size, tracking=tracking, ink=ink, wave=wave, wave_freq=1.4)
        y += size * leading
