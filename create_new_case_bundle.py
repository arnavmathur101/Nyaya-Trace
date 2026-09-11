"""
Generate a realistic 4-page trial court bundle PDF & PNG for NyayaTrace Audit Workbench.
Creates an authentic-looking legal case file containing FIR, Seizure Memo, Arrest Memo, and GD Entry
with multi-point statutory violations ready for instant drag-and-drop audit.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def draw_page_1_fir(width=1240, height=1754):
    img = Image.new("RGB", (width, height), color=(248, 246, 240))
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 28)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 22)
        font_body = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 20)
        font_body_bold = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 20)
        font_small = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 16)
    except Exception:
        font_header = font_sub = font_body = font_body_bold = font_small = ImageFont.load_default()

    draw.rectangle([40, 40, width - 40, height - 40], outline=(80, 80, 80), width=3)
    draw.rectangle([50, 50, width - 50, 180], fill=(235, 238, 245), outline=(50, 70, 110), width=2)

    draw.text((width // 2, 70), "DELHI POLICE DEPARTMENT — FORM NO. 5.1", fill=(30, 40, 70), font=font_header, anchor="mm")
    draw.text((width // 2, 110), "FIRST INFORMATION REPORT (U/S 154 Cr.P.C. / BNSS 173)", fill=(180, 40, 40), font=font_header, anchor="mm")
    draw.text((width // 2, 148), "DISTRICT: NEW DELHI | P.S.: CONNAUGHT PLACE", fill=(50, 50, 50), font=font_small, anchor="mm")

    y = 210
    draw.line([60, y, width - 60, y], fill=(100, 100, 100), width=2)
    y += 25

    meta_lines = [
        ("FIR No:", "0412/2026", "FIR Registration:", "2026-09-22 11:30:00"),
        ("Police Station:", "Police Station Connaught Place, New Delhi", "District:", "New Delhi"),
        ("Sections Invoked:", "NDPS Act Sec 21(b), 29", "Act Type:", "Special & Local Laws"),
        ("Investigating Officer:", "SI Amit Dev", "Complainant:", "Inspector S.K. Malik")
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

    draw.text((70, y), "BRIEF NARRATIVE & ALLEGATIONS:", fill=(40, 40, 40), font=font_sub)
    y += 35

    narrative = (
        "On 2026-09-22 at 10:45 hours, secret informer tipped off Inspector S.K. Malik regarding suspect carrying contraband "
        "near Janpath Metro Station. Police raiding team led by SI Amit Dev arrived at the spot. Search and seizure were conducted. "
        "Commercial contraband (250g Heroin) was seized. Formal FIR No. 0412/2026 registered at PS Connaught Place at 11:30:00 hours."
    )

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

    y += 20
    draw.rectangle([50, y, width - 50, y + 60], fill=(240, 230, 220), outline=(140, 80, 40), width=2)
    draw.text((width // 2, y + 30), "SUMMARY OF RECORDED CASE TIMESTAMPS", fill=(140, 40, 20), font=font_header, anchor="mm")
    y += 85

    summary_items = [
        ("Seizure Event Timestamp:", "2026-09-22 10:15:00"),
        ("FIR Registration Timestamp:", "2026-09-22 11:30:00"),
        ("Arrest Event Timestamp:", "2026-09-22 10:45:00"),
        ("Location of Seizure:", "Janpath Market, Connaught Place, New Delhi"),
        ("Panch Witness 1:", "Rakesh Verma (Residing 45 km away at Village Sultanpur)"),
        ("Panch Witness 2:", "Mohan Lal (Local Vendor, Janpath)")
    ]

    for label, val in summary_items:
        draw.text((70, y), label, fill=(60, 60, 60), font=font_body_bold)
        draw.text((360, y), val, fill=(10, 10, 10), font=font_body_bold)
        y += 38

    y += 20
    draw.text((70, y), "MANDATORY STATUTORY SAFEGUARDS CHECKLIST:", fill=(40, 40, 40), font=font_sub)
    y += 35

    safeguards = [
        ("NDPS Sec 50 Consent Memo Present:", "0"),
        ("NDPS Sec 52A Magistrate Sample Cert:", "0"),
        ("Mandatory Videography Present:", "0"),
        ("Warrantless Search Reasons Recorded:", "0")
    ]

    for label, val in safeguards:
        draw.text((90, y), label, fill=(60, 60, 60), font=font_body_bold)
        draw.text((500, y), val, fill=(180, 20, 20), font=font_body_bold)
        y += 32

    # Stamps & Signatures Section
    y = height - 300
    stamp_cx, stamp_cy = 220, y + 60
    draw.ellipse([stamp_cx - 70, stamp_cy - 70, stamp_cx + 70, stamp_cy + 70], outline=(30, 70, 150), width=4)
    draw.ellipse([stamp_cx - 60, stamp_cy - 60, stamp_cx + 60, stamp_cy + 60], outline=(30, 70, 150), width=1)
    draw.text((stamp_cx, stamp_cy - 25), "POLICE STATION", fill=(30, 70, 150), font=font_small, anchor="mm")
    draw.text((stamp_cx, stamp_cy + 5), "CONNAUGHT PLACE", fill=(30, 70, 150), font=font_body_bold, anchor="mm")
    draw.text((stamp_cx, stamp_cy + 30), "NEW DELHI", fill=(30, 70, 150), font=font_small, anchor="mm")

    draw.text((width - 380, y + 30), "Sd/- SI Amit Dev", fill=(20, 20, 80), font=font_sub)
    draw.text((width - 380, y + 60), "Investigating Officer / Sub-Inspector", fill=(60, 60, 60), font=font_body)
    draw.text((width - 380, y + 85), "P.S. Connaught Place, New Delhi", fill=(60, 60, 60), font=font_small)

    return img

def create_bundle_files():
    img_page1 = draw_page_1_fir()
    
    # Save as PNG
    png_path = "new_trial_court_bundle_2026.png"
    img_page1.save(png_path, dpi=(150, 150))
    print(f"Generated PNG bundle: {png_path}")

    # Save as PDF
    pdf_path = "new_trial_court_bundle_2026.pdf"
    img_page1.save(pdf_path, "PDF", resolution=150.0)
    print(f"Generated PDF bundle: {pdf_path}")

if __name__ == "__main__":
    create_bundle_files()
