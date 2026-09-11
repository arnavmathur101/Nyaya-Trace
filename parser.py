"""
NyayaTrace Legal Document Parser
Parses raw text / document files, extracts legal events, metadata, and inserts them into nyayatrace.db.
"""

import re
import sqlite3
from datetime import datetime

DB_PATH = "nyayatrace.db"

def parse_and_ingest_text(text: str, bundle_id: str = "CASE-2026-LIVE") -> dict:
    """
    Extracts legal event parameters from text and inserts document + event into database.
    """
    text_lower = text.lower()
    
    # Extract Document Type
    if "fir" in text_lower or "first information report" in text_lower:
        doc_type = "FIR"
    elif "seizure" in text_lower or "panchnama" in text_lower:
        doc_type = "SEIZURE_MEMO"
    elif "fsl" in text_lower or "forensic" in text_lower:
        doc_type = "FSL_REPORT"
    elif "arrest" in text_lower:
        doc_type = "ARREST_MEMO"
    elif "search" in text_lower:
        doc_type = "SEARCH_MEMO"
    else:
        doc_type = "GENERAL_MEMO"

    # Extract Timestamp (YYYY-MM-DD HH:MM)
    date_match = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?', text)
    if date_match:
        doc_date = date_match.group(0)
    else:
        doc_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Safeguard Flags
    consent_memo = 1 if ("consent memo" in text_lower or "sec 50 consent" in text_lower) else 0
    sample_cert = 1 if ("magistrate cert" in text_lower or "sec 52a cert" in text_lower) else 0
    videography = 1 if ("videography" in text_lower or "video recording" in text_lower) else 0
    search_reasons = 1 if ("reasons recorded" in text_lower or "grounds of search" in text_lower) else 0

    # Lat / Lon coordinates
    lat_match = re.search(r'lat(?:itude)?\s*[:=]?\s*([0-9]+\.[0-9]+)', text_lower)
    lon_match = re.search(r'lon(?:gitude)?\s*[:=]?\s*([0-9]+\.[0-9]+)', text_lower)
    lat = float(lat_match.group(1)) if lat_match else 28.6139
    lon = float(lon_match.group(1)) if lon_match else 77.2090

    # Insert into Database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    doc_id = f"DOC-{int(datetime.now().timestamp())}"
    cursor.execute("""
        INSERT INTO documents (
            doc_id, bundle_id, doc_type, doc_title, doc_date,
            consent_memo_present, sample_certification_present,
            search_reasons_recorded, videography_present
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doc_id, bundle_id, doc_type, f"{doc_type} - {bundle_id}", doc_date,
        consent_memo, sample_cert, search_reasons, videography
    ))

    event_id = f"EVT-{int(datetime.now().timestamp())}"
    cursor.execute("""
        INSERT INTO events (
            event_id, doc_id, event_type, event_timestamp, location_name, lat, lon
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id, doc_id, doc_type, doc_date, "Uploaded Location", lat, lon
    ))

    conn.commit()
    conn.close()

    return {
        "doc_id": doc_id,
        "bundle_id": bundle_id,
        "doc_type": doc_type,
        "doc_date": doc_date,
        "consent_memo": consent_memo,
        "sample_cert": sample_cert,
        "videography": videography
    }
