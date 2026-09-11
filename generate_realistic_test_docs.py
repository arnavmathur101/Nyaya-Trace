"""
Generate Realistic Scanned Test Documents (PNG & PDF) for NyayaTrace Audit Workbench
Creates synthetic yet authentic-looking scanned trial bundle documents (FIR + Seizure Memo)
with built-in procedural violations for rule testing.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_realistic_document_image(output_png="realistic_test_fir_seizure.png"):
    # Dimensions for standard A4 scanned document at 150 DPI (1240 x 1754)
    width, height = 1240, 1754
    
    # Paper background: warm vintage off-white scanned paper tone
    img = Image.new("RGB", (width, height), color=(248, 246, 240))
    draw = ImageDraw.Draw(img)

    # Try loading clean Windows system font, fallback to default if missing
    font_path_bold = r"C:\Windows\Fonts\arialbd.ttf"
    font_path_regular = r"C:\Windows\Fonts\arial.ttf"
    
    try:
        font_header = ImageFont.truetype(font_path_bold, 28)
        font_sub = ImageFont.truetype(font_path_bold, 22)
        font_body = ImageFont.truetype(font_path_regular, 20)
        font_body_bold = ImageFont.truetype(font_path_bold, 20)
        font_small = ImageFont.truetype(font_path_regular, 16)
    except Exception:
        font_header = font_sub = font_body = font_body_bold = font_small = ImageFont.load_default()

    # Draw Page Border & Header Boxes
    draw.rectangle([40, 40, width - 40, height - 40], outline=(80, 80, 80), width=3)
    draw.rectangle([50, 50, width - 50, 180], fill=(235, 238, 245), outline=(50, 70, 110), width=2)

    # State Emblem & Police Header
    draw.text((width // 2, 70), "FORM NO. 5.1 — STATE POLICE DEPARTMENT", fill=(30, 40, 70), font=font_header, anchor="mm")
    draw.text((width // 2, 110), "FIRST INFORMATION REPORT (U/S 154 Cr.P.C.)", fill=(180, 40, 40), font=font_header, anchor="mm")
    draw.text((width // 2, 148), "DISTRICT: CENTRAL DELHI | P.S.: POLICE STATION KAROL BAGH", fill=(50, 50, 50), font=font_small, anchor="mm")

    y = 210
    draw.line([60, y, width - 60, y], fill=(100, 100, 100), width=2)
    y += 20

    # Section 1: FIR Metadata Table
    meta_lines = [
        ("FIR No:", "0248/2026", "FIR Registration:", "2026-09-20 10:00:00"),
        ("Police Station:", "Police Station Karol Bagh, Delhi", "District:", "Central Delhi"),
        ("Sections Invoked:", "NDPS Act Sec 20(b), 29", "Booked Under:", "Special Act"),
        ("Investigating Officer:", "SI R.K. Sharma", "Complainant:", "Inspector Vijay Pal")
    ]

    for label1, val1, label2, val2 in meta_lines:
        draw.text((70, y), label1, fill=(60, 60, 60), font=font_body_bold)
        draw.text((290, y), val1, fill=(10, 10, 10), font=font_body)
        draw.text((640, y), label2, fill=(60, 60, 60), font=font_body_bold)
        draw.text((860, y), val2, fill=(10, 10, 10), font=font_body)
        y += 38

    y += 10
    draw.line([60, y, width - 60, y], fill=(180, 180, 180), width=1)
    y += 25

    # Section 2: Narrative / Summary
    draw.text((70, y), "INCIDENT DETAILS & BRIEF FACTS OF THE CASE:", fill=(40, 40, 40), font=font_sub)
    y += 35

    narrative = (
        "On 2026-09-20 at 09:30 hours, secret information was received at Police Station Karol Bagh regarding transport "
        "of contraband. The police team dispatched to the location and conducted search operations. "
        "A formal FIR was registered at 10:00:00 hours following initial verification by SI R.K. Sharma."
    )

    # Word wrap narrative
    words = narrative.split(" ")
    line = ""
    for w in words:
        if len(line + " " + w) > 85:
            draw.text((70, y), line, fill=(30, 30, 30), font=font_body)
            y += 30
            line = w
        else:
            line += " " + w if line else w
    if line:
        draw.text((70, y), line, fill=(30, 30, 30), font=font_body)
        y += 40

    y += 10
    # Section 3: Seizure Memo Banner Header
    draw.rectangle([50, y, width - 50, y + 60], fill=(240, 230, 220), outline=(140, 80, 40), width=2)
    draw.text((width // 2, y + 30), "SPOT SEIZURE MEMO & SEARCH RECORD (U/S 102 Cr.P.C.)", fill=(140, 40, 20), font=font_header, anchor="mm")
    y += 85

    seizure_lines = [
        ("Seizure Event Timestamp:", "2026-09-20 09:15:00"),
        ("Location of Seizure:", "Ajmal Khan Market, Karol Bagh, Delhi"),
        ("Items Recovered:", "5.0 kg Narcotic Contraband (Heroin)"),
        ("Panch Witness 1:", "Ramesh Kumar (Residing at Village 25 km away)"),
        ("Panch Witness 2:", "Suresh Verma (Residing at Local Market)")
    ]

    for label, val in seizure_lines:
        draw.text((70, y), label, fill=(60, 60, 60), font=font_body_bold)
        draw.text((360, y), val, fill=(10, 10, 10), font=font_body_bold)
        y += 38

    y += 15
    draw.line([60, y, width - 60, y], fill=(180, 180, 180), width=1)
    y += 25

    # Section 4: Mandatory Safeguard Flags
    draw.text((70, y), "STATUTORY & PROCEDURAL SAFEGUARDS CHECKLIST:", fill=(40, 40, 40), font=font_sub)
    y += 35

    safeguards = [
        ("Consent Memo Present:", "0"),
        ("Magistrate Sample Cert Present:", "0"),
        ("Videography Present:", "0"),
        ("Search Reasons Recorded:", "0")
    ]

    for label, val in safeguards:
        draw.text((90, y), label, fill=(60, 60, 60), font=font_body_bold)
        draw.text((450, y), val, fill=(180, 20, 20), font=font_body_bold)
        y += 32

    # Stamps & Signatures Section
    y = max(y + 60, height - 320)
    
    # Official Circular Police Stamp Seal (drawn with PIL shapes)
    stamp_cx, stamp_cy = 220, y + 80
    draw.ellipse([stamp_cx - 75, stamp_cy - 75, stamp_cx + 75, stamp_cy + 75], outline=(30, 70, 150), width=4)
    draw.ellipse([stamp_cx - 65, stamp_cy - 65, stamp_cx + 65, stamp_cy + 65], outline=(30, 70, 150), width=1)
    draw.text((stamp_cx, stamp_cy - 30), "POLICE STATION", fill=(30, 70, 150), font=font_small, anchor="mm")
    draw.text((stamp_cx, stamp_cy), "KAROL BAGH", fill=(30, 70, 150), font=font_body_bold, anchor="mm")
    draw.text((stamp_cx, stamp_cy + 30), "OFFICIAL SEAL", fill=(30, 70, 150), font=font_small, anchor="mm")

    # Signatures
    draw.text((width - 380, y + 40), "Sd/- SI R.K. Sharma", fill=(20, 20, 80), font=font_sub)
    draw.text((width - 380, y + 70), "Investigating Officer / SHO", fill=(60, 60, 60), font=font_body)
    draw.text((width - 380, y + 95), "P.S. Karol Bagh, Delhi", fill=(60, 60, 60), font=font_small)

    # Save PNG
    img.save(output_png, dpi=(150, 150))
    print(f"Created PNG test document: {output_png}")

    # Also save as PDF
    output_pdf = output_png.replace(".png", ".pdf")
    img.save(output_pdf, "PDF", resolution=150.0)
    print(f"Created PDF test document: {output_pdf}")

if __name__ == "__main__":
    create_realistic_document_image("realistic_test_fir_seizure.png")
