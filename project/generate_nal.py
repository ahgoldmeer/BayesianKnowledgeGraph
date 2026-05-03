import csv
import math

def confidence_to_repetitions(confidence):
    # NARS confidence formula: c = n / (n + k) where k=1 (default)
    # solving for n: n = k * c / (1 - c)
    # We use this to determine how many times to repeat a statement
    # to naturally arrive at approximately that confidence through revision
    k = 1.0
    if confidence >= 1.0:
        return 10
    n = k * confidence / (1 - confidence)
    reps = max(1, round(n))
    return reps

def sanitize(term):
    return term.replace(' ', '_').replace('.', '_').replace('-', '_')

rows = []
with open('/mnt/user-data/uploads/MedData.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

lines = []
lines.append("// NARS Medical Knowledge Base")
lines.append("// Auto-generated from MedData.csv")
lines.append("// 5 cycles between concepts, repetitions derived from confidence values")
lines.append("")

for row in rows:
    subj = sanitize(row['Subject'])
    pred = sanitize(row['Predicate'])
    obj = sanitize(row['Object'])
    conf = float(row['Confidence'])
    reps = confidence_to_repetitions(conf)
    
    lines.append(f"// {row['Subject']} {row['Predicate']} {row['Object']} (conf={conf}, reps={reps})")
    for i in range(reps):
        lines.append(f"<(*,{subj},{obj}) --> {pred}>. %1.0;0.9%")
    lines.append("5")
    lines.append("")

with open('/home/claude/MedData.nal', 'w') as f:
    f.write('\n'.join(lines))

print("Generated MedData.nal")
print(f"Total statements: {sum(confidence_to_repetitions(float(r['Confidence'])) for r in rows)}")
print(f"Total concepts: {len(rows)}")
print("\nSample repetition mapping:")
for row in rows[:5]:
    c = float(row['Confidence'])
    print(f"  {row['Subject']} {row['Predicate']} {row['Object']}: conf={c} -> {confidence_to_repetitions(c)} reps")
