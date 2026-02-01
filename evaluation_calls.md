# Call Quality Evaluation (Part C2)

**Sample size:** 10 calls (manual labels in `data/eval_calls_labels.csv`)
**Decision rule:** predict “good” if `quality_score >= 0.7`

## Results

- Confusion Matrix (actual → predicted)
  - closed: {closed: 1, not_closed: 5}
  - not_closed: {closed: 0, not_closed: 4}
- Precision: 1.00
- Recall: 0.17
- F1: 0.29
- Accuracy: 0.50

## Wrong Predictions (2 examples)

1. **C001** — Predicted bad (score 0.50), labeled good. The transcript is short and polite but lacks explicit need discovery or closing attempts, so the model scores it conservatively.
2. **C003** — Predicted bad (score 0.50), labeled good. The call contains positive intent (“rental yield details”) but no direct closing signal, so quality_score stays below the 0.7 threshold.

## Notes

Raising signal detection for intent/closing (or lowering the threshold to ~0.6) would likely improve recall on good calls.
