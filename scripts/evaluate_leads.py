import csv
import requests
import numpy as np

# -----------------------------
API_URL = "http://127.0.0.1:8000/api/v1/lead-priority"
EVAL_FILE = "data/eval_leads_labels.csv"
LEADS_FILE = "data/leads.csv"
# -----------------------------

# Load ground truth labels
ground_truth = {}
with open(EVAL_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ground_truth[row["lead_id"]] = row["priority_bucket"]

# Load full leads and prepare payload
leads_by_id = {}
with open(LEADS_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        row["budget"] = int(row["budget"])
        row["last_activity_minutes_ago"] = int(row["last_activity_minutes_ago"])
        row["past_interactions"] = int(row["past_interactions"])
        leads_by_id[row["lead_id"]] = row

leads_payload = []
missing = []
for lead_id in ground_truth:
    if lead_id in leads_by_id:
        leads_payload.append(leads_by_id[lead_id])
    else:
        missing.append(lead_id)

if missing:
    print(f"Warning: {len(missing)} lead_ids missing from {LEADS_FILE}")

response = requests.post(API_URL, json={"max_results": len(leads_payload), "leads": leads_payload})

if response.status_code != 200:
    print(f"Error: API returned status {response.status_code}")
    exit(1)

data = response.json()

# Compare predictions to ground truth
y_true = []
y_pred = []
scores = []

for lead in data:
    lead_id = lead["lead_id"]
    priority = lead.get("priority_bucket", "warm")
    y_pred.append(priority)
    y_true.append(ground_truth[lead_id])
    scores.append(float(lead.get("priority_score", 0)))


def compute_confusion(y_true, y_pred, labels):
    confusion = {l: {l2: 0 for l2 in labels} for l in labels}
    for t, p in zip(y_true, y_pred):
        if t not in labels:
            continue
        if p not in labels:
            p = "cold"
        confusion[t][p] += 1
    return confusion


def precision_recall_f1(confusion, label, labels):
    tp = confusion[label][label]
    fp = sum(confusion[l][label] for l in labels if l != label)
    fn = sum(confusion[label][l] for l in labels if l != label)

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0
    return precision, recall, f1


labels = ["hot", "warm", "cold"]
conf_matrix = compute_confusion(y_true, y_pred, labels)
total = sum(conf_matrix[a][p] for a in labels for p in labels)
correct = sum(conf_matrix[l][l] for l in labels)
accuracy = correct / total if total else 0

bucket_rank = {"cold": 0, "warm": 1, "hot": 2}
actual_ranks = [bucket_rank[b] for b in y_true]
pred_ranks = [bucket_rank[b] for b in y_pred]

score_bucket_corr = float(np.corrcoef(scores, actual_ranks)[0, 1]) if len(scores) > 1 else 0
score_pred_corr = float(np.corrcoef(scores, pred_ranks)[0, 1]) if len(scores) > 1 else 0

print("\n✅ Confusion Matrix:")
for true_label in labels:
    print(f"{true_label}: {conf_matrix[true_label]}")

print("\nMETRICS (per class)")
macro_p = macro_r = macro_f1 = 0.0
for label in labels:
    p, r, f1 = precision_recall_f1(conf_matrix, label, labels)
    macro_p += p
    macro_r += r
    macro_f1 += f1
    print(f"{label.upper():5} | Precision: {p:.2f}  Recall: {r:.2f}  F1: {f1:.2f}")

macro_p /= len(labels)
macro_r /= len(labels)
macro_f1 /= len(labels)

print(f"\nAccuracy: {accuracy:.2f}")
print(f"Macro Precision: {macro_p:.2f}")
print(f"Macro Recall: {macro_r:.2f}")
print(f"Macro F1: {macro_f1:.2f}")
print(f"Score vs actual-bucket correlation: {score_bucket_corr:.2f}")
print(f"Score vs predicted-bucket correlation: {score_pred_corr:.2f}")
