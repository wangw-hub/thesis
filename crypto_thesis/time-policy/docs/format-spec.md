# NTP1 Canonical Format

All integers are unsigned and big-endian except `time_origin`, which is a
signed Unix timestamp in seconds.

| Field | Width |
|---|---:|
| magic (`NTP1`) | 4 bytes |
| schema | uint16 |
| time_origin | int64 |
| delta seconds | uint64 |
| domain size | uint64 |
| interval count | uint32 |
| each `(left, right)` | 2 x uint64 |

Intervals must be ordered, disjoint, non-adjacent, and inside the domain.
JSON is not a canonical digest input.
