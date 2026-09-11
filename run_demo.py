"""
NyayaTrace One-Command Demo Runner
Resets nyayatrace.db, re-seeds synthetic case bundles (GAMMA, DELTA), executes the 21-rule audit engine,
regenerates the Excel report, and builds the Cross-Examination Cheat Sheet for CASE-2026-GAMMA.
"""

import os
import sys
import sqlite3
import pandas as pd

# Local Engine Imports
from rules import (
    NyayaAuditEngine, ensure_db_schema,
    RuleCT01, RuleCT02, RuleCT03, RuleCT04, RuleCT05,
    RuleCT06, RuleCT07, RuleCT08, RuleCT09, RuleCT10,
    RuleCT11, RuleCT12, RuleCT13, RuleCT14, RuleCT15,
    RuleCT16, RuleCT17, RuleCT18, RuleCT19, RuleCT20, RuleCT21
)
from export_report import generate_audit_excel_report
from generate_cheatsheet import generate_cheatsheet

DB_PATH = "nyayatrace.db"
SCHEMA_SQL = "schema.sql"
GAMMA_SQL = "sample_data_gamma.sql"
DELTA_SQL = "sample_data_delta.sql"

def reset_and_seed_database():
    """Resets database and executes schema.sql + seed SQL files."""
    print("-----------------------------------------------------------------")
    print("STEP 1: Resetting database and applying schema...")
    print("-----------------------------------------------------------------")
    
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"  -> Removed existing '{DB_PATH}'")
        except Exception as e:
            print(f"  -> Warning: Could not remove '{DB_PATH}': {e}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Apply Schema
    if os.path.exists(SCHEMA_SQL):
        with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print(f"  -> Applied schema from '{SCHEMA_SQL}'")
    else:
        print(f"  -> Warning: '{SCHEMA_SQL}' not found!")

    # Ensure non-destructive safeguard columns exist
    ensure_db_schema(conn)

    # 2. Seed CASE-2026-GAMMA
    if os.path.exists(GAMMA_SQL):
        with open(GAMMA_SQL, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print(f"  -> Seeded CASE-2026-GAMMA from '{GAMMA_SQL}'")

    # 3. Seed CASE-2026-DELTA
    if os.path.exists(DELTA_SQL):
        with open(DELTA_SQL, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print(f"  -> Seeded CASE-2026-DELTA from '{DELTA_SQL}'")

    # 4. Ingest Real OCR Document Sample
    try:
        from ingest import create_synthetic_test_document_image, ingest_bundle
        sample_img = create_synthetic_test_document_image("synthetic_sample_fir.png")
        ingest_bundle(sample_img, bundle_id="CASE-2026-OCR-DEMO")
        print("  -> Ingested real OCR sample into 'CASE-2026-OCR-DEMO'")
    except Exception as e:
        print(f"  -> OCR Ingestion Notice: {e}")

    conn = sqlite3.connect(DB_PATH)
    conn.commit()
    conn.close()
    print("Database reset, seeding & OCR ingestion complete.")


def run_audit_engine():
    """Executes the full 21-rule NyayaAuditEngine."""
    print("\n-----------------------------------------------------------------")
    print("STEP 2: Executing 21-Rule NyayaAuditEngine...")
    print("-----------------------------------------------------------------")
    
    engine = NyayaAuditEngine(DB_PATH)
    rules_list = [
        RuleCT01(), RuleCT02(), RuleCT03(), RuleCT04(), RuleCT05(),
        RuleCT06(), RuleCT07(), RuleCT08(), RuleCT09(), RuleCT10(),
        RuleCT11(), RuleCT12(), RuleCT13(), RuleCT14(), RuleCT15(),
        RuleCT16(), RuleCT17(), RuleCT18(), RuleCT19(), RuleCT20(), RuleCT21()
    ]
    for r in rules_list:
        engine.register_rule(r)
    
    engine.run()


def generate_reports():
    """Generates Excel Audit Report & Cross-Exam Cheat Sheet."""
    print("\n-----------------------------------------------------------------")
    print("STEP 3: Regenerating Excel Report & Cross-Exam Cheat Sheet...")
    print("-----------------------------------------------------------------")
    
    excel_path = generate_audit_excel_report(DB_PATH, "NyayaTrace_Audit_Report.xlsx")
    cs_path = generate_cheatsheet("CASE-2026-GAMMA", DB_PATH)
    
    return excel_path, cs_path


def print_summary():
    """Prints final summary of the demo run."""
    conn = sqlite3.connect(DB_PATH)
    
    # Query summary counts
    df_all = pd.read_sql_query("SELECT bundle_id, rule_id, severity FROM contradictions", conn)
    doc_cnt = pd.read_sql_query("SELECT COUNT(*) as cnt FROM documents", conn).iloc[0]['cnt']
    evt_cnt = pd.read_sql_query("SELECT COUNT(*) as cnt FROM events", conn).iloc[0]['cnt']
    conn.close()

    total_contras = len(df_all)
    rules_fired = df_all['rule_id'].nunique() if total_contras > 0 else 0
    bundles_audited = df_all['bundle_id'].nunique() if total_contras > 0 else 0
    
    print("\n=================================================================")
    print("                  NYAYATRACE AUDIT DEMO SUMMARY                  ")
    print("=================================================================")
    print(f" Total Documents Audited   : {doc_cnt}")
    print(f" Total Legal Events Parsed  : {evt_cnt}")
    print(f" Active Bundles Audited    : {bundles_audited}")
    print(f" Total Contradictions Found: {total_contras}")
    print(f" Distinct Rules Violated   : {rules_fired} / 21 Rules")
    print("-----------------------------------------------------------------")
    if total_contras > 0:
        sev_counts = df_all['severity'].value_counts().to_dict()
        print(f" Severity Breakdown       : CRITICAL: {sev_counts.get('CRITICAL',0)} | HIGH: {sev_counts.get('HIGH',0)} | MEDIUM: {sev_counts.get('MEDIUM',0)}")
    print("-----------------------------------------------------------------")
    print(" Generated Artifacts:")
    print("   1. Database Report     : nyayatrace.db")
    print("   2. Excel Audit Report  : NyayaTrace_Audit_Report.xlsx")
    print("   3. Cross-Exam Sheet    : CrossExam_CheatSheet_CASE-2026-GAMMA.md")
    print("=================================================================\n")


if __name__ == "__main__":
    reset_and_seed_database()
    run_audit_engine()
    generate_reports()
    print_summary()
