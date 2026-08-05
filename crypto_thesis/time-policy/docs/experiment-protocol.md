# E1/E2 Experiment Protocol

## E2 correctness gate

1. Run unit and boundary tests.
2. Run all semantic bitmaps for each `U` from 1 through 12.
3. Run the 10,000-case Hypothesis compiler property.
4. Do not interpret E1 results if any E2 check fails.

## E1 execution

```powershell
python -m experiments.generate --config experiments/configs/e1.yaml --output experiments/raw/e1_cases.jsonl
python -m experiments.run --input experiments/raw/e1_cases.jsonl --output experiments/raw/e1_results.csv --repeats 30
python -m experiments.analyze --input experiments/raw/e1_results.csv --output experiments/processed/e1_summary.csv
python -m experiments.plot --input experiments/processed/e1_summary.csv --output experiments/figures/e1_sizes.png
```

Formal E1 runs are intentionally not part of the current implementation
milestone.
