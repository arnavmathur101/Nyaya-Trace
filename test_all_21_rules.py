import sqlite3
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

from rules import (
    NyayaAuditEngine, ensure_db_schema,
    RuleCT01, RuleCT02, RuleCT03, RuleCT04, RuleCT05,
    RuleCT06, RuleCT07, RuleCT08, RuleCT09, RuleCT10,
    RuleCT11, RuleCT12, RuleCT13, RuleCT14, RuleCT15,
    RuleCT16, RuleCT17, RuleCT18, RuleCT19, RuleCT20,
    RuleCT21
)

def seed_complete_21_rules_database():
    conn = sqlite3.connect("nyayatrace.db")
    conn.execute("PRAGMA foreign_keys = OFF;")
    
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
        
    conn.execute("PRAGMA foreign_keys = ON;")
    ensure_db_schema(conn)
    cursor = conn.cursor()

    # ==========================================
    # BUNDLE 1: CASE-2026-ALPHA (Triggers CT-01, CT-06, CT-07)
    # ==========================================
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-ALPHA', 'FIR', 'FIR_Alpha.pdf', 3, 0.96);
    """)
    doc_fir_a = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number, sections_invoked)
        VALUES (?, 'fir_registration', '11-09-2026 18:00', '2026-09-11 18:00', 'PS Connaught Place', 28.6315, 77.2167, 'FIR Lodged', 1, 'IPC 379');
    """, (doc_fir_a,))

    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, search_reasons_recorded, videography_present)
        VALUES ('CASE-2026-ALPHA', 'Panchnama', 'Panchnama_Alpha.pdf', 4, 0.94, 1, 1);
    """)
    doc_seizure_a = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
        VALUES (?, 'seizure', '11-09-2026 11:00', '2026-09-11 11:00', 'Pahar Ganj Shop', 28.6448, 77.2167, 'Seizure of cash', 2);
    """, (doc_seizure_a,))
    event_seizure_a = cursor.lastrowid

    cursor.execute("""
        INSERT INTO actors (name_raw, name_canonical, role, address)
        VALUES ('Ramesh Kumar', 'Ramesh Kumar', 'panch_witness', 'Pahar Ganj Local Shop 5');
    """)
    actor_w1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO event_actors (event_id, actor_id, role_in_event)
        VALUES (?, ?, 'witness');
    """, (event_seizure_a, actor_w1))

    # ==========================================
    # BUNDLE 2: CASE-2026-BETA (Triggers CT-03, CT-04)
    # ==========================================
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, search_reasons_recorded, videography_present)
        VALUES ('CASE-2026-BETA', 'Seizure Memo', 'Seizure_1.pdf', 2, 0.98, 1, 1);
    """)
    doc_b1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
        VALUES (?, 'seizure', '11-09-2026 14:00', '2026-09-11 14:00', 'Sector 15, Noida', 28.5800, 77.3178, 'Primary Seizure', 1);
    """, (doc_b1,))
    event_b1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO seizures (event_id, item_desc, quantity, unit, seal_id)
        VALUES (?, 'Contraband Package A', 5.0, 'kg', 'SEAL-777');
    """, (event_b1,))

    # Repeat witness 'Suresh Verma' (Bundle 2)
    cursor.execute("""
        INSERT INTO actors (name_raw, name_canonical, role, address)
        VALUES ('Suresh Verma', 'Suresh Verma', 'panch_witness', 'Distt Outer Village (>20km from scene)');
    """)
    actor_w2 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO event_actors (event_id, actor_id, role_in_event)
        VALUES (?, ?, 'witness');
    """, (event_b1, actor_w2))

    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, search_reasons_recorded, videography_present)
        VALUES ('CASE-2026-BETA', 'Seizure Memo', 'Seizure_2.pdf', 2, 0.97, 1, 1);
    """)
    doc_b2 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
        VALUES (?, 'seizure', '11-09-2026 15:30', '2026-09-11 15:30', 'Malkhana Vault', 28.5800, 77.3178, 'Malkhana Entry', 1);
    """, (doc_b2,))
    event_b2 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO seizures (event_id, item_desc, quantity, unit, seal_id)
        VALUES (?, 'Contraband Package A', 4.2, 'kg', 'SEAL-777');
    """, (event_b2,))

    # ==========================================
    # BUNDLE 3: CASE-2026-GAMMA (Triggers CT-02, CT-05)
    # ==========================================
    cursor.execute("""
        INSERT INTO actors (name_raw, name_canonical, role, address)
        VALUES ('Rohan Gupta', 'Rohan Gupta', 'Witness', 'Civil Lines, Delhi');
    """)
    actor_rohan = cursor.lastrowid

    cursor.execute("""
        INSERT INTO actors (name_raw, name_canonical, role, address)
        VALUES ('Inspector V.K. Singh', 'Inspector V.K. Singh', 'IO', 'Police HQ, Delhi');
    """)
    actor_io = cursor.lastrowid

    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-GAMMA', 'Search Memo', 'Search_Delhi.pdf', 2, 0.99);
    """)
    doc_g1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
        VALUES (?, 'search', '11-09-2026 14:00', '2026-09-11 14:00', 'Delhi Suburb', 28.6448, 77.2167, 'Search conducted in Delhi', 1);
    """, (doc_g1,))
    event_g1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO event_actors (event_id, actor_id, role_in_event)
        VALUES (?, ?, 'witness'), (?, ?, 'IO');
    """, (event_g1, actor_rohan, event_g1, actor_io))

    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-GAMMA', 'Search Memo', 'Search_Agra.pdf', 2, 0.99);
    """)
    doc_g2 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
        VALUES (?, 'search', '11-09-2026 14:30', '2026-09-11 14:30', 'Agra Highway', 27.1767, 78.0081, 'Search conducted in Agra', 1);
    """, (doc_g2,))
    event_g2 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO event_actors (event_id, actor_id, role_in_event)
        VALUES (?, ?, 'witness');
    """, (event_g2, actor_rohan))

    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-GAMMA', 'GD Entry', 'GD_Entry_Gurugram.pdf', 1, 0.95);
    """)
    doc_g3 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
        VALUES (?, 'gd_entry', '11-09-2026 14:15', '2026-09-11 14:15', 'Gurugram PS', 28.4595, 77.0266, 'GD Entry by IO', 1);
    """, (doc_g3,))
    event_g3 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO event_actors (event_id, actor_id, role_in_event)
        VALUES (?, ?, 'IO');
    """, (event_g3, actor_io))

    # ==========================================
    # BUNDLE 4: CASE-2026-DELTA (Triggers CT-08, CT-09, CT-10, CT-11, CT-14, CT-19)
    # ==========================================
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, search_reasons_recorded, videography_present)
        VALUES ('CASE-2026-DELTA', 'Seizure Memo', 'Seizure_Delta.pdf', 2, 0.98, 0, 0);
    """)
    doc_d1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number)
        VALUES (?, 'seizure', '01-09-2026 09:00', '2026-09-01 09:00', 'Warehouse 12', 'Seizure of suspected narcotics', 1);
    """, (doc_d1,))
    event_d1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO seizures (event_id, item_desc, quantity, unit, seal_id)
        VALUES (?, 'Seized Opium Sample', 1.0, 'kg', 'SEAL-DELTA-ORIGINAL');
    """, (event_d1,))

    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-DELTA', 'FSL Forwarding', 'FSL_Forwarding_Delta.pdf', 1, 0.95);
    """)
    doc_d2 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number)
        VALUES (?, 'fsl_forwarding', '12-09-2026 10:00', '2026-09-12 10:00', 'FSL Forensic Lab', 'Sample forwarded to FSL', 1);
    """, (doc_d2,))
    event_d2 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO seizures (event_id, item_desc, quantity, unit, seal_id)
        VALUES (?, 'Seized Opium Sample', 1.0, 'kg', 'SEAL-DELTA-TAMPERED');
    """, (event_d2,))

    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-DELTA', 'Arrest Memo', 'Arrest_Delta.pdf', 2, 0.99);
    """)
    doc_d3 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number)
        VALUES (?, 'arrest', '10-09-2026 08:00', '2026-09-10 08:00', 'Suspect House', 'Accused Arrested', 1);
    """, (doc_d3,))

    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-DELTA', 'Remand Application', 'Remand_Delta.pdf', 1, 0.95);
    """)
    doc_d4 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
        VALUES (?, 'magistrate_production', '11-09-2026 14:00', '2026-09-11 14:00', 'District Court', 28.6300, 77.2200, 'Produced before Magistrate', 1);
    """, (doc_d4,))

    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-DELTA', 'MLC Report', 'MLC_Delta.pdf', 1, 0.97);
    """)
    doc_d5 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
        VALUES (?, 'medical_examination', '11-09-2026 16:00', '2026-09-11 16:00', 'Civil Hospital', 28.6300, 77.2200, 'Medical Examination', 1);
    """, (doc_d5,))

    # ==========================================
    # BUNDLE 5: CASE-2026-EPSILON (Triggers CT-12, CT-13)
    # ==========================================
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, consent_memo_present, sample_certification_present)
        VALUES ('CASE-2026-EPSILON', 'NDPS Seizure Memo', 'NDPS_Seizure.pdf', 3, 0.96, 0, 0);
    """)
    doc_e1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number)
        VALUES (?, 'seizure', '05-09-2026 12:00', '2026-09-05 12:00', 'Highway Checkpoint', 'NDPS Heroin Contraband Seizure', 1);
    """, (doc_e1,))
    event_e1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO seizures (event_id, item_desc, quantity, unit, seal_id)
        VALUES (?, 'NDPS Heroin Packet', 6.5, 'kg', 'SEAL-EPSILON-1');
    """, (event_e1,))

    # ==========================================
    # BUNDLE 6: CASE-2026-ZETA (Triggers CT-15, CT-16, CT-17, CT-18, CT-20, CT-21)
    # ==========================================
    # FIR with IPC 307
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-ZETA', 'FIR', 'FIR_Zeta.pdf', 2, 0.99);
    """)
    doc_z1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number, sections_invoked)
        VALUES (?, 'fir_registration', '01-05-2026 10:00', '2026-05-01 10:00', 'PS West', 'FIR registered under IPC 307', 1, 'IPC 307');
    """, (doc_z1,))

    # Arrest on 01-05-2026 11:00
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-ZETA', 'Arrest Memo', 'Arrest_Zeta.pdf', 2, 0.98);
    """)
    doc_z2 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number)
        VALUES (?, 'arrest', '01-05-2026 11:00', '2026-05-01 11:00', 'Zeta Residence', 'Accused Arrested', 1);
    """, (doc_z2,))

    # Search Memo with missing malkhana -> CT-18, reasons=1, video=1
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, search_reasons_recorded, videography_present)
        VALUES ('CASE-2026-ZETA', 'Search & Seizure Memo', 'Search_Zeta.pdf', 3, 0.97, 1, 1);
    """)
    doc_z3 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number)
        VALUES (?, 'seizure', '01-05-2026 12:00', '2026-05-01 12:00', 'Zeta Residence Premises', 'Search and recovery of weapon', 1);
    """, (doc_z3,))
    event_z3 = cursor.lastrowid

    # Stock Witness Suresh Verma (actor_w2) re-appears in ZETA (Bundle #2)
    cursor.execute("""
        INSERT INTO event_actors (event_id, actor_id, role_in_event)
        VALUES (?, ?, 'witness');
    """, (event_z3, actor_w2))

    # Statement of accused in Tamil, accused did NOT understand -> CT-20
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, statement_language, accused_understood_language)
        VALUES ('CASE-2026-ZETA', 'Confession Statement', 'Statement_Zeta.pdf', 2, 0.95, 'Tamil', 0);
    """)
    doc_z4 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number)
        VALUES (?, 'accused_statement', '02-05-2026 15:00', '2026-05-02 15:00', 'PS West Interrogation Room', 'Confession recorded by IO', 1);
    """, (doc_z4,))

    # TIP identification parade on 25-05-2026 (24 days after arrest -> CT-21)
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-ZETA', 'TIP Report', 'TIP_Zeta.pdf', 2, 0.96);
    """)
    doc_z5 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number)
        VALUES (?, 'tip_parade', '25-05-2026 11:00', '2026-05-25 11:00', 'Central Jail Tihar', 'Test Identification Parade', 1);
    """, (doc_z5,))

    # Chargesheet filed on 15-08-2026 (106 days after arrest -> CT-16), sections altered to IPC 307, IPC 302, IPC 120B -> CT-17
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-ZETA', 'Chargesheet', 'Chargesheet_Zeta.pdf', 15, 0.99);
    """)
    doc_z6 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number, sections_invoked)
        VALUES (?, 'chargesheet', '15-08-2026 10:00', '2026-08-15 10:00', 'Magistrate Court', 'Chargesheet Filed', 1, 'IPC 307, IPC 302, IPC 120B');
    """, (doc_z6,))

    # ==========================================
    # BUNDLE 7: CASE-2026-ETA (Triggers CT-15 stock witness Suresh Verma for 3rd bundle!)
    # ==========================================
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
        VALUES ('CASE-2026-ETA', 'Panchnama', 'Panchnama_Eta.pdf', 2, 0.95);
    """)
    doc_eta1 = cursor.lastrowid

    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number)
        VALUES (?, 'seizure', '01-09-2026 10:00', '2026-09-01 10:00', 'Eta Location', 'Seizure Operation', 1);
    """, (doc_eta1,))
    event_eta1 = cursor.lastrowid

    # Stock Witness Suresh Verma (actor_w2) appears in ETA (Bundle #3 -> CT-15 trigger!)
    cursor.execute("""
        INSERT INTO event_actors (event_id, actor_id, role_in_event)
        VALUES (?, ?, 'witness');
    """, (event_eta1, actor_w2))

    conn.commit()
    conn.close()
    print("[SETUP] Seeded database with complete test scenarios for ALL 21 RULES.")

