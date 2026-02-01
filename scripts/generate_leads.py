# scripts/generate_leads.py
import csv
import random
import os

# File path
file_path = os.path.join("data", "leads.csv")

# Lead statuses
statuses = ["new", "follow_up", "contacted"]

# Generate 20 leads
leads = []
for i in range(1, 21):
    lead_id = f"L{i:03d}"
    status = random.choice(statuses)
    last_activity_minutes_ago = random.randint(10, 1000)
    budget = random.choice([3000000, 6000000, 12000000])  # in INR
    leads.append([lead_id, status, last_activity_minutes_ago, budget])

# Write to CSV
os.makedirs("data", exist_ok=True)
with open(file_path, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["lead_id", "status", "last_activity_minutes_ago", "budget"])
    writer.writerows(leads)

print(f"Generated {len(leads)} leads in {file_path}")
