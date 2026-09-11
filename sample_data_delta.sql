-- sample_data_delta.sql: Synthetic Test Case Bundle 'CASE-2026-DELTA'
-- Specifically constructed to trigger CT-02 (Physical Impossibility) & CT-05 (IO Bilocation)

PRAGMA foreign_keys = ON;

-- 1. Insert Search Document & Event A in Delhi for CASE-2026-DELTA
INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, search_reasons_recorded, videography_present)
VALUES ('CASE-2026-DELTA', 'Search Memo', 'Search_Delhi_KarolBagh.pdf', 2, 0.99, 1, 1);

INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
VALUES (last_insert_rowid(), 'search', '20-09-2026 10:00', '2026-09-20 10:00', 'Police Station A, Karol Bagh, Delhi', 28.6519, 77.1909, 'Search operation at Karol Bagh', 1);

-- 2. Insert Seizure Document & Event B in Kanpur for CASE-2026-DELTA (45 minutes later!)
INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, search_reasons_recorded, videography_present)
VALUES ('CASE-2026-DELTA', 'Seizure Memo', 'Seizure_Kanpur_Railway.pdf', 3, 0.98, 1, 1);

INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
VALUES (last_insert_rowid(), 'seizure', '20-09-2026 10:45', '2026-09-20 10:45', 'Railway Station, Kanpur', 26.4499, 80.3319, 'Seizure at Kanpur Railway Station', 1);

INSERT INTO seizures (event_id, item_desc, quantity, unit, seal_id)
VALUES (last_insert_rowid(), 'Recovered Items Package', 2.0, 'kg', 'SEAL-KANPUR-999');

-- 3. Ensure IO Actor 'R.K. Sharma' exists
INSERT INTO actors (name_raw, name_canonical, role, address)
SELECT 'R.K. Sharma', 'R.K. Sharma', 'IO', 'PS Connaught Place, New Delhi'
WHERE NOT EXISTS (SELECT 1 FROM actors WHERE name_canonical = 'R.K. Sharma');

-- 4. Ensure non-IO Panch Witness 'Vikram Malhotra' exists
INSERT INTO actors (name_raw, name_canonical, role, address)
SELECT 'Vikram Malhotra', 'Vikram Malhotra', 'panch_witness', 'Local Market Shop, Delhi'
WHERE NOT EXISTS (SELECT 1 FROM actors WHERE name_canonical = 'Vikram Malhotra');

-- Link IO R.K. Sharma to both Event A and Event B
INSERT INTO event_actors (event_id, actor_id, role_in_event)
SELECT e.event_id, a.actor_id, 'IO'
FROM events e
JOIN documents d ON e.doc_id = d.doc_id
JOIN actors a ON a.name_canonical = 'R.K. Sharma'
WHERE d.bundle_id = 'CASE-2026-DELTA';

-- Link Non-IO Vikram Malhotra to both Event A and Event B
INSERT INTO event_actors (event_id, actor_id, role_in_event)
SELECT e.event_id, a.actor_id, 'witness'
FROM events e
JOIN documents d ON e.doc_id = d.doc_id
JOIN actors a ON a.name_canonical = 'Vikram Malhotra'
WHERE d.bundle_id = 'CASE-2026-DELTA';
