"""Tapered tentacle ribbons: octopus-leg strokes."""

from __future__ import annotations

import math

import cairo

from .geom import V, arclen, catmull, tangent, wobble

INK = (0x0A / 255, 0x3D / 255, 0x62 / 255)
INK_SOFT = (0x1B / 255, 0x55 / 255, 0x7A / 255)
SUCKER = (0xC4 / 255, 0x8A / 255, 0x6A / 255)
SUCKER_RIM = (0x8A / 255, 0x4E / 255, 0x3A / 255)


def _width(t: float, root: float, tip: float) -> float:
    u = max(0.0, min(1.0, t))
    return tip + (root - tip) * (1.0 - u) ** 1.55


def ribbon_poly(spine: list[V], root: float, tip: float) -> list[V]:
    s = arclen(spine)
    total = s[-1] or 1.0
    left: list[V] = []
    right: list[V] = []
    last = len(spine) - 1
    for i, p in enumerate(spine):
        t = s[i] / total
        w = _width(t, root, tip)
        n = tangent(spine, i).rot90()
        if i == last:
            left.append(p)
            right.append(p)
        else:
            left.append(p + n * (w * 0.5))
            right.append(p - n * (w * 0.5))
    return left + list(reversed(right[1:-1]))


def fill_poly(cr: cairo.Context, poly: list[V], rgb: tuple[float, float, float]) -> None:
    if len(poly) < 3:
        return
    cr.new_path()
    cr.move_to(poly[0].x, poly[0].y)
    for p in poly[1:]:
        cr.line_to(p.x, p.y)
    cr.close_path()
    cr.set_source_rgb(*rgb)
    cr.fill()


def suckers(cr: cairo.Context, spine: list[V], root: float, tip: float, side: int, every: float) -> None:
    if side == 0:
        return
    s = arclen(spine)
    total = s[-1] or 1.0
    if total < every * 1.5:
        return
    acc = every * 0.7
    for i, p in enumerate(spine[:-4]):
        if s[i] < acc:
            continue
        acc = s[i] + every
        t = s[i] / total
        if t < 0.08 or t > 0.88:
            continue
        w = _width(t, root, tip)
        n = tangent(spine, i).rot90() * side
        c = p + n * (w * 0.18)
        r = max(2.2, w * 0.28)
        cr.set_source_rgb(*SUCKER)
        cr.arc(c.x, c.y, r, 0, math.tau)
        cr.fill()
        cr.set_source_rgb(*SUCKER_RIM)
        cr.set_line_width(max(0.8, r * 0.18))
        cr.arc(c.x, c.y, r * 0.55, 0, math.tau)
        cr.stroke()


def tentacle(
    cr: cairo.Context,
    anchors: list[V],
    *,
    root: float,
    tip: float,
    amp: float = 0.0,
    freq: float = 1.6,
    phase: float = 0.0,
    sucker_side: int = 1,
    closed: bool = False,
    ink: tuple[float, float, float] = INK,
    with_suckers: bool = True,
) -> None:
    if closed and len(anchors) >= 3:
        loop = anchors + [anchors[0], anchors[1]]
        spine = catmull(loop, n=16)[:-16]
        mid = (root + tip) * 0.5
        spine = wobble(spine, amp * 0.4, freq, phase) if amp else spine
        s = arclen(spine)
        total = s[-1] or 1.0
        left: list[V] = []
        right: list[V] = []
        for i, p in enumerate(spine):
            w = mid * (0.85 + 0.15 * math.sin(phase + 4 * math.pi * s[i] / total))
            n = tangent(spine, i).rot90()
            left.append(p + n * (w * 0.5))
            right.append(p - n * (w * 0.5))
        fill_poly(cr, left + list(reversed(right)), ink)
        if with_suckers:
            suckers(cr, spine, mid, mid * 0.7, sucker_side, every=mid * 1.8)
        return

    spine = catmull(anchors, n=20)
    if amp:
        spine = wobble(spine, amp, freq, phase)
    fill_poly(cr, ribbon_poly(spine, root, tip), ink)
    cr.set_source_rgb(*ink)
    cr.arc(spine[0].x, spine[0].y, root * 0.48, 0, math.tau)
    cr.fill()
    if with_suckers:
        suckers(cr, spine, root, tip, sucker_side, every=max(14.0, root * 1.35))
