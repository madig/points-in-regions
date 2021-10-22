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

    def __contains__(self, value: Union[float, Range, Stops]) -> bool:
        if isinstance(value, Range):
            start, end = sorted((value.start, value.end))
            return self.start <= start <= self.end and self.start <= end <= self.end
        if isinstance(value, Stops):
            return all(self.start <= stop <= self.end for stop in value.stops)
        return self.start <= value <= self.end


@dataclass
class Stops:
    __slots__ = "stops"

    stops: set[float]

    def __contains__(self, value: Union[float, Range, Stops]) -> bool:
        if isinstance(value, Range):
            return value.start == value.end and value.start in self.stops
        if isinstance(value, Stops):
            return all(stop in self.stops for stop in value.stops)
        return value in self.stops


Location = Mapping[str, float]
Region = Mapping[str, Union[Range, Stops]]


def location_in_region(location: Location, region: Region) -> bool:
    return location.keys() == region.keys() and all(
        value in region[name] for name, value in location.items()
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


def region_in_region(region1: Region, region2: Region) -> bool:
    return region1.keys() == region2.keys() and all(
        value in region2[name] for name, value in region1.items()
    )


@given(
    a1=st.floats(min_value=100, max_value=900),
    a2=st.floats(min_value=100, max_value=900),
    b1=st.floats(min_value=75, max_value=125),
    b2=st.floats(min_value=75, max_value=125),
    c1=st.sampled_from([0, 1]),
    c2=st.sampled_from([0, 1]),
)
def test_region_in_region(
    a1: float, a2: float, b1: float, b2: float, c1: float, c2: float
) -> None:
    region1: Region = {"a": Range(a1, a2), "b": Range(b1, b2), "c": Stops({c1, c2})}
    region2: Region = {"a": Range(100, 900), "b": Range(75, 125), "c": Stops({0, 1})}
    assert region_in_region(region1, region2)


@given(
    a1=st.floats(),
    a2=st.floats(),
    b1=st.floats(),
    b2=st.floats(),
    c1=st.floats(),
    c2=st.floats(),
)
def test_region_outside_region(
    a1: float, a2: float, b1: float, b2: float, c1: float, c2: float
) -> None:
    assume(
        not (
            100 <= a1 <= 900
            and 100 <= a2 <= 900
            and 75 <= b1 <= 125
            and 75 <= b2 <= 125
            and c1 in {0, 1}
            and c2 in {0, 1}
        )
    )

    region1: Region = {"a": Range(a1, a2), "b": Range(b1, b2), "c": Stops({c1, c2})}
    region2: Region = {"a": Range(100, 900), "b": Range(75, 125), "c": Stops({0, 1})}
    assert not region_in_region(region1, region2)
