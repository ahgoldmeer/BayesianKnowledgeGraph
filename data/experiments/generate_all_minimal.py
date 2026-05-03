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

# Load minimal CSV
rows = []
with open('/home/claude/MedData_minimal.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"Loaded {len(rows)} rows from minimal dataset")

# ============================================================
# CONCEPT QUERIES - only diseases in minimal set
# ============================================================
diseases = ["Influenza", "Pneumonia", "Migraine", "Anemia", "COVID_19"]

query_lines = []
query_lines.append("// ============================================================")
query_lines.append("// CONCEPT BAG QUERY BLOCK - Minimal Dataset")
query_lines.append("// ============================================================")
query_lines.append("")
for disease in diseases:
    query_lines.append(f"// --- {disease} ---")
    query_lines.append(f"<{disease} --> ?x>?")
    query_lines.append("10")
    query_lines.append(f"<?x --> {disease}>?")
    query_lines.append("10")
    query_lines.append(f"<(*,{disease},?x) --> ?r>?")
    query_lines.append("10")
    query_lines.append(f"<(*,?x,{disease}) --> ?r>?")
    query_lines.append("10")
    query_lines.append("")
query_block = '\n'.join(query_lines)

def write_nal(filename, content, include_queries=True):
    with open(filename, 'w') as f:
        f.write(content)
        if include_queries:
            f.write("\n\n")
            f.write(query_block)

# ============================================================
# BASELINE - MedData_minimal v2
# ============================================================
write_nal('/home/claude/minimal_baseline.nal',
    rows_to_nal(rows, "MINIMAL BASELINE - MedData_minimal.csv"))
print("Generated minimal_baseline.nal")

# ============================================================
# BRIDGED VERSION
# ============================================================
predicates = sorted(set(sanitize(row['Predicate']) for row in rows))
bridge_lines = []
bridge_lines.append("// MINIMAL DATASET - Bridging Rule Version")
bridge_lines.append("// Bridging rules loaded FIRST to prevent relation collapse")
bridge_lines.append("")
bridge_lines.append("// ============================================================")
bridge_lines.append("// SECTION 1: BRIDGING RULES")
bridge_lines.append("// ============================================================")
bridge_lines.append("")
for pred in predicates:
    bridge_lines.append(f"// Align product <-> relational image for: {pred}")
    bridge_lines.append(f"<<(*,?x,?y) --> {pred}> ==> <?x --> (/, {pred},_,?y)>>.")
    bridge_lines.append(f"<<(?x --> (/, {pred},_,?y))> ==> <(*,?x,?y) --> {pred}>>.")
    bridge_lines.append("5")
    bridge_lines.append("")
bridge_lines.append("")
bridge_lines.append("// ============================================================")
bridge_lines.append("// SECTION 2: DATA")
bridge_lines.append("// ============================================================")
bridge_lines.append("")
bridge_lines.append(rows_to_nal(rows, "Minimal Dataset Data"))
bridge_lines.append("")
bridge_lines.append("// ============================================================")
bridge_lines.append("// SECTION 3: QUERIES")
bridge_lines.append("// ============================================================")
bridge_lines.append("")
bridge_lines.append(query_block)
with open('/home/claude/minimal_bridged.nal', 'w') as f:
    f.write('\n'.join(bridge_lines))
print("Generated minimal_bridged.nal")

# ============================================================
# EXPERIMENT 1: ORDERING SENSITIVITY
# ============================================================

# 1a original
write_nal('/home/claude/minimal_exp1a_original.nal',
    rows_to_nal(rows, "EXP 1a - Original Order"))
print("Generated minimal_exp1a_original.nal")

# 1b reversed
write_nal('/home/claude/minimal_exp1b_reversed.nal',
    rows_to_nal(list(reversed(rows)), "EXP 1b - Reversed Order"))
print("Generated minimal_exp1b_reversed.nal")

# 1c disease clustered
disease_names = ["Influenza", "Pneumonia", "Migraine", "Anemia", "COVID-19"]
rows_clustered = []
seen = set()
for disease in disease_names:
    for row in rows:
        key = (row['Subject'], row['Predicate'], row['Object'])
        if (row['Object'] == disease or row['Subject'] == disease) and key not in seen:
            rows_clustered.append(row)
            seen.add(key)
for row in rows:
    key = (row['Subject'], row['Predicate'], row['Object'])
    if key not in seen:
        rows_clustered.append(row)
        seen.add(key)
write_nal('/home/claude/minimal_exp1c_clustered.nal',
    rows_to_nal(rows_clustered, "EXP 1c - Disease Clustered Order"))
print("Generated minimal_exp1c_clustered.nal")

# 1d random
rows_random = list(rows)
random.seed(42)
random.shuffle(rows_random)
write_nal('/home/claude/minimal_exp1d_random.nal',
    rows_to_nal(rows_random, "EXP 1d - Random Order (seed=42)"))
print("Generated minimal_exp1d_random.nal")

# ============================================================
# EXPERIMENT 2: CONTRADICTION
# ============================================================

base_content = rows_to_nal(rows, "Base Knowledge")

# 2a full negation
contradictions_full = [
    ("Anemia",    "caused_by",    "Iron_Deficiency",  0.0),
    ("Influenza", "treated_with", "Oseltamivir",      0.0),
    ("Fever",     "is_symptom_of","Influenza",        0.0),
    ("COVID_19",  "caused_by",    "Viral_Infection",  0.0),
    ("Migraine",  "treated_with", "Triptans",         0.2),
    ("Pneumonia", "treated_with", "Antibiotics",      0.2),
]
lines_2a = []
lines_2a.append("// EXP 2a - Contradiction Full Negation (Minimal Dataset)")
lines_2a.append("")
lines_2a.append("// === BASE KNOWLEDGE ===")
lines_2a.append(base_content)
lines_2a.append("")
lines_2a.append("// === CONTRADICTIONS ===")
lines_2a.append("")
for subj, pred, obj, conf in contradictions_full:
    reps = max(1, round((1 - conf) / (conf + 0.001)))
    reps = min(reps, 10)
    lines_2a.append(f"// CONTRADICT: {subj} {pred} {obj} -> %{conf};0.9%")
    for i in range(reps):
        lines_2a.append(f"<(*,{subj},{obj}) --> {pred}>. %{conf};0.9%")
    lines_2a.append("5")
    lines_2a.append("")
lines_2a.append(query_block)
with open('/home/claude/minimal_exp2a_contradiction_full.nal', 'w') as f:
    f.write('\n'.join(lines_2a))
print("Generated minimal_exp2a_contradiction_full.nal")

# 2b partial
contradictions_partial = [
    ("Anemia",    "caused_by",    "Iron_Deficiency",  0.3),
    ("Influenza", "treated_with", "Oseltamivir",      0.3),
    ("Fever",     "is_symptom_of","Influenza",        0.3),
    ("COVID_19",  "caused_by",    "Viral_Infection",  0.3),
    ("Migraine",  "treated_with", "Triptans",         0.4),
    ("Pneumonia", "treated_with", "Antibiotics",      0.4),
]
lines_2b = []
lines_2b.append("// EXP 2b - Contradiction Partial Weakening (Minimal Dataset)")
lines_2b.append("")
lines_2b.append("// === BASE KNOWLEDGE ===")
lines_2b.append(base_content)
lines_2b.append("")
lines_2b.append("// === PARTIAL CONTRADICTIONS ===")
lines_2b.append("")
for subj, pred, obj, conf in contradictions_partial:
    reps = max(1, round((1 - conf) / conf))
    lines_2b.append(f"// WEAKEN: {subj} {pred} {obj} -> %{conf};0.9%")
    for i in range(reps):
        lines_2b.append(f"<(*,{subj},{obj}) --> {pred}>. %{conf};0.9%")
    lines_2b.append("5")
    lines_2b.append("")
lines_2b.append(query_block)
with open('/home/claude/minimal_exp2b_contradiction_partial.nal', 'w') as f:
    f.write('\n'.join(lines_2b))
print("Generated minimal_exp2b_contradiction_partial.nal")

print(f"\nAll files generated.")
print(f"Dataset: {len(rows)} rows, {len(diseases)} diseases, {len(predicates)} predicates")
print(f"Total statements (baseline): {sum(confidence_to_repetitions(float(r['Confidence'])) for r in rows)}")
