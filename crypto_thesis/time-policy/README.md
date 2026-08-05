# time-policy

`time-policy` is the engineering prototype for Chapter 4 of the thesis
"Research and Implementation of Key Technologies for Blockchain Data Sharing
with Non-contiguous Time Constraints".

The project compiles unordered and redundant time intervals into:

1. a unique semantic interval representation;
2. a maximal dyadic execution cover;
3. a canonical binary representation using the `NTP1` format;
4. a stable SHA-256 policy digest.

## Scope

This repository contains only time-policy compilation, matching, tests, and the
E1/E2 experiment framework. It does not contain blockchain, storage, revocation,
or custom cryptographic protocol code.

## Runtime

- Python 3.13.11
- `pytest`: unit and integration testing
- `hypothesis`: randomized property testing
- `numpy`: experiment data generation and numeric summaries
- `pandas`: experiment result tables
- `matplotlib`: reproducible paper figures

## Setup

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Design rules

- Time intervals are half-open: `[left, right)`.
- Datetimes must be timezone-aware and are normalized to UTC.
- Semantic digests are computed from canonical normalized intervals, not from
  the execution cover.
- Complexity is output-sensitive: `O(n log n + c)`.
- No claim is made that every fragmented policy has logarithmic size.
