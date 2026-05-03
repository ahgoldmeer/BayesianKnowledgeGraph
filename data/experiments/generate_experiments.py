import csv
import math
import random

def confidence_to_repetitions(confidence):
    k = 1.0
    if confidence >= 1.0:
        return 10
    n = k * confidence / (1 - confidence)
    return max(1, round(n))

def sanitize(term):
    return term.replace(' ', '_').replace('.', '_').replace('-', '_')

def rows_to_nal(rows, header_comment):
    lines = []
    lines.append(f"// {header_comment}")
    lines.append("// Frequency = original confidence value")
    lines.append("// Repetitions = derived from confidence via n = c / (1 - c)")
    lines.append("// 5 cycles between concept groups")
    lines.append("")
    for row in rows:
        subj = sanitize(row['Subject'])
        pred = sanitize(row['Predicate'])
        obj = sanitize(row['Object'])
        conf = float(row['Confidence'])
        reps = confidence_to_repetitions(conf)
        lines.append(f"// {row['Subject']} {row['Predicate']} {row['Object']} (conf={conf}, reps={reps})")
        for i in range(reps):
            lines.append(f"<(*,{subj},{obj}) --> {pred}>. %{conf};0.9%")
        lines.append("5")
        lines.append("")
    return '\n'.join(lines)

