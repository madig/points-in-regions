from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Union

from hypothesis import assume, given
from hypothesis import strategies as st


@dataclass
class Range:
    __slots__ = "start", "end"

    start: float
    end: float

    def __contains__(self, value: float) -> bool:
        return self.start <= value <= self.end


@dataclass
class Stops:
    __slots__ = "stops"

    stops: set[float]

    def __contains__(self, value: float) -> bool:
        return value in self.stops


Location = Mapping[str, float]
Region = Mapping[str, Union[Range, Stops]]


def location_in_region(location: Location, region: Region) -> bool:
    return all(
        name in region and value in region[name] for name, value in location.items()
    )


@given(
    a=st.floats(min_value=100, max_value=900),
    b=st.floats(min_value=75, max_value=125),
    c=st.sampled_from([0, 1]),
)
def test_location_in_region(a: float, b: float, c: float) -> None:
    loc: Location = {"a": a, "b": b, "c": c}
    region: Region = {"a": Range(100, 900), "b": Range(75, 125), "c": Stops({0, 1})}
    assert location_in_region(loc, region)


@given(a=st.floats(), b=st.floats(), c=st.floats())
def test_location_outside_region(a: float, b: float, c: float) -> None:
    assume(not (100 <= a <= 900 and 75 <= b <= 125 and c in {0, 1}))

    loc: Location = {"a": a, "b": b, "c": c}
    region: Region = {"a": Range(100, 900), "b": Range(75, 125), "c": Stops({0, 1})}
    assert not location_in_region(loc, region)
