import random
import json
import csv
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

cities = ["Delhi", "Noida", "Gurgaon", "Mumbai", "Pune", "Bangalore"]
property_types = ["1BHK", "2BHK", "3BHK", "Plot", "Commercial"]
sources = ["portal", "website", "walk-in", "referral"]
statuses = ["new", "contacted", "follow_up"]

notes_samples = [
    "Client wants 2bhk near metro, loan pre-approved",
    "Budget flexible, looking next 2 months",
    "Just checking prices, will call later",
    "Investor looking for rental yield",
    "Needs possession before year end",
    "Talked once, no response after that",
    "Urgent requirement, family shifting soon",
    "NRI buyer, prefers email communication"
]

# ---------- LEADS CSV ----------
leads = []
for i in range(1, 151):
    leads.append({
        "lead_id": f"L{i:03}",
        "source": random.choice(sources),
        "budget": random.randint(3000000, 15000000),
        "city": random.choice(cities),
        "property_type": random.choice(property_types),
        "last_activity_minutes_ago": random.randint(5, 5000),
        "past_interactions": random.randint(0, 8),
        "notes": random.choice(notes_samples),
        "status": random.choice(statuses)
    })

with open(DATA_DIR / "leads.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=leads[0].keys())
    writer.writeheader()
    writer.writerows(leads)

# ---------- CALLS JSON ----------
call_templates = [
    (
        "Agent: Hi, this is Riya from ABC Realty.\n"
        "Client: Yes, I'm interested.\n"
        "Agent: You asked about a {ptype} in {city}. Can we schedule a visit?\n"
        "Client: Saturday works.\n"
        "Agent: Great, I’ll block a slot and share details.\n"
    ),
    (
        "Agent: Hello, following up on your inquiry.\n"
        "Client: I'm just browsing, not sure yet.\n"
        "Agent: No worries. Would you like options within a budget?\n"
        "Client: Maybe around {budget}.\n"
        "Agent: I’ll send curated options.\n"
    ),
    (
        "Agent: Good evening, calling about the {ptype} listing.\n"
        "Client: I'm in a hurry, can you be quick?\n"
        "Agent: Of course. It’s near {city} metro and available immediately.\n"
        "Client: Send me the brochure.\n"
    ),
    (
        "Agent: Hi, this is ABC Realty.\n"
        "Client: Please stop calling.\n"
        "Agent: Sorry for the disturbance. I’ll update your preferences.\n"
    ),
    (
        "Agent: Hello! You had asked about investment properties.\n"
        "Client: Yes, I need rental yield details.\n"
        "Agent: This {ptype} has strong ROI and steady occupancy.\n"
        "Client: Sounds good, send the numbers.\n"
    ),
    (
        "Agent: Hi, just checking if you’re still looking.\n"
        "Client: Not now, call next month.\n"
        "Agent: Noted. I’ll follow up then.\n"
    ),
    (
        "Agent: Hello, can I help with your shortlisting?\n"
        "Client: I want a ready-to-move {ptype} in {city}.\n"
        "Agent: I have 3 options. Are you free for a call today?\n"
        "Client: Yes, after 6 PM.\n"
    ),
    (
        "Agent: This is a quick follow-up on your inquiry.\n"
        "Client: I’m comparing with another builder.\n"
        "Agent: We can match amenities and offer better payment terms.\n"
        "Client: If the price fits {budget}, I’m interested.\n"
    ),
    (
        "Agent: Hello, I can arrange a site visit for the {ptype}.\n"
        "Client: I'm out of town. Any virtual tour?\n"
        "Agent: Yes, I can share a video walkthrough.\n"
        "Client: Please send it today.\n"
    ),
    (
        "Agent: Hi, we saw your request online.\n"
        "Client: Yeah, I need something cheap.\n"
        "Agent: Understood. I’ll share listings within your range.\n"
        "Client: Okay.\n"
    )
]

calls = []
for i in range(1, 26):
    city = random.choice(cities)
    ptype = random.choice(property_types)
    budget = f"₹{random.randint(30, 150)}L"
    template = random.choice(call_templates)
    transcript = template.format(city=city, ptype=ptype, budget=budget)
    calls.append({
        "call_id": f"C{i:03}",
        "lead_id": f"L{random.randint(1,150):03}",
        "transcript": transcript,
        "duration_seconds": random.randint(60, 900),
        "was_deal_closed": random.choice([True, False])
    })

with open(DATA_DIR / "calls.json", "w", encoding="utf-8") as f:
    json.dump(calls, f, indent=2)

print("✅ Data generated: leads.csv and calls.json")
