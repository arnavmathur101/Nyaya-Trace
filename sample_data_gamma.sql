-- sample_data_gamma.sql: Synthetic Test Case Bundle 'CASE-2026-GAMMA'
-- Specifically constructed to trigger CT-01, CT-03, CT-04, CT-07, CT-12, CT-13, CT-14, CT-15, CT-16, CT-17, CT-18, CT-19

PRAGMA foreign_keys = ON;

-- 1. Insert FIR Document for CASE-2026-GAMMA
INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, consent_memo_present, sample_certification_present, search_reasons_recorded, videography_present)
VALUES ('CASE-2026-GAMMA', 'FIR', 'FIR_Gamma.pdf', 3, 0.98, 0, 0, 0, 0);

-- 2. Insert FIR Registration Event (at 18:00 PM) with sections_invoked = '20(b)'
INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number, sections_invoked)
VALUES (last_insert_rowid(), 'fir_registration', '11-09-2026 18:00', '2026-09-11 18:00', 'PS Crime Branch', 28.6139, 77.2090, 'FIR Lodged under Section 20(b) NDPS', 1, '20(b)');

-- 3. Insert Seizure Document 1 (at 10:00 AM — BEFORE FIR -> triggers CT-01)
-- consent_memo_present=0 -> CT-12, sample_certification_present=0 -> CT-13, search_reasons_recorded=0 -> CT-14, videography_present=0 -> CT-19
INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, consent_memo_present, sample_certification_present, search_reasons_recorded, videography_present)
VALUES ('CASE-2026-GAMMA', 'Panchnama', 'Panchnama_Gamma_Seizure1.pdf', 4, 0.95, 0, 0, 0, 0);

-- 4. Insert Seizure Event 1
INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
VALUES (last_insert_rowid(), 'seizure', '11-09-2026 10:00', '2026-09-11 10:00', 'Interstate Bus Terminal', 28.6667, 77.2333, 'Seizure of contraband narcotics package', 1);

-- Insert Seizure item record (Quantity: 10.0 kg)
INSERT INTO seizures (event_id, item_desc, quantity, unit, seal_id)
VALUES (last_insert_rowid(), 'Contraband Narcotics Package', 10.0, 'kg', 'SEAL-GAMMA-101');

-- 5. Insert Seizure Document 2 (Quantity mismatch: 4.0 kg -> triggers CT-04)
INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence, consent_memo_present, sample_certification_present, search_reasons_recorded, videography_present)
VALUES ('CASE-2026-GAMMA', 'Seizure Verification Memo', 'Panchnama_Gamma_Seizure2.pdf', 2, 0.96, 0, 0, 0, 0);

INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, lat, lon, action, page_number)
VALUES (last_insert_rowid(), 'seizure', '11-09-2026 12:00', '2026-09-11 12:00', 'Station Vault', 28.6667, 77.2333, 'Secondary Seizure Verification', 1);

INSERT INTO seizures (event_id, item_desc, quantity, unit, seal_id)
VALUES (last_insert_rowid(), 'Contraband Narcotics Package', 4.0, 'kg', 'SEAL-GAMMA-101');

-- 6. Ensure Panch Witness 'Suresh Verma' exists and link ONLY 1 witness -> triggers CT-03, CT-07, CT-15 (reused across 3+ bundles)
INSERT INTO actors (name_raw, name_canonical, role, address)
SELECT 'Suresh Verma', 'Suresh Verma', 'panch_witness', 'Distt Outer Village (>20km from scene)'
WHERE NOT EXISTS (SELECT 1 FROM actors WHERE name_canonical = 'Suresh Verma');

INSERT INTO event_actors (event_id, actor_id, role_in_event)
SELECT e.event_id, a.actor_id, 'witness'
FROM events e
JOIN documents d ON e.doc_id = d.doc_id
JOIN actors a ON a.name_canonical = 'Suresh Verma'
WHERE d.bundle_id = 'CASE-2026-GAMMA' AND e.event_type = 'seizure' AND e.timestamp_iso = '2026-09-11 10:00';

-- 7. Insert Arrest Event on 01-05-2026 08:00
INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
VALUES ('CASE-2026-GAMMA', 'Arrest Memo', 'Arrest_Gamma.pdf', 2, 0.99);

INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number)
VALUES (last_insert_rowid(), 'arrest', '01-05-2026 08:00', '2026-05-01 08:00', 'Suspect Hideout', 'Accused Arrested', 1);

-- 8. Insert Chargesheet Document on 15-08-2026 10:00 (106 days after arrest > 90 days limit -> triggers CT-16)
-- Chargesheet event sections_invoked = '20(b),29' (Section 29 added -> triggers CT-17)
INSERT INTO documents (bundle_id, doc_type, file_name, page_count, ocr_confidence)
VALUES ('CASE-2026-GAMMA', 'Chargesheet', 'Chargesheet_Gamma.pdf', 12, 0.98);

INSERT INTO events (doc_id, event_type, timestamp_raw, timestamp_iso, location_raw, action, page_number, sections_invoked)
VALUES (last_insert_rowid(), 'chargesheet', '15-08-2026 10:00', '2026-08-15 10:00', 'Session Court', 'Chargesheet filed', 1, '20(b),29');
