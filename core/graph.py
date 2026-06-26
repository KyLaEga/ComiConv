"""Conversion-graph resolution (spec PC-4).

Given a source Intermediate kind and a target encoder, find a path to a kind the
encoder accepts: either direct (kinds match) or chained through registered
adapters (e.g. Document -> ImageSet via the PDF renderer). BFS yields the
shortest chain; no path raises a clear, typed error.

Adapters are registered as ``(from_kind, to_kind) -> callable(intermediate,
cancel_check) -> intermediate`` so cross-intermediate conversions (PDF<->images)
are ordinary graph edges, which is what makes image->PDF and split-PDF fall out
for free.
"""
from __future__ import annotations

from collections import deque
from typing import Callable, Dict, List, Tuple

from .intermediates import Intermediate, Kind

_adapters: Dict[Tuple[Kind, Kind], Callable] = {}


class NoConversionPath(Exception):
    pass


def register_adapter(from_kind: Kind, to_kind: Kind, fn: Callable) -> Callable:
    _adapters[(from_kind, to_kind)] = fn
    return fn


def _find_path(start: Kind, goal: Kind) -> List[Kind]:
    if start == goal:
        return [start]
    seen = {start}
    queue = deque([[start]])
    while queue:
        path = queue.popleft()
        last = path[-1]
        for (frm, to) in _adapters:
            if frm == last and to not in seen:
                new_path = path + [to]
                if to == goal:
                    return new_path
                seen.add(to)
                queue.append(new_path)
    raise NoConversionPath(f"No conversion path from {start.value} to {goal.value}")


def adapt(intermediate: Intermediate, target_kind: Kind, cancel_check=None) -> Intermediate:
    """Convert ``intermediate`` so its kind becomes ``target_kind``."""
    path = _find_path(intermediate.kind, target_kind)
    current = intermediate
    for nxt in path[1:]:
        current = _adapters[(current.kind, nxt)](current, cancel_check)
    return current


def reset():
    """Test helper."""
    _adapters.clear()
