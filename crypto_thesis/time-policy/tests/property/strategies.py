"""Reusable Hypothesis strategies for valid raw interval policies."""

from __future__ import annotations

from hypothesis import strategies as st

from time_policy.models import Interval


@st.composite
def raw_policies(draw):
    """Generate a domain and an unordered, potentially redundant policy."""

    domain_size = draw(st.integers(min_value=1, max_value=256))
    bounds = st.tuples(
        st.integers(min_value=0, max_value=domain_size - 1),
        st.integers(min_value=1, max_value=domain_size),
    ).filter(lambda pair: pair[0] < pair[1])
    pairs = draw(st.lists(bounds, min_size=0, max_size=40))
    return domain_size, [Interval(left, right) for left, right in pairs]
