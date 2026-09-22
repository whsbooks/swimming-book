"""Points, Catmull–Rom spines, perpendiculars."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class V:
    x: float
    y: float

    def __add__(self, o: V) -> V:
        return V(self.x + o.x, self.y + o.y)

    def __sub__(self, o: V) -> V:
        return V(self.x - o.x, self.y - o.y)

    def __mul__(self, s: float) -> V:
        return V(self.x * s, self.y * s)

    __rmul__ = __mul__

    def dot(self, o: V) -> float:
        return self.x * o.x + self.y * o.y

    def len(self) -> float:
        return math.hypot(self.x, self.y)

    def unit(self) -> V:
        l = self.len()
        return V(1.0, 0.0) if l < 1e-9 else V(self.x / l, self.y / l)

    def rot90(self) -> V:
        return V(-self.y, self.x)

    def lerp(self, o: V, t: float) -> V:
        return self + (o - self) * t


def pts(*xy: float) -> list[V]:
    it = iter(xy)
    return [V(x, y) for x, y in zip(it, it)]


def _cr_segment(p0: V, p1: V, p2: V, p3: V, n: int) -> list[V]:
    out: list[V] = []
    for i in range(n):
        t = i / n
        t2, t3 = t * t, t * t * t
        out.append(
            p0 * (-0.5 * t3 + t2 - 0.5 * t)
            + p1 * (1.5 * t3 - 2.5 * t2 + 1)
            + p2 * (-1.5 * t3 + 2 * t2 + 0.5 * t)
            + p3 * (0.5 * t3 - 0.5 * t2)
        )
    return out


def catmull(points: list[V], n: int = 18) -> list[V]:
    if len(points) < 2:
        return list(points)
    if len(points) == 2:
        return [points[0].lerp(points[1], i / (n * 2)) for i in range(n * 2 + 1)]
    ext = [points[0] * 2 - points[1], *points, points[-1] * 2 - points[-2]]
    out: list[V] = []
    for i in range(1, len(ext) - 2):
        out.extend(_cr_segment(ext[i - 1], ext[i], ext[i + 1], ext[i + 2], n))
    out.append(points[-1])
    return out


def arclen(poly: list[V]) -> list[float]:
    s = [0.0]
    for a, b in zip(poly, poly[1:]):
        s.append(s[-1] + (b - a).len())
    return s


def tangent(poly: list[V], i: int) -> V:
    if i == 0:
        return (poly[1] - poly[0]).unit()
    if i == len(poly) - 1:
        return (poly[-1] - poly[-2]).unit()
    return (poly[i + 1] - poly[i - 1]).unit()


def wobble(poly: list[V], amp: float, freq: float, phase: float) -> list[V]:
    s = arclen(poly)
    total = s[-1] or 1.0
    out: list[V] = []
    for i, p in enumerate(poly):
        nrm = tangent(poly, i).rot90()
        k = amp * math.sin(phase + freq * 2 * math.pi * s[i] / total)
        # taper wobble at ends so letters still close
        edge = math.sin(math.pi * s[i] / total)
        out.append(p + nrm * (k * edge))
    return out
