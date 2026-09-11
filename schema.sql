-- NyayaTrace Audit — Database Schema (v0.1)
-- SQLite compatible

PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS contradiction_actors;
DROP TABLE IF EXISTS seizure_items;
DROP TABLE IF EXISTS contradictions;
DROP TABLE IF EXISTS seizures;
DROP TABLE IF EXISTS event_actors;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS actors;
DROP TABLE IF EXISTS documents;

PRAGMA foreign_keys = ON;

-- 1. Documents table: har uploaded file ki entry
CREATE TABLE documents (
    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bundle_id TEXT NOT NULL,          -- kaunse case bundle ka hissa hai
    doc_type TEXT NOT NULL,           -- FIR, Panchnama, Seizure Memo, GD Entry, MLC, Chargesheet
    file_name TEXT,
    page_count INTEGER,
    ocr_confidence REAL,              -- 0.0 to 1.0
    consent_memo_present INTEGER,     -- 0/1/NULL (CT-12)
    sample_certification_present INTEGER, -- 0/1/NULL (CT-13)
    search_reasons_recorded INTEGER,  -- 0/1/NULL (CT-14)
    videography_present INTEGER,      -- 0/1/NULL (CT-19)
    statement_language TEXT,          -- Language string (CT-20)
    accused_understood_language INTEGER, -- 0/1/NULL (CT-20)
    uploaded_at TEXT DEFAULT (datetime('now'))
);

-- 2. Actors table: sab log — police, witness, accused
CREATE TABLE actors (
    actor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_raw TEXT NOT NULL,           -- jaisa document mein likha tha
    name_canonical TEXT,              -- normalized/deduplicated naam
    role TEXT,                        -- IO, panch_witness, accused, magistrate
    address TEXT
);

-- 3. Events table: har date/time/location jo documents se nikla
CREATE TABLE events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id INTEGER NOT NULL,
    event_type TEXT,                  -- fir_registration, seizure, arrest, search
    timestamp_raw TEXT,               -- jaisa document mein likha tha
    timestamp_iso TEXT,               -- standardized format: YYYY-MM-DD HH:MM
    location_raw TEXT,
    lat REAL,
    lon REAL,
    action TEXT,                      -- description of what happened
    page_number INTEGER,
    bbox TEXT,                        -- "x1,y1,x2,y2" for UI highlighting
    sections_invoked TEXT,            -- comma-separated penal sections (e.g., "IPC 307, 34") (CT-17)
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
);

-- 4. Event-Actor link table: kaun kaunse event mein involved tha, kis role mein
CREATE TABLE event_actors (
    event_id INTEGER NOT NULL,
    actor_id INTEGER NOT NULL,
    role_in_event TEXT,               -- signatory, witness, subject
    PRIMARY KEY (event_id, actor_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (actor_id) REFERENCES actors(actor_id)
);

-- 5. Seizures table: kya-kya saaman zabt hua
CREATE TABLE seizures (
    seizure_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    item_desc TEXT,
    quantity REAL,
    unit TEXT,
    seal_id TEXT,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- 6. Contradictions table: jo gadbadiyan mili
CREATE TABLE contradictions (
    contradiction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bundle_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,            -- CT-01, CT-02, etc.
    severity TEXT,                    -- CRITICAL, HIGH, MEDIUM
    event_ids TEXT,                   -- comma-separated event_id list involved
    narrative TEXT,                   -- human-readable explanation
    statute TEXT,                     -- legal reference (e.g. "Sec 154 CrPC")
    created_at TEXT DEFAULT (datetime('now'))
);
