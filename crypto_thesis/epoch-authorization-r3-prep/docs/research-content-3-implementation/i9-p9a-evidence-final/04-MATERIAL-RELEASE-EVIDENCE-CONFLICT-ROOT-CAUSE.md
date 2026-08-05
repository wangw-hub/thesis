# Material-release conflict root cause

A7 scenario code produced `ALLOWED_AFTER_CURRENT_HEADER_ONLY`, while the outer accumulator/terminalizer independently used generic `ELIGIBLE_TEST_ONLY` or default `NOT_RELEASED`. Serialization selected both projections without conflict rejection. Thus a later valid observation could coexist with an older default.

The repair removes `NOT_RELEASED` as a multi-meaning terminal value and rejects projection conflicts.
