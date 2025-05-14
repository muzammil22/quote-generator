import sys
import json
from docxtpl import DocxTemplate

SERVICE_LEVELS = {
    "Bhrt (no Pellet Insertion)": 1,
    "Non Invasive Weight Loss Treatment": 2,
    # Add more mappings here
}

template_path = sys.argv[1]
json_path = sys.argv[2]
output_path = sys.argv[3]

with open(json_path, 'r') as f:
    context = json.load(f)

# Initialize counters
level_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

services = [s.strip() for s in context.get("services", "").split(",") if s.strip()]
total = len(services)

for s in services:
    level = SERVICE_LEVELS.get(s)
    if level:
        level_counts[level] += 1

# Calculate percentages
for level in range(1, 6):
    context[f"level_{level}_pct"] = f"{int((level_counts[level] / total) * 100)}%" if total else "0%"

print(context)

doc = DocxTemplate(template_path)
doc.render({
    'entity': context.get('entity'),
    'state': context.get('state'),
    'services': context.get('services'),
    'revenue': f"${context.get('revenue')}",
    'retro_date': context.get('retro_date'),
    'limit': context.get('limit'),
    'claims': context.get('claims'),
    'disciplinary': context.get('disciplinary'),
    'program_pp23x': "X",
    'level_1_pct': context['level_1_pct'],
    'level_2_pct': context['level_2_pct'],
    'level_3_pct': context['level_3_pct'],
    'level_4_pct': context['level_4_pct'],
    'level_5_pct': context['level_5_pct'],
})
doc.save(output_path)
