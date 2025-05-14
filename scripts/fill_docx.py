import json
from docxtpl import DocxTemplate
import os

# Define service levels
SERVICE_LEVELS = {
    "No-Rx Weight Loss Management": 1,
    "Hyperbaric Treatment": 1,
    "Spa Facials": 1,
    "Cryotherapy (Local, Full Body)": 1,
    "Ozone Therapy": 1,
    "Compression Therapy": 1,
    "Full Body Massage": 1,
    "Body & Facial Waxing": 1,
    "Medical Evaluation Wellness Visit (Marijuana Visit included)": 1,
    "Chiropractic (No Aesthesia)": 1,
    "Red Light Therapy": 1,
    
    "Botox, Beauty Fillers & Injectables": 2,
    "IV Hydration / Therapy": 2,
    "Prescription Weight Loss Treatment": 2,
    "Ketamine Therapy": 2,
    "Microdermabrasion": 2,
    "Light Chemical Peels": 2,
    "Dermaplaning Exfoliation Treatment": 2,
    "Non-Laser Brown Spot Removal / Skin Tag Removal": 2,
    "O-SHOT & P-SHOT": 2,
    "Chelation Therapy": 2,
    "BHRT (no pellet insertion)": 2,
    "Platelet Rich Plasma Therapy (PRP / PRF)": 2,
    "HCG Injections or Liquid Drops Treatment": 2,
    "Acupuncture": 2,
    "Permanent Hair Removal Electrolysis": 2,
    "Mesotherapy (Excluding PC/DC)": 2,
    "Permanent Make Up": 2,
    "Microneedling": 2,
    "Testosterone Injections": 2,
    "Topical Exosome Treatments": 2,

    "BHRT (pellet insertion)": 3,
    "Laser Cellulite Treatment": 3,
    "Laser Skin Resurfacing": 3,
    "Laser Tattoo Removal": 3,
    "Cold Laser for Fat Reduction": 3,
    "Liposonix Fat Reduction": 3,
    "Mesotherapy Vein Treatments": 3,
    "Thermage Skin Tightening": 3,
    "Cosmetic Pigmented Lesion Removal": 3,
    "Heavy Chemical Peels": 3,
    "Laser Hair Removal": 3,
    "Laser Brown Spot Removal": 3,
    "Fraxel Laser Treatment": 3,
    "Cavi-Lipo Fat Reduction": 3,
    "Varicose Vein Sclerotherapy": 3,
    "VelaShape Body Contouring": 3,
    "Intense Pulsed Light Therapy": 3,
    "Vaginal Rejuvenation": 3,

    "Hair Transplant Surgery": 4,
    "Threadlifts": 4,
    "Eyelid Surgery Blepharoplasty": 4,
    "Hair Restoration Surgery": 4,
    "Cosmetic Ear Pinning Otoplasty": 4,

    "Primary Medical Care Treatment": 5,
    "Urgent Care Treatment": 5,
    "Psychiatric Services": 5,
    "Abdominoplasty / Tummy Tucks": 5,
    "Butt Lift or Augmentation": 5,
    "Anesthesia": 5,
    "Surgical Laser Lipolysis (Smart Lipo)": 5,
    "Liposelection": 5,
    "Liposuction - Tumescent or Other": 5,
    "Mesotherapy with PC/DC Smart Liposuction": 5,
    "Face Lifts - Full Face Laser Lipolysis Lipodissolve": 5,
    "SPG Block": 5,
    "Stem Cell Therapy": 5
}

# Create a case-insensitive lookup dictionary
SERVICE_LEVELS_CI = {k.lower(): v for k, v in SERVICE_LEVELS.items()}

def fill_doc(template_path, json_path, output_path):
    with open(json_path, "r") as f:
        context = json.load(f)

    # Count service levels
    level_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    services = [s.strip() for s in context.get("services", "").split(",") if s.strip()]
    total = len(services)

    print("services", services)
    print("len", len(services))

    # Print services that don't exist in SERVICE_LEVELS (case-insensitive)
    print("\nServices not found in SERVICE_LEVELS:")
    for s in services:
        s = s.replace('\n', ' ')
        if s.lower() not in SERVICE_LEVELS_CI:
            print(f"- {s}")

    for s in services:
        s = s.replace('\n', ' ')
        level = SERVICE_LEVELS_CI.get(s.lower())
        if level:
            level_counts[level] += 1

    print("level_counts", level_counts)

    for level in range(1, 6):
        pct = round((level_counts[level] / total) * 100) if total else 0
        context[f"level_{level}_pct"] = f"{pct}%"
        

    # Prepare template context
    render_data = {
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
    }

    doc = DocxTemplate(template_path)
    doc.render(render_data)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
