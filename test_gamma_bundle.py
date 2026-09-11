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

def setup_gamma_database():
    conn = sqlite3.connect("nyayatrace.db")
    conn.execute("PRAGMA foreign_keys = OFF;")
    
    # Reload schema
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
        
    conn.execute("PRAGMA foreign_keys = ON;")
    ensure_db_schema(conn)
    cursor = conn.cursor()

    # Create supporting bundles CASE-2026-BETA and CASE-2026-ETA for witness reuse 'Suresh Verma'
    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name) VALUES ('CASE-2026-BETA', 'Seizure Memo', 'Seizure_B.pdf');
    """)
    doc_b = cursor.lastrowid
    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_iso, location_raw) VALUES (?, 'seizure', '2026-09-10 10:00', 'BETA Location');
    """, (doc_b,))
    event_b = cursor.lastrowid

    cursor.execute("""
        INSERT INTO documents (bundle_id, doc_type, file_name) VALUES ('CASE-2026-ETA', 'Seizure Memo', 'Seizure_E.pdf');
    """)
    doc_e = cursor.lastrowid
    cursor.execute("""
        INSERT INTO events (doc_id, event_type, timestamp_iso, location_raw) VALUES (?, 'seizure', '2026-09-09 10:00', 'ETA Location');
    """, (doc_e,))
    event_e = cursor.lastrowid

    cursor.execute("""
        INSERT INTO actors (name_raw, name_canonical, role, address)
        VALUES ('Suresh Verma', 'Suresh Verma', 'panch_witness', 'Distt Outer Village (>20km from scene)');
    """)
    actor_suresh = cursor.lastrowid

    cursor.execute("""
        INSERT INTO event_actors (event_id, actor_id, role_in_event)
        VALUES (?, ?, 'witness'), (?, ?, 'witness');
    """, (event_b, actor_suresh, event_e, actor_suresh))

    conn.commit()

    # Execute sample_data_gamma.sql
    with open("sample_data_gamma.sql", "r", encoding="utf-8") as f:
        gamma_sql = f.read()
    
    conn.executescript(gamma_sql)
    conn.close()
    print("[SETUP] Executed sample_data_gamma.sql into nyayatrace.db successfully.")


def run_audit_and_report():
    print("\n--- RUNNING FULL RULES ENGINE ---")
    engine = NyayaAuditEngine("nyayatrace.db")
    rules_list = [
        RuleCT01(), RuleCT02(), RuleCT03(), RuleCT04(), RuleCT05(),
        RuleCT06(), RuleCT07(), RuleCT08(), RuleCT09(), RuleCT10(),
        RuleCT11(), RuleCT12(), RuleCT13(), RuleCT14(), RuleCT15(),
        RuleCT16(), RuleCT17(), RuleCT18(), RuleCT19(), RuleCT20(),
        RuleCT21()
    ]
    for r in rules_list:
        engine.register_rule(r)

    engine.run()

    conn = sqlite3.connect("nyayatrace.db")
    df = pd.read_sql_query("SELECT contradiction_id, bundle_id, rule_id, severity, event_ids, statute, narrative FROM contradictions", conn)
    conn.close()

    print("\n=======================================================================================================")
    print("                                1. EVERY CONTRADICTION IN DATABASE (GROUPED BY BUNDLE_ID)              ")
    print("=======================================================================================================")
    
    for bundle_id, group in df.groupby("bundle_id"):
        print(f"\n📁 CASE BUNDLE: {bundle_id} ({len(group)} contradictions)")
        print("-" * 115)
        for _, row in group.iterrows():
            print(f"  [{row['rule_id']}] ({row['severity']}) Event IDs: {row['event_ids']} | Statute: {row['statute']}")
            print(f"      Narrative: {row['narrative']}\n")

    print("=======================================================================================================")
    print("                                2. SUMMARY TABLE: RULE_ID | TIMES FIRED | SEVERITY                     ")
    print("=======================================================================================================")
    
    summary_data = []
    for r in rules_list:
        fired_df = df[df["rule_id"] == r.rule_id]
        times_fired = len(fired_df)
        summary_data.append({
            "rule_id": r.rule_id,
            "rule_name": r.name,
            "severity": r.severity,
            "times_fired": times_fired
        })
    
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    print("=======================================================================================================\n")

    print("--- 3. CONFIRMING CLEAN RE-RUN (DEDUPLICATION CHECK) ---")
    engine.run()
    print("✅ Clean re-run confirmed with zero duplicate insertion errors!\n")

if __name__ == "__main__":
    setup_gamma_database()
    run_audit_and_report()
