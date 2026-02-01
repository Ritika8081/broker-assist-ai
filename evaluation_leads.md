# Lead Prioritisation Evaluation (Part C1)

**Sample size:** 20 leads (manual labels in `data/eval_leads_labels.csv`)

## Results

**Confusion Matrix (actual → predicted)**

- hot: {hot: 1, warm: 6, cold: 0}
- warm: {hot: 1, warm: 5, cold: 1}
- cold: {hot: 1, warm: 4, cold: 1}

**Metrics (per class)**

- HOT — Precision: 0.33, Recall: 0.14, F1: 0.20
- WARM — Precision: 0.33, Recall: 0.71, F1: 0.45
- COLD — Precision: 0.50, Recall: 0.17, F1: 0.25

**Overall**

- Accuracy: 0.35
- Macro Precision: 0.39
- Macro Recall: 0.34
- Macro F1: 0.30
- Score vs **actual** bucket correlation: 0.15
- Score vs **predicted** bucket correlation: 0.91

## Insights (2–3)

1. **Warm bias:** High WARM recall (0.71) with low HOT recall (0.14) shows the rules overweight “warm” patterns, missing true HOT leads.
2. **Score alignment vs truth:** Score→predicted bucket correlation is high (0.91), but score→actual bucket correlation is low (0.15), meaning thresholds are consistent but the signals don’t match ground truth well.
3. **Cold detection is weak:** COLD recall is only 0.17, suggesting the rules need stronger negative signals (e.g., long inactivity + low engagement + weak intent from notes).