# Load CSV
rows = []
with open('/mnt/user-data/uploads/MedData.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Load concept queries
with open('/home/claude/concept_queries.nal', 'r') as f:
    query_block = f.read()

def write_nal(filename, content, include_queries=True):
    with open(filename, 'w') as f:
        f.write(content)
        if include_queries:
            f.write("\n\n")
            f.write(query_block)

# ============================================================
# EXPERIMENT 1: ORDERING SENSITIVITY
# ============================================================

# 1a - Original order (already have this, but regenerate for consistency)
write_nal('/home/claude/exp1a_original_order.nal',
    rows_to_nal(rows, "EXPERIMENT 1a - Original Order"))
print("Generated exp1a_original_order.nal")

# 1b - Reversed order
rows_reversed = list(reversed(rows))
write_nal('/home/claude/exp1b_reversed_order.nal',
    rows_to_nal(rows_reversed, "EXPERIMENT 1b - Reversed Order"))
print("Generated exp1b_reversed_order.nal")

# 1c - Disease clustered order
disease_objects = [
    "Influenza", "Pneumonia", "Migraine", "Anemia", "Rheumatoid Arthritis",
    "COVID-19", "Strep Throat", "Seasonal Allergies", "Asthma", "Food Poisoning",
    "Dehydration", "Chronic Fatigue Syndrome", "Hypertension", "Heart Disease",
    "Lyme Disease", "IBS", "Bronchitis", "Chronic Kidney Disease", "Ulcer",
    "Common Cold", "Mononucleosis", "Air Pollution Exposure"
]
rows_clustered = []
seen = set()
for disease in disease_objects:
    for row in rows:
        if row['Object'] == disease or row['Subject'] == disease:
            key = (row['Subject'], row['Predicate'], row['Object'])
            if key not in seen:
                rows_clustered.append(row)
                seen.add(key)
# Add any remaining rows not captured
for row in rows:
    key = (row['Subject'], row['Predicate'], row['Object'])
    if key not in seen:
        rows_clustered.append(row)
        seen.add(key)
write_nal('/home/claude/exp1c_clustered_order.nal',
    rows_to_nal(rows_clustered, "EXPERIMENT 1c - Disease Clustered Order"))
print("Generated exp1c_clustered_order.nal")

# 1d - Random order (fixed seed for reproducibility)
rows_random = list(rows)
random.seed(42)
random.shuffle(rows_random)
write_nal('/home/claude/exp1d_random_order.nal',
    rows_to_nal(rows_random, "EXPERIMENT 1d - Random Order (seed=42)"))
print("Generated exp1d_random_order.nal")

# ============================================================
# EXPERIMENT 2: ROBUSTNESS TO CONTRADICTION
# ============================================================

# Select high confidence statements to contradict — most impactful
contradictions = [
    # High confidence direct facts
    ("Anemia",      "caused_by",    "Iron_Deficiency",   0.0),
    ("Influenza",   "treated_with", "Oseltamivir",       0.0),
    ("Fever",       "is_symptom_of","Influenza",         0.0),
    ("COVID_19",    "caused_by",    "Viral_Infection",   0.0),
    ("Lyme_Disease","caused_by",    "Tick_Bite",         0.0),
    # Partial contradictions — reduce rather than negate
    ("Pneumonia",   "treated_with", "Antibiotics",       0.2),
    ("Migraine",    "treated_with", "Triptans",          0.2),
    ("Asthma",      "treated_with", "Inhaled_Corticosteroids", 0.2),
]

# 2a - Load base data first, then full contradictions
lines_2a = []
lines_2a.append("// EXPERIMENT 2a - Robustness to Contradiction (Full Negation)")
lines_2a.append("// Step 1: Load base knowledge")
lines_2a.append("// Step 2: Introduce direct contradictions at 0.0 frequency")
lines_2a.append("")
lines_2a.append("// === BASE KNOWLEDGE ===")
lines_2a.append("")

# Add base data
base_content = rows_to_nal(rows, "Base Knowledge")
lines_2a.append(base_content)
lines_2a.append("")
lines_2a.append("// === CONTRADICTIONS ===")
lines_2a.append("")

for subj, pred, obj, conf in contradictions:
    reps = confidence_to_repetitions(1 - conf) if conf < 1.0 else 1
    lines_2a.append(f"// CONTRADICT: {subj} {pred} {obj} -> now %{conf};0.9%")
    for i in range(reps):
        lines_2a.append(f"<(*,{subj},{obj}) --> {pred}>. %{conf};0.9%")
    lines_2a.append("5")
    lines_2a.append("")

lines_2a.append("")
lines_2a.append(query_block)

with open('/home/claude/exp2a_contradiction_full.nal', 'w') as f:
    f.write('\n'.join(lines_2a))
print("Generated exp2a_contradiction_full.nal")

# 2b - Partial contradictions only (reduce confidence rather than negate)
lines_2b = []
lines_2b.append("// EXPERIMENT 2b - Robustness to Contradiction (Partial)")
lines_2b.append("// Step 1: Load base knowledge")  
lines_2b.append("// Step 2: Introduce partial contradictions at reduced frequency")
lines_2b.append("")

partial_contradictions = [
    ("Anemia",      "caused_by",    "Iron_Deficiency",   0.3),
    ("Influenza",   "treated_with", "Oseltamivir",       0.3),
    ("Fever",       "is_symptom_of","Influenza",         0.3),
    ("COVID_19",    "caused_by",    "Viral_Infection",   0.3),
    ("Lyme_Disease","caused_by",    "Tick_Bite",         0.3),
    ("Pneumonia",   "treated_with", "Antibiotics",       0.4),
    ("Migraine",    "treated_with", "Triptans",          0.4),
    ("Asthma",      "treated_with", "Inhaled_Corticosteroids", 0.4),
]

lines_2b.append("// === BASE KNOWLEDGE ===")
lines_2b.append("")
lines_2b.append(base_content)
lines_2b.append("")
lines_2b.append("// === PARTIAL CONTRADICTIONS ===")
lines_2b.append("")

for subj, pred, obj, conf in partial_contradictions:
    reps = max(1, round((1-conf) / conf)) if conf > 0 else 5
    lines_2b.append(f"// WEAKEN: {subj} {pred} {obj} -> now %{conf};0.9%")
    for i in range(reps):
        lines_2b.append(f"<(*,{subj},{obj}) --> {pred}>. %{conf};0.9%")
    lines_2b.append("5")
    lines_2b.append("")

lines_2b.append("")
lines_2b.append(query_block)

with open('/home/claude/exp2b_contradiction_partial.nal', 'w') as f:
    f.write('\n'.join(lines_2b))
print("Generated exp2b_contradiction_partial.nal")

print("\nAll experiment files generated successfully.")
