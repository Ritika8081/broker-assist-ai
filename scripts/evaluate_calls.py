import json
import requests

API_URL = "http://127.0.0.1:8000/api/v1/call-eval"
CALLS_FILE = "data/calls.json"
LABELS_FILE = "data/eval_calls_labels.csv"
THRESHOLD = 0.7


def load_calls(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_labels(path):
    labels = {}
    with open(path, encoding="utf-8") as f:
        for line in f.read().splitlines()[1:]:
            call_id, label = line.split(",")
            labels[call_id] = label.strip()
    return labels


def compute_confusion(y_true, y_pred):
    # Binary labels: closed / not_closed
    confusion = {
        "closed": {"closed": 0, "not_closed": 0},
        "not_closed": {"closed": 0, "not_closed": 0}
    }
    for t, p in zip(y_true, y_pred):
        confusion[t][p] += 1
    return confusion


def precision_recall_f1(confusion):
    tp = confusion["closed"]["closed"]
    fp = confusion["not_closed"]["closed"]
    fn = confusion["closed"]["not_closed"]
    tn = confusion["not_closed"]["not_closed"]

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0

    return precision, recall, f1, accuracy


calls = load_calls(CALLS_FILE)
labels = load_labels(LABELS_FILE)

calls = [c for c in calls if c["call_id"] in labels]

y_true = []
y_pred = []
errors = []

for call in calls:
    payload = {
        "call_id": call["call_id"],
        "lead_id": call.get("lead_id"),
        "transcript": call.get("transcript", ""),
        "duration_seconds": call.get("duration_seconds", 0)
    }

    response = requests.post(API_URL, json=payload)
    if response.status_code != 200:
        print(f"Error: API returned status {response.status_code} for call {call['call_id']}")
        continue

    data = response.json()
    quality_score = float(data.get("quality_score", 0))
    predicted_closed = "closed" if quality_score >= THRESHOLD else "not_closed"
    actual_closed = "closed" if labels.get(call["call_id"]) == "good" else "not_closed"

    y_pred.append(predicted_closed)
    y_true.append(actual_closed)

    if predicted_closed != actual_closed:
        errors.append({
            "call_id": call["call_id"],
            "predicted": predicted_closed,
            "actual": actual_closed,
            "quality_score": quality_score
        })

conf_matrix = compute_confusion(y_true, y_pred)
precision, recall, f1, accuracy = precision_recall_f1(conf_matrix)

print("\n✅ Confusion Matrix:")
print(conf_matrix)
print(f"\nPrecision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1: {f1:.2f}")
print(f"Accuracy: {accuracy:.2f}")

if errors:
    print("\nMISPREDICTIONS")
    for e in errors:
        print(f"{e['call_id']}: predicted={e['predicted']} actual={e['actual']} score={e['quality_score']:.2f}")