def run_full_21_rules_audit():
    engine = NyayaAuditEngine("nyayatrace.db")
    all_rules = [
        RuleCT01(), RuleCT02(), RuleCT03(), RuleCT04(), RuleCT05(),
        RuleCT06(), RuleCT07(), RuleCT08(), RuleCT09(), RuleCT10(),
        RuleCT11(), RuleCT12(), RuleCT13(), RuleCT14(), RuleCT15(),
        RuleCT16(), RuleCT17(), RuleCT18(), RuleCT19(), RuleCT20(),
        RuleCT21()
    ]
    
    for r in all_rules:
        engine.register_rule(r)

    print("\n--- RUNNING COMPLETE AUDIT ENGINE (ALL 21 RULES) ---")
    engine.run()

    conn = sqlite3.connect("nyayatrace.db")
    df = pd.read_sql_query("SELECT contradiction_id, bundle_id, rule_id, severity, event_ids, statute, narrative FROM contradictions", conn)
    conn.close()

    print("\n========================================================================================================================================")
    print("                                                 ALL CONTRADICTIONS TABLE CONTENT (21 RULES)                                           ")
    print("========================================================================================================================================")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', None)
    print(df.to_string(index=False))
    print("========================================================================================================================================\n")

    # 1. Severity Breakdown
    print("--------------------------------------------------")
    print("      SUMMARY OF CONTRADICTIONS BY SEVERITY       ")
    print("--------------------------------------------------")
    severity_counts = df['severity'].value_counts().to_dict()
    for sev in ['CRITICAL', 'HIGH', 'MEDIUM']:
        print(f"  - {sev}: {severity_counts.get(sev, 0)}")

    # 2. Rule evaluation stats (matching vs zero-match rules)
    matched_rule_ids = set(df['rule_id'].unique())
    zero_match_rules = [r for r in all_rules if r.rule_id not in matched_rule_ids]

    print("\n--------------------------------------------------")
    print("             RULE EVALUATION RESULTS              ")
    print("--------------------------------------------------")
    print(f"Total Rules Executed: {len(all_rules)}")
    print(f"Total Contradictions Detected: {len(df)}")
    
    if zero_match_rules:
        print("\nRules with ZERO matches:")
        for r in zero_match_rules:
            print(f"  - [{r.rule_id}] {r.name}")
    else:
        print("\n🎉 ALL 21 RULES TRIGGERED SUCCESSFULLY WITH AT LEAST 1 VERIFIED MATCH!")
    print("--------------------------------------------------\n")

if __name__ == "__main__":
    seed_complete_21_rules_database()
    run_full_21_rules_audit()
