import sqlite3
import os
import rules
import ingest

DB_PATH = "nyayatrace.db"

def reset_and_reseed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Clear old documents and events for BUNDLE_REALISTIC_TEST and uploaded bundles
    cur.execute("DELETE FROM contradictions WHERE bundle_id NOT IN ('CASE-2026-GAMMA', 'CASE-2026-DELTA')")
    cur.execute("DELETE FROM documents WHERE bundle_id NOT IN ('CASE-2026-GAMMA', 'CASE-2026-DELTA')")
    conn.commit()
    conn.close()

    # 2. Re-ingest BUNDLE_REALISTIC_TEST
    if os.path.exists("realistic_test_fir_seizure.png"):
        print("Re-ingesting BUNDLE_REALISTIC_TEST (State vs. Rajesh Sharma)...")
        ingest.ingest_bundle("realistic_test_fir_seizure.png", bundle_id="BUNDLE_REALISTIC_TEST")

    # 3. Re-ingest new trial court bundle
    if os.path.exists("new_trial_court_bundle_2026.pdf"):
        print("Re-ingesting CASE-2026-DELHI-NDPS...")
        ingest.ingest_bundle("new_trial_court_bundle_2026.pdf", bundle_id="CASE-2026-DELHI-NDPS")

    # 4. Run full audit across all bundles
    print("Running full audit engine...")
    engine = rules.NyayaAuditEngine(DB_PATH)
    engine.run()
    print("Reset and reseed complete!")

if __name__ == "__main__":
    reset_and_reseed()
