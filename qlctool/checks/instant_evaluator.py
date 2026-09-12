"""Cached instant evaluation for one immutable show graph."""

from dataclasses import dataclass

from .driven_channels import Driven, driven_channels
from .show_graph import ShowGraph, lit


@dataclass(frozen=True)
class _Instant:
    """One possible output for a channel and the colour running beside it."""

    coloured: bool
    written: bool
    value: int | None


class InstantEvaluator:
    """Evaluate and reuse graph states while one show graph stays immutable."""

    def __init__(self, graph: ShowGraph, groups: dict[int, tuple[int, ...]]) -> None:
        self._graph = graph
        self._groups = groups
        self._driven: dict[int, Driven] = {}
        self._states: dict[
            tuple[
                int,
                int,
                int,
                tuple[int, ...],
                frozenset[int],
                frozenset[int],
            ],
            frozenset[_Instant],
        ] = {}

    def states(
        self,
        function_ids: int | tuple[int, ...],
        fixture_id: int,
        offset: int,
        light_offsets: tuple[int, ...],
        stopped: frozenset[int],
    ) -> frozenset[_Instant]:
        """Every reachable HTP channel result for concurrent function roots."""
        roots = (function_ids,) if isinstance(function_ids, int) else function_ids
        states = frozenset((_Instant(False, False, 0),))
        for root_id in roots:
            states = _concurrent(
                states,
                self._node_states(
                    root_id,
                    fixture_id,
                    offset,
                    light_offsets,
                    stopped,
                    frozenset(),
                ),
            )
        return states

    def _node_states(
        self,
        function_id: int,
        fixture_id: int,
        offset: int,
        light_offsets: tuple[int, ...],
        stopped: frozenset[int],
        seen: frozenset[int],
    ) -> frozenset[_Instant]:
        """Possible channel results for one graph node and traversal frontier."""
        key = (function_id, fixture_id, offset, light_offsets, stopped, seen)
        cached = self._states.get(key)
        if cached is not None:
            return cached

        function = self._graph.functions.get(function_id)
        if function is None or function_id in seen or function_id in stopped:
            states = frozenset((_Instant(False, False, 0),))
        else:
            members = self._graph.members.get(function_id, ())
            if not members:
                written = self._driven_channels(function_id).get(fixture_id, {})
                states = frozenset(
                    (
                        _Instant(
                            coloured=any(
                                lit(written.get(light_offset, 0)) for light_offset in light_offsets
                            ),
                            written=offset in written,
                            value=written.get(offset, 0),
                        ),
                    )
                )
            else:
                nested_seen = seen | {function_id}
                parts = [
                    self._node_states(
                        member,
                        fixture_id,
                        offset,
                        light_offsets,
                        stopped,
                        nested_seen,
                    )
                    for member in members
                ]
                if function.attrib.get("Type") != "Collection":
                    states = frozenset().union(*parts)
                else:
                    states = frozenset((_Instant(False, False, 0),))
                    for part in parts:
                        states = _concurrent(states, part)

        self._states[key] = states
        return states

    def _driven_channels(self, function_id: int) -> Driven:
        cached = self._driven.get(function_id)
        if cached is not None:
            return cached
        function = self._graph.functions[function_id]
        driven = driven_channels(function, self._graph.capabilities, self._groups)
        self._driven[function_id] = driven
        return driven


def _concurrent(first: frozenset[_Instant], second: frozenset[_Instant]) -> frozenset[_Instant]:
    """Combine every simultaneous pair using QLC+'s HTP channel value."""
    return frozenset(_merge(left, right) for left in first for right in second)


def _merge(first: _Instant, second: _Instant) -> _Instant:
    if not first.written:
        value, written = second.value, second.written
    elif not second.written:
        value, written = first.value, first.written
    elif first.value is None or second.value is None:
        value, written = None, True
    else:
        value, written = max(first.value, second.value), True
    return _Instant(first.coloured or second.coloured, written, value)
