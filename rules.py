"""
NyayaTrace Enhanced Legal Audit Rules Engine (rules.py)
Implements 21 comprehensive, deterministic, legal audit rules under IPC / CrPC / BNSS / NDPS Act
with precise statutory analysis, precedent citations, time-delta math, and case-law backing.
"""

import math
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

# Configurable Threshold Constants
FSL_FORWARDING_DELAY_DAYS_THRESHOLD = 3  # NCB Standing Order 1/88 72-hour limit
COMMERCIAL_QUANTITY_THRESHOLDS = {
    "heroin": 0.25,      # 250 grams (0.25 kg)
    "ganja": 20.0,       # 20 kg
    "opium": 2.5,        # 2.5 kg
    "charas": 1.0,       # 1.0 kg
    "cocaine": 0.10,     # 100 grams (0.10 kg)
    "meth": 0.05,        # 50 grams
    "contraband": 0.25   # Default commercial threshold
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle (straight-line) distance between two points
    on Earth using the Haversine formula. Returns distance in kilometers.
    """
    R = 6371.0  # Radius of Earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return R * c


def ensure_db_schema(conn: sqlite3.Connection):
    """
    Applies non-destructive ALTER TABLE commands to add missing columns.
    """
    cursor = conn.cursor()
    doc_columns = [
        ("consent_memo_present", "INTEGER"),
        ("sample_certification_present", "INTEGER"),
        ("search_reasons_recorded", "INTEGER"),
        ("videography_present", "INTEGER"),
        ("statement_language", "TEXT"),
        ("accused_understood_language", "INTEGER")
    ]
    for col_name, col_type in doc_columns:
        try:
            cursor.execute(f"ALTER TABLE documents ADD COLUMN {col_name} {col_type};")
        except sqlite3.OperationalError:
            pass  # Column already exists

    try:
        cursor.execute("ALTER TABLE events ADD COLUMN sections_invoked TEXT;")
    except sqlite3.OperationalError:
        pass

    conn.commit()


class BaseRule(ABC):
    """
    Abstract Base Class for NyayaTrace Audit Rules.
    """
    rule_id: str
    name: str
    severity: str
    statute: str

    @abstractmethod
    def evaluate(
        self,
        events_df: pd.DataFrame,
        docs_df: pd.DataFrame,
        actors_df: Optional[pd.DataFrame] = None,
        event_actors_df: Optional[pd.DataFrame] = None,
        seizures_df: Optional[pd.DataFrame] = None
    ) -> List[Dict[str, Any]]:
        pass


class RuleCT01(BaseRule):
    """RULE CT-01 — Seizure Timestamp Prior to FIR Registration"""
    rule_id = "CT-01"
    name = "Seizure Timestamp Prior to FIR Registration"
    severity = "CRITICAL"
    statute = "Sec 154 CrPC / Sec 173 BNSS; Lalita Kumari v. Govt of U.P. (2014) 2 SCC 1"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        df["dt"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            fir_events = bundle_group[(bundle_group["event_type"].str.lower().isin(["fir", "fir_registration"])) & (bundle_group["event_type"].str.lower() != "seizure")]
            seizure_events = bundle_group[(bundle_group["event_type"].str.lower() == "seizure") | (bundle_group["doc_type"].str.upper().str.contains("SEIZURE|PANCHNAMA"))]

            if fir_events.empty or seizure_events.empty:
                continue

            earliest_fir = fir_events.sort_values("dt").iloc[0]
            fir_dt = earliest_fir["dt"]
            fir_event_id = earliest_fir["event_id"]
            fir_time_str = earliest_fir.get("timestamp_iso", str(fir_dt))

            for _, seizure_row in seizure_events.iterrows():
                seizure_dt = seizure_row["dt"]
                if pd.notnull(seizure_dt) and pd.notnull(fir_dt) and seizure_dt < fir_dt:
                    diff_mins = (fir_dt - seizure_dt).total_seconds() / 60.0
                    hours = int(diff_mins // 60)
                    mins = int(diff_mins % 60)
                    time_gap_str = f"{hours} hours {mins} mins" if hours > 0 else f"{mins} mins"
                    
                    seizure_time_str = seizure_row.get("timestamp_iso", str(seizure_dt))
                    seizure_event_id = seizure_row["event_id"]
                    event_ids_str = f"{seizure_event_id},{fir_event_id}"
                    action_name = seizure_row.get("event_type", "seizure")

                    narrative = (
                        f"Seizure action '{action_name}' recorded at {seizure_time_str}, "
                        f"which precedes official FIR registration at {fir_time_str} by {time_gap_str}. "
                        f"Under Lalita Kumari guidelines, conducting search & recovery prior to FIR registration without a recorded preliminary inquiry invalidates the seizure."
                    )
                    contradictions.append({
                        "bundle_id": str(bundle_id),
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "event_ids": event_ids_str,
                        "narrative": narrative,
                        "statute": self.statute
                    })
        return contradictions


class RuleCT02(BaseRule):
    """RULE CT-02 — Physical Impossibility (Teleportation)"""
    rule_id = "CT-02"
    name = "Physical Impossibility (Teleportation)"
    severity = "CRITICAL"
    statute = "Sec 100 CrPC / Sec 103 BNSS; General Rules of Evidentiary Relevance"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty or actors_df is None or event_actors_df is None:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        df["dt"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            events_list = bundle_group.to_dict("records")
            n = len(events_list)
            for i in range(n):
                for j in range(i + 1, n):
                    evA, evB = events_list[i], events_list[j]
                    latA, lonA = evA.get("lat"), evA.get("lon")
                    latB, lonB = evB.get("lat"), evB.get("lon")
                    if pd.isnull(latA) or pd.isnull(lonA) or pd.isnull(latB) or pd.isnull(lonB):
                        continue

                    dtA, dtB = evA.get("dt"), evB.get("dt")
                    if pd.isnull(dtA) or pd.isnull(dtB):
                        continue

                    actorsA = set(event_actors_df[event_actors_df["event_id"] == evA["event_id"]]["actor_id"])
                    actorsB = set(event_actors_df[event_actors_df["event_id"] == evB["event_id"]]["actor_id"])
                    common_actor_ids = actorsA.intersection(actorsB)

                    if not common_actor_ids:
                        continue

                    dist_km = haversine_distance(float(latA), float(lonA), float(latB), float(lonB))
                    time_diff_hours = abs((dtB - dtA).total_seconds()) / 3600.0
                    time_diff_mins = time_diff_hours * 60.0

                    if time_diff_hours <= 0:
                        speed_kmh = 9999.0
                    else:
                        speed_kmh = dist_km / time_diff_hours

                    if dist_km > 0.5 and speed_kmh > 120.0:
                        for aid in common_actor_ids:
                            act_row = actors_df[actors_df["actor_id"] == aid]
                            act_name = act_row.iloc[0]["name_canonical"] if not act_row.empty else f"Actor #{aid}"
                            time_A_str = evA.get("timestamp_iso", str(dtA))
                            time_B_str = evB.get("timestamp_iso", str(dtB))
                            loc_A = evA["location_raw"] or "Location A"
                            loc_B = evB["location_raw"] or "Location B"
                            event_ids_str = f"{evA['event_id']},{evB['event_id']}"

                            narrative = (
                                f"Actor '{act_name}' is recorded at '{loc_A}' at {time_A_str} and at "
                                f"'{loc_B}' ({dist_km:.1f} km away) at {time_B_str} (time gap: {int(time_diff_mins)} mins). "
                                f"Calculated travel speed of {speed_kmh:.1f} km/h represents physical impossibility."
                            )
                            contradictions.append({
                                "bundle_id": str(bundle_id),
                                "rule_id": self.rule_id,
                                "severity": self.severity,
                                "event_ids": event_ids_str,
                                "narrative": narrative,
                                "statute": self.statute
                            })

        return contradictions


class RuleCT03(BaseRule):
    """RULE CT-03 — Panch Witness Ghosting & Non-Local Stock Witness"""
    rule_id = "CT-03"
    name = "Panch Witness Ghosting"
    severity = "HIGH"
    statute = "Sec 100(4) CrPC / Sec 103(4) BNSS; State of Punjab v. Baldev Singh (1999) 6 SCC 172"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty or actors_df is None or event_actors_df is None:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        seizure_events = df[(df["event_type"].str.lower() == "seizure") | (df["doc_type"].str.upper().str.contains("SEIZURE|PANCHNAMA"))]

        for _, event_row in seizure_events.iterrows():
            event_id = event_row["event_id"]
            bundle_id = event_row["bundle_id"]

            linked = event_actors_df[event_actors_df["event_id"] == event_id]
            witness_links = linked[linked["role_in_event"].str.lower().str.contains("witness", na=False)]

            for _, w_link in witness_links.iterrows():
                actor_matches = actors_df[actors_df["actor_id"] == w_link["actor_id"]]
                if actor_matches.empty:
                    continue

                actor = actor_matches.iloc[0]
                name = actor["name_canonical"] or actor["name_raw"]
                address = str(actor["address"] or "").strip()

                is_missing = not address or address.lower() in ["none", "nan", "null", "unknown", ""]
                is_far = any(indicator in address.lower() for indicator in [">20km", "20 km", "25 km", "45 km", "far", "out of station", "different district", "out of jurisdiction"])

                if is_missing:
                    narrative = f"Panch witness '{name}' has no recorded home address or identification details in the search memo, rendering the witness un-verifiable."
                    contradictions.append({
                        "bundle_id": str(bundle_id),
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "event_ids": str(event_id),
                        "narrative": narrative,
                        "statute": self.statute
                    })
                elif is_far:
                    narrative = f"Panch witness '{name}' listed address ('{address}') is located far from the search scene, violating Sec 100(4) CrPC mandate requiring independent local residents of the locality."
                    contradictions.append({
                        "bundle_id": str(bundle_id),
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "event_ids": str(event_id),
                        "narrative": narrative,
                        "statute": self.statute
                    })

        return contradictions


class RuleCT04(BaseRule):
    """RULE CT-04 — Quantity Mismatch & Commercial Threshold Shift"""
    rule_id = "CT-04"
    name = "Seized Item Quantity Mismatch"
    severity = "HIGH"
    statute = "Sec 100(5) CrPC / Sec 37 NDPS Act"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if seizures_df is None or seizures_df.empty or events_df.empty or docs_df.empty:
            return contradictions

        merged = seizures_df.merge(events_df, on="event_id", how="inner").merge(docs_df, on="doc_id", how="inner")
        if merged.empty:
            return contradictions

        merged["item_key"] = merged["item_desc"].str.lower().str.strip()

        for (bundle_id, item_key), group in merged.groupby(["bundle_id", "item_key"]):
            if len(group) < 2:
                continue

            unique_quantities = group["quantity"].dropna().unique()
            if len(unique_quantities) > 1:
                row1, row2 = group.iloc[0], group.iloc[1]
                qty1, unit1 = row1["quantity"], row1["unit"] or "kg"
                qty2, unit2 = row2["quantity"], row2["unit"] or "kg"
                item_name = row1["item_desc"]
                event_ids = f"{row1['event_id']},{row2['event_id']}"
                
                # Check commercial threshold shift
                threshold = COMMERCIAL_QUANTITY_THRESHOLDS.get("heroin", 0.25)
                is_shift = (qty1 >= threshold and qty2 < threshold) or (qty2 >= threshold and qty1 < threshold)
                
                if is_shift:
                    narrative = (
                        f"Seized contraband '{item_name}' weight shifts from {qty1} {unit1} to {qty2} {unit2} across memos. "
                        f"This discrepancy crosses the Commercial Quantity threshold ({threshold} kg), altering statutory bail eligibility under Section 37 NDPS Act."
                    )
                else:
                    narrative = f"Seized item '{item_name}' recorded as {qty1} {unit1} in search memo but {qty2} {unit2} in verification report within bundle '{bundle_id}'."

                contradictions.append({
                    "bundle_id": str(bundle_id),
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "event_ids": event_ids,
                    "narrative": narrative,
                    "statute": self.statute
                })

        return contradictions


class RuleCT05(BaseRule):
    """RULE CT-05 — IO Bilocation"""
    rule_id = "CT-05"
    name = "IO Bilocation"
    severity = "CRITICAL"
    statute = "Sec 172 CrPC / Sec 192 BNSS; Police Case Diary Regulations"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty or actors_df is None or event_actors_df is None:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        df["dt"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            events_list = bundle_group.to_dict("records")
            n = len(events_list)
            for i in range(n):
                for j in range(i + 1, n):
                    evA, evB = events_list[i], events_list[j]
                    latA, lonA = evA.get("lat"), evA.get("lon")
                    latB, lonB = evB.get("lat"), evB.get("lon")
                    if pd.isnull(latA) or pd.isnull(lonA) or pd.isnull(latB) or pd.isnull(lonB):
                        continue

                    dtA, dtB = evA.get("dt"), evB.get("dt")
                    if pd.isnull(dtA) or pd.isnull(dtB):
                        continue

                    actorsA = set(event_actors_df[event_actors_df["event_id"] == evA["event_id"]]["actor_id"])
                    actorsB = set(event_actors_df[event_actors_df["event_id"] == evB["event_id"]]["actor_id"])
                    common_actor_ids = actorsA.intersection(actorsB)

                    for aid in common_actor_ids:
                        act_row = actors_df[actors_df["actor_id"] == aid]
                        if act_row.empty:
                            continue
                        
                        actor_obj = act_row.iloc[0]
                        actor_role = str(actor_obj.get("role") or "").upper()
                        ea_row_A = event_actors_df[(event_actors_df["event_id"] == evA["event_id"]) & (event_actors_df["actor_id"] == aid)]
                        ea_role_A = str(ea_row_A.iloc[0]["role_in_event"] if not ea_row_A.empty else "").upper()

                        if "IO" in actor_role or "INVESTIGATING" in actor_role or "IO" in ea_role_A or "INVESTIGATING" in ea_role_A:
                            dist_km = haversine_distance(float(latA), float(lonA), float(latB), float(lonB))
                            time_diff_hours = abs((dtB - dtA).total_seconds()) / 3600.0
                            required_travel_hours = dist_km / 60.0

                            if dist_km > 0.5 and time_diff_hours < required_travel_hours:
                                io_name = actor_obj["name_canonical"] or actor_obj["name_raw"]
                                loc_A = evA["location_raw"] or "Location A"
                                loc_B = evB["location_raw"] or "Location B"
                                event_ids_str = f"{evA['event_id']},{evB['event_id']}"

                                narrative = (
                                    f"Investigating Officer '{io_name}' is recorded conducting proceedings at '{loc_A}' and "
                                    f"simultaneously at '{loc_B}' ({dist_km:.1f} km away) within an impossible time window. "
                                    f"This bilocation compromises the authenticity of Case Diary entries under Sec 172 CrPC."
                                )
                                contradictions.append({
                                    "bundle_id": str(bundle_id),
                                    "rule_id": self.rule_id,
                                    "severity": self.severity,
                                    "event_ids": event_ids_str,
                                    "narrative": narrative,
                                    "statute": self.statute
                                })

        return contradictions


class RuleCT06(BaseRule):
    """RULE CT-06 — GD Entry Gap"""
    rule_id = "CT-06"
    name = "GD Entry Gap"
    severity = "MEDIUM"
    statute = "Sec 44 Police Act 1861 / Sec 175 BNSS"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        df["dt"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            fir_events = bundle_group[(bundle_group["event_type"].str.lower() == "fir_registration") | (bundle_group["doc_type"].str.upper() == "FIR")]
            seizure_events = bundle_group[(bundle_group["event_type"].str.lower() == "seizure") | (bundle_group["doc_type"].str.upper().str.contains("SEIZURE|PANCHNAMA"))]

            if fir_events.empty or seizure_events.empty:
                continue

            earliest_seizure = seizure_events.sort_values("dt").iloc[0]
            earliest_fir = fir_events.sort_values("dt").iloc[0]
            seizure_dt, fir_dt = earliest_seizure["dt"], earliest_fir["dt"]

            if pd.isnull(seizure_dt) or pd.isnull(fir_dt):
                continue

            start_win, end_win = min(seizure_dt, fir_dt), max(seizure_dt, fir_dt)
            gd_entries = bundle_group[(bundle_group["doc_type"].str.upper().str.contains("GD ENTRY")) | (bundle_group["event_type"].str.lower() == "gd_entry")]
            gd_in_window = gd_entries[(gd_entries["dt"] >= start_win) & (gd_entries["dt"] <= end_win)]

            if gd_in_window.empty:
                seizure_time_str = earliest_seizure.get("timestamp_iso", str(seizure_dt))
                fir_time_str = earliest_fir.get("timestamp_iso", str(fir_dt))
                event_ids_str = f"{earliest_seizure['event_id']},{earliest_fir['event_id']}"

                narrative = (
                    f"No General Diary (GD) departure entry recorded between seizure at {seizure_time_str} "
                    f"and FIR registration at {fir_time_str} in bundle '{bundle_id}' — violating mandatory station diary recording under Sec 44 Police Act."
                )
                contradictions.append({
                    "bundle_id": str(bundle_id),
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "event_ids": event_ids_str,
                    "narrative": narrative,
                    "statute": self.statute
                })

        return contradictions


class RuleCT07(BaseRule):
    """RULE CT-07 — Missing Mandatory Independent Witness"""
    rule_id = "CT-07"
    name = "Missing Mandatory Witness"
    severity = "HIGH"
    statute = "Sec 100(4) CrPC / Sec 103(4) BNSS; Appabhai v. State of Gujarat (1988)"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty or event_actors_df is None:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        seizure_events = df[(df["event_type"].str.lower() == "seizure") | (df["doc_type"].str.upper().str.contains("SEIZURE|PANCHNAMA"))]

        for _, event_row in seizure_events.iterrows():
            event_id, bundle_id = event_row["event_id"], event_row["bundle_id"]
            linked = event_actors_df[event_actors_df["event_id"] == event_id]
            witnesses = linked[linked["role_in_event"].str.lower().str.contains("witness", na=False)]
            count = len(witnesses)

            if count < 2:
                narrative = (
                    f"Seizure event has only {count} independent witness(es) recorded. "
                    f"Sec 100(4) CrPC / Sec 103(4) BNSS mandates at least 2 independent respectable inhabitants of the locality to attest the search."
                )
                contradictions.append({
                    "bundle_id": str(bundle_id),
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "event_ids": str(event_id),
                    "narrative": narrative,
                    "statute": self.statute
                })

        return contradictions


class RuleCT08(BaseRule):
    """RULE CT-08 — Chain of Custody Break (Seal Mismatch)"""
    rule_id = "CT-08"
    name = "Chain of Custody Break (Seal Mismatch)"
    severity = "CRITICAL"
    statute = "Sec 55 NDPS Act; Gaunter Edwin Kircher v. State of Goa (1993)"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if seizures_df is None or seizures_df.empty or events_df.empty or docs_df.empty:
            return contradictions

        merged = seizures_df.merge(events_df, on="event_id", how="inner").merge(docs_df, on="doc_id", how="inner")
        if merged.empty:
            return contradictions

        merged["item_key"] = merged["item_desc"].str.lower().str.strip()

        for (bundle_id, item_key), group in merged.groupby(["bundle_id", "item_key"]):
            if len(group) < 2:
                continue

            valid_seals = group[group["seal_id"].notnull() & (group["seal_id"].str.strip() != "")]
            if len(valid_seals) >= 2:
                seal_values = valid_seals["seal_id"].unique()
                if len(seal_values) > 1:
                    row1, row2 = valid_seals.iloc[0], valid_seals.iloc[1]
                    seal_1, seal_2 = row1["seal_id"], row2["seal_id"]
                    event_ids = f"{row1['event_id']},{row2['event_id']}"

                    narrative = (
                        f"Seal ID '{seal_1}' recorded at spot seizure does not match seal ID '{seal_2}' recorded at malkhana/FSL receipt. "
                        f"This break in chain of custody creates grave suspicion of tampering under Sec 55 NDPS Act."
                    )
                    contradictions.append({
                        "bundle_id": str(bundle_id),
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "event_ids": event_ids,
                        "narrative": narrative,
                        "statute": self.statute
                    })

        return contradictions


class RuleCT09(BaseRule):
    """RULE CT-09 — 24-Hour Magistrate Production Violation"""
    rule_id = "CT-09"
    name = "24-Hour Magistrate Production Violation"
    severity = "CRITICAL"
    statute = "Article 22(2) Constitution of India; Sec 57 CrPC / Sec 58 BNSS"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        df["dt"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            arrest_events = bundle_group[(bundle_group["event_type"].str.lower() == "arrest") | (bundle_group["doc_type"].str.upper().str.contains("ARREST"))]
            if arrest_events.empty:
                continue

            prod_events = bundle_group[(bundle_group["event_type"].str.lower() == "magistrate_production") | (bundle_group["doc_type"].str.upper().str.contains("REMAND|MAGISTRATE"))]

            for _, arrest_row in arrest_events.iterrows():
                arrest_dt = arrest_row["dt"]
                arrest_event_id = arrest_row["event_id"]
                arrest_time_str = arrest_row.get("timestamp_iso", str(arrest_dt))

                if prod_events.empty:
                    narrative = f"Accused arrested at {arrest_time_str} has no recorded Magistrate production entry in bundle '{bundle_id}', establishing prima facie illegal detention under Art 22(2)."
                    contradictions.append({
                        "bundle_id": str(bundle_id),
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "event_ids": str(arrest_event_id),
                        "narrative": narrative,
                        "statute": self.statute
                    })
                else:
                    earliest_prod = prod_events.sort_values("dt").iloc[0]
                    prod_dt = earliest_prod["dt"]
                    prod_event_id = earliest_prod["event_id"]
                    prod_time_str = earliest_prod.get("timestamp_iso", str(prod_dt))

                    if pd.notnull(arrest_dt) and pd.notnull(prod_dt):
                        hours_gap = (prod_dt - arrest_dt).total_seconds() / 3600.0
                        if hours_gap > 24.0:
                            event_ids = f"{arrest_event_id},{prod_event_id}"
                            narrative = (
                                f"Accused arrested at {arrest_time_str} was produced before Judicial Magistrate at {prod_time_str} "
                                f"({hours_gap:.1f} hours post-arrest) — exceeding the 24-hour constitutional maximum under Art 22(2)."
                            )
                            contradictions.append({
                                "bundle_id": str(bundle_id),
                                "rule_id": self.rule_id,
                                "severity": self.severity,
                                "event_ids": event_ids,
                                "narrative": narrative,
                                "statute": self.statute
                            })

        return contradictions


class RuleCT10(BaseRule):
    """RULE CT-10 — Medical Examination Delay"""
    rule_id = "CT-10"
    name = "Medical Examination Delay"
    severity = "HIGH"
    statute = "Sec 54 CrPC / Sec 53 BNSS; D.K. Basu v. State of West Bengal (1997)"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        df["dt"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            arrest_events = bundle_group[(bundle_group["event_type"].str.lower() == "arrest") | (bundle_group["doc_type"].str.upper().str.contains("ARREST"))]
            mlc_events = bundle_group[(bundle_group["event_type"].str.lower().str.contains("medical_examination|mlc")) | (bundle_group["doc_type"].str.upper().str.contains("MLC|MEDICAL"))]

            if arrest_events.empty or mlc_events.empty:
                continue

            for _, arrest_row in arrest_events.iterrows():
                arrest_dt, arrest_event_id = arrest_row["dt"], arrest_row["event_id"]
                for _, mlc_row in mlc_events.iterrows():
                    mlc_dt, mlc_event_id = mlc_row["dt"], mlc_row["event_id"]
                    if pd.notnull(arrest_dt) and pd.notnull(mlc_dt) and mlc_dt >= arrest_dt:
                        hours_gap = (mlc_dt - arrest_dt).total_seconds() / 3600.0
                        if hours_gap > 12.0:
                            event_ids = f"{arrest_event_id},{mlc_event_id}"
                            narrative = (
                                f"Medical examination (MLC) for the arrested accused was conducted {hours_gap:.1f} hours post-arrest, "
                                f"violating D.K. Basu guidelines requiring immediate medical examination upon arrest to document injuries."
                            )
                            contradictions.append({
                                "bundle_id": str(bundle_id),
                                "rule_id": self.rule_id,
                                "severity": self.severity,
                                "event_ids": event_ids,
                                "narrative": narrative,
                                "statute": self.statute
                            })

        return contradictions


class RuleCT11(BaseRule):
    """RULE CT-11 — FSL Sample Forwarding Delay"""
    rule_id = "CT-11"
    name = "FSL Forwarding Delay"
    severity = "MEDIUM"
    statute = "NCB Standing Order No. 1/88; Kuchar v. State"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        df["dt"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            seizure_events = bundle_group[(bundle_group["event_type"].str.lower() == "seizure") | (bundle_group["doc_type"].str.upper().str.contains("SEIZURE|PANCHNAMA"))]
            fsl_events = bundle_group[(bundle_group["event_type"].str.lower().str.contains("fsl")) | (bundle_group["doc_type"].str.upper().str.contains("FSL|FORWARDING"))]

            if seizure_events.empty or fsl_events.empty:
                continue

            for _, seizure_row in seizure_events.iterrows():
                seizure_dt, seizure_event_id = seizure_row["dt"], seizure_row["event_id"]
                for _, fsl_row in fsl_events.iterrows():
                    fsl_dt, fsl_event_id = fsl_row["dt"], fsl_row["event_id"]
                    if pd.notnull(seizure_dt) and pd.notnull(fsl_dt) and fsl_dt >= seizure_dt:
                        days_gap = (fsl_dt - seizure_dt).total_seconds() / 86400.0
                        if days_gap > FSL_FORWARDING_DELAY_DAYS_THRESHOLD:
                            event_ids = f"{seizure_event_id},{fsl_event_id}"
                            narrative = (
                                f"Seized contraband sample forwarded to Forensic Science Laboratory {days_gap:.1f} days after seizure, "
                                f"exceeding the statutory 72-hour limit under NCB Standing Order 1/88."
                            )
                            contradictions.append({
                                "bundle_id": str(bundle_id),
                                "rule_id": self.rule_id,
                                "severity": self.severity,
                                "event_ids": event_ids,
                                "narrative": narrative,
                                "statute": self.statute
                            })

        return contradictions


class RuleCT12(BaseRule):
    """RULE CT-12 — NDPS Section 50 Statutory Consent Memo Defect"""
    rule_id = "CT-12"
    name = "NDPS Section 50 Consent Memo Missing"
    severity = "CRITICAL"
    statute = "Sec 50 NDPS Act; Vijaysinh Chandubha Jadeja v. State of Gujarat (2011) 1 SCC 609"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if docs_df.empty or events_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        
        ndps_bundles = set()
        if seizures_df is not None and not seizures_df.empty:
            sz_merged = seizures_df.merge(events_df, on="event_id", how="inner").merge(docs_df, on="doc_id", how="inner")
            for _, sz_row in sz_merged.iterrows():
                item_txt = str(sz_row.get("item_desc") or "").lower()
                doc_txt = str(sz_row.get("doc_type") or "").lower()
                action_txt = str(sz_row.get("action") or "").lower()
                if any(k in item_txt or k in doc_txt or k in action_txt for k in ["narcotic", "contraband", "ndps", "drug", "heroin", "ganja"]):
                    ndps_bundles.add(sz_row["bundle_id"])

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            is_ndps_doc = bundle_group["doc_type"].str.lower().str.contains("narcotic|contraband|ndps|drug|heroin|ganja") | bundle_group["action"].str.lower().str.contains("narcotic|contraband|ndps|drug|heroin|ganja")
            if bundle_id in ndps_bundles or is_ndps_doc.any():
                has_consent = (bundle_group["consent_memo_present"] == 1).any() if "consent_memo_present" in bundle_group.columns else False
                if not has_consent:
                    ev_id = bundle_group.iloc[0]["event_id"]
                    narrative = (
                        "No Section 50 NDPS written consent memo found. "
                        "Under Vijaysinh Jadeja (Constitution Bench), informing the accused in writing of the statutory right to be searched before a Gazetted Officer or Magistrate is mandatory; non-compliance vitiates the recovery."
                    )
                    contradictions.append({
                        "bundle_id": str(bundle_id),
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "event_ids": str(ev_id),
                        "narrative": narrative,
                        "statute": self.statute
                    })
        return contradictions


class RuleCT13(BaseRule):
    """RULE CT-13 — NDPS Section 52A Magistrate Inventory & Sample Certification"""
    rule_id = "CT-13"
    name = "NDPS Sample Certification Missing (Sec 52A)"
    severity = "CRITICAL"
    statute = "Sec 52A NDPS Act; Simarnjit Singh v. State of Punjab (2023); Union of India v. Mohanlal (2016)"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if docs_df.empty or events_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        
        ndps_bundles = set()
        if seizures_df is not None and not seizures_df.empty:
            sz_merged = seizures_df.merge(events_df, on="event_id", how="inner").merge(docs_df, on="doc_id", how="inner")
            for _, sz_row in sz_merged.iterrows():
                item_txt = str(sz_row.get("item_desc") or "").lower()
                doc_txt = str(sz_row.get("doc_type") or "").lower()
                action_txt = str(sz_row.get("action") or "").lower()
                if any(k in item_txt or k in doc_txt or k in action_txt for k in ["narcotic", "contraband", "ndps", "drug", "heroin", "ganja"]):
                    ndps_bundles.add(sz_row["bundle_id"])

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            is_ndps_doc = bundle_group["doc_type"].str.lower().str.contains("narcotic|contraband|ndps|drug|heroin|ganja") | bundle_group["action"].str.lower().str.contains("narcotic|contraband|ndps|drug|heroin|ganja")
            if bundle_id in ndps_bundles or is_ndps_doc.any():
                has_cert = (bundle_group["sample_certification_present"] == 1).any() if "sample_certification_present" in bundle_group.columns else False
                if not has_cert:
                    ev_id = bundle_group.iloc[0]["event_id"]
                    narrative = (
                        "No Magistrate inventory certification under Sec 52A NDPS Act present. "
                        "As per Simarnjit Singh (Supreme Court, 2023), samples drawn at spot by IO without Judicial Magistrate certification cannot be treated as primary evidence in trial."
                    )
                    contradictions.append({
                        "bundle_id": str(bundle_id),
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "event_ids": str(ev_id),
                        "narrative": narrative,
                        "statute": self.statute
                    })
        return contradictions


class RuleCT14(BaseRule):
    """RULE CT-14 — NDPS Section 42 Warrantless Nighttime Search Grounds"""
    rule_id = "CT-14"
    name = "Warrantless Search Reasons Not Recorded"
    severity = "HIGH"
    statute = "Sec 42 NDPS Act / Sec 165 CrPC; State of Punjab v. Balbir Singh (1994)"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        seizure_events = df[(df["event_type"].str.lower() == "seizure") | (df["doc_type"].str.upper().str.contains("SEIZURE|PANCHNAMA"))]

        for _, ev_row in seizure_events.iterrows():
            reasons_val = ev_row.get("search_reasons_recorded")
            if pd.isnull(reasons_val) or int(reasons_val) != 1:
                loc = ev_row["location_raw"] or "search location"
                narrative = (
                    f"No recorded grounds of belief found prior to conducting search at '{loc}'. "
                    f"Under Sec 42 NDPS Act / Sec 165 CrPC, IO must record reasons for belief in writing before conducting warrantless search."
                )
                contradictions.append({
                    "bundle_id": str(ev_row["bundle_id"]),
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "event_ids": str(ev_row["event_id"]),
                    "narrative": narrative,
                    "statute": self.statute
                })

        return contradictions


class RuleCT15(BaseRule):
    """RULE CT-15 — Repeat/Stock Witness Across Cases"""
    rule_id = "CT-15"
    name = "Repeat/Stock Witness Across Cases"
    severity = "HIGH"
    statute = "Sec 100 CrPC / Sec 103 BNSS; Evidentiary Credibility Precedents"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty or actors_df is None or event_actors_df is None:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        merged = event_actors_df.merge(df, on="event_id", how="inner").merge(actors_df, on="actor_id", how="inner")

        witnesses = merged[
            (merged["role"].str.lower() == "panch_witness") |
            (merged["role_in_event"].str.lower().str.contains("witness", na=False))
        ]

        if witnesses.empty:
            return contradictions

        for name, group in witnesses.groupby("name_canonical"):
            distinct_bundles = group["bundle_id"].unique()
            if len(distinct_bundles) >= 2:
                first_row = group.iloc[0]
                narrative = (
                    f"Witness '{name}' appears as attesting witness across {len(distinct_bundles)} distinct case bundles ({', '.join(distinct_bundles)}). "
                    f"Using professional 'stock witnesses' destroys independent evidentiary credibility."
                )
                contradictions.append({
                    "bundle_id": str(first_row["bundle_id"]),
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "event_ids": str(first_row["event_id"]),
                    "narrative": narrative,
                    "statute": self.statute
                })

        return contradictions


class RuleCT16(BaseRule):
    """RULE CT-16 — Statutory Detention Limit Exceeded (Sec 167 CrPC / Default Bail)"""
    rule_id = "CT-16"
    name = "Statutory Detention Limit Exceeded (Sec 167 CrPC)"
    severity = "CRITICAL"
    statute = "Sec 167(2) CrPC / Sec 187 BNSS; Sec 36A(4) NDPS Act; Sanjay Dutt v. State (1994)"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        df["dt"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            arrest_events = bundle_group[(bundle_group["event_type"].str.lower() == "arrest") | (bundle_group["doc_type"].str.upper().str.contains("ARREST"))]
            if arrest_events.empty:
                continue

            cs_docs = bundle_group[bundle_group["doc_type"].str.upper() == "CHARGESHEET"]

            limit_days = 60
            if seizures_df is not None and not seizures_df.empty:
                sz_merged = seizures_df.merge(events_df, on="event_id", how="inner").merge(docs_df, on="doc_id", how="inner")
                bundle_sz = sz_merged[sz_merged["bundle_id"] == bundle_id]
                for _, sz_row in bundle_sz.iterrows():
                    qty = sz_row.get("quantity") or 0.0
                    txt = (str(sz_row.get("item_desc") or "") + str(sz_row.get("item_category") or "")).lower()
                    if qty >= 0.25 or any(k in txt for k in ["commercial", "narcotic", "contraband", "ndps", "heroin"]):
                        limit_days = 90
                        break

            for _, arrest_row in arrest_events.iterrows():
                arrest_dt = arrest_row["dt"]
                arrest_event_id = arrest_row["event_id"]

                if cs_docs.empty:
                    days_gap = (pd.Timestamp.now() - arrest_dt).total_seconds() / 86400.0 if pd.notnull(arrest_dt) else (limit_days + 5)
                    if days_gap > limit_days:
                        narrative = (
                            f"Chargesheet not filed after {days_gap:.0f} days of arrest, exceeding the {limit_days}-day statutory limit under Sec 167(2) CrPC. "
                            f"Accused has an indefeasible right to Default Bail (Sanjay Dutt v. State)."
                        )
                        contradictions.append({
                            "bundle_id": str(bundle_id),
                            "rule_id": self.rule_id,
                            "severity": self.severity,
                            "event_ids": str(arrest_event_id),
                            "narrative": narrative,
                            "statute": self.statute
                        })
                else:
                    cs_row = cs_docs.sort_values("dt").iloc[0]
                    cs_dt = cs_row["dt"]
                    cs_event_id = cs_row["event_id"]
                    if pd.notnull(arrest_dt) and pd.notnull(cs_dt):
                        days_gap = (cs_dt - arrest_dt).total_seconds() / 86400.0
                        if days_gap > limit_days:
                            narrative = (
                                f"Chargesheet filed {days_gap:.0f} days after arrest, exceeding the {limit_days}-day limit under Sec 167(2) CrPC. "
                                f"Defeats statutory detention timeline, entitling accused to Default Bail."
                            )
                            contradictions.append({
                                "bundle_id": str(bundle_id),
                                "rule_id": self.rule_id,
                                "severity": self.severity,
                                "event_ids": f"{arrest_event_id},{cs_event_id}",
                                "narrative": narrative,
                                "statute": self.statute
                            })

        return contradictions


class RuleCT17(BaseRule):
    """RULE CT-17 — FIR-to-Chargesheet Section Discrepancy"""
    rule_id = "CT-17"
    name = "FIR-to-Chargesheet Section Discrepancy"
    severity = "MEDIUM"
    statute = "Sec 173(2) CrPC / Sec 193 BNSS"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        for bundle_id, bundle_group in df.groupby("bundle_id"):
            fir_ev = bundle_group[(bundle_group["event_type"].str.lower() == "fir_registration") | (bundle_group["doc_type"].str.upper() == "FIR")]
            cs_ev = bundle_group[(bundle_group["event_type"].str.lower() == "chargesheet") | (bundle_group["doc_type"].str.upper() == "CHARGESHEET")]

            if fir_ev.empty or cs_ev.empty:
                continue

            fir_sec_str = str(fir_ev.iloc[0].get("sections_invoked") or "").strip()
            cs_sec_str = str(cs_ev.iloc[0].get("sections_invoked") or "").strip()

            if not fir_sec_str or not cs_sec_str:
                continue

            fir_secs = {s.strip() for s in fir_sec_str.split(",") if s.strip()}
            cs_secs = {s.strip() for s in cs_sec_str.split(",") if s.strip()}

            new_sections = cs_secs - fir_secs
            if new_sections:
                new_str = ", ".join(sorted(new_sections))
                fir_str = ", ".join(sorted(fir_secs))
                event_ids = f"{fir_ev.iloc[0]['event_id']},{cs_ev.iloc[0]['event_id']}"
                narrative = (
                    f"Additional statutory sections ({new_str}) introduced in chargesheet that were absent in FIR ({fir_str}) "
                    f"without recorded supplementary 161 CrPC statements."
                )

                contradictions.append({
                    "bundle_id": str(bundle_id),
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "event_ids": event_ids,
                    "narrative": narrative,
                    "statute": self.statute
                })

        return contradictions


class RuleCT18(BaseRule):
    """RULE CT-18 — Case Property Register Gap"""
    rule_id = "CT-18"
    name = "Case Property Register Gap"
    severity = "MEDIUM"
    statute = "Sec 55 NDPS Act / Malkhana Register No. 19 Regulations"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        for bundle_id, bundle_group in df.groupby("bundle_id"):
            seizures = bundle_group[(bundle_group["event_type"].str.lower() == "seizure") | (bundle_group["doc_type"].str.upper().str.contains("SEIZURE|PANCHNAMA"))]
            if seizures.empty:
                continue

            malkhana_doc = bundle_group[bundle_group["doc_type"].str.upper().str.contains("PROPERTY REGISTER|MALKHANA")]
            if malkhana_doc.empty:
                first_sz = seizures.iloc[0]
                narrative = f"No Malkhana Register No. 19 entry found for contraband seized in bundle '{bundle_id}', risking un-tracked storage."
                contradictions.append({
                    "bundle_id": str(bundle_id),
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "event_ids": str(first_sz["event_id"]),
                    "narrative": narrative,
                    "statute": self.statute
                })

        return contradictions


class RuleCT19(BaseRule):
    """RULE CT-19 — Mandatory Audio-Video Recording Missing"""
    rule_id = "CT-19"
    name = "Mandatory Videography Missing"
    severity = "MEDIUM"
    statute = "Sec 105 BNSS; Sec 63B BSA"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        seizure_events = df[(df["event_type"].str.lower() == "seizure") | (df["doc_type"].str.upper().str.contains("SEIZURE|PANCHNAMA"))]

        for _, ev_row in seizure_events.iterrows():
            video_val = ev_row.get("videography_present")
            if pd.isnull(video_val) or int(video_val) != 1:
                loc = ev_row["location_raw"] or "search location"
                narrative = (
                    f"No recorded audio-video footage found for search/seizure at '{loc}'. "
                    f"Sec 105 BNSS mandates audio-video recording of all search and seizure proceedings."
                )
                contradictions.append({
                    "bundle_id": str(ev_row["bundle_id"]),
                    "rule_id": self.rule_id,
                    "severity": self.severity,
                    "event_ids": str(ev_row["event_id"]),
                    "narrative": narrative,
                    "statute": self.statute
                })

        return contradictions


class RuleCT20(BaseRule):
    """RULE CT-20 — Statement Recorded in Unfamiliar Language"""
    rule_id = "CT-20"
    name = "Statement Recorded in Unfamiliar Language"
    severity = "HIGH"
    statute = "Sec 161 CrPC / Sec 180 BNSS / Sec 281 CrPC"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if docs_df.empty or events_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        for _, row in df.iterrows():
            lang = row.get("statement_language")
            if pd.notnull(lang) and str(lang).strip() and str(lang).lower() not in ["none", "nan", "null"]:
                understood = row.get("accused_understood_language")
                if pd.notnull(understood) and int(understood) == 0:
                    narrative = f"Statement recorded in '{lang}' which accused/witness did not understand, without certified interpreter endorsement."
                    contradictions.append({
                        "bundle_id": str(row["bundle_id"]),
                        "rule_id": self.rule_id,
                        "severity": self.severity,
                        "event_ids": str(row["event_id"]),
                        "narrative": narrative,
                        "statute": self.statute
                    })

        return contradictions


class RuleCT21(BaseRule):
    """RULE CT-21 — Identification Parade (TIP) Delay"""
    rule_id = "CT-21"
    name = "Identification Parade (TIP) Delay"
    severity = "MEDIUM"
    statute = "Sec 9 Evidence Act / Sec 7 BSA; Rajesh v. State"

    def evaluate(self, events_df: pd.DataFrame, docs_df: pd.DataFrame, actors_df=None, event_actors_df=None, seizures_df=None):
        contradictions = []
        if events_df.empty or docs_df.empty:
            return contradictions

        df = events_df.merge(docs_df, on="doc_id", how="inner")
        df["dt"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")

        for bundle_id, bundle_group in df.groupby("bundle_id"):
            arrest_events = bundle_group[(bundle_group["event_type"].str.lower() == "arrest") | (bundle_group["doc_type"].str.upper().str.contains("ARREST"))]
            tip_events = bundle_group[(bundle_group["event_type"].str.lower().str.contains("tip_parade|tip")) | (bundle_group["doc_type"].str.upper().str.contains("TIP|IDENTIFICATION PARADE"))]

            if arrest_events.empty or tip_events.empty:
                continue

            for _, arrest_row in arrest_events.iterrows():
                arrest_dt = arrest_row["dt"]
                arrest_event_id = arrest_row["event_id"]

                for _, tip_row in tip_events.iterrows():
                    tip_dt = tip_row["dt"]
                    tip_event_id = tip_row["event_id"]

                    if pd.notnull(arrest_dt) and pd.notnull(tip_dt) and tip_dt >= arrest_dt:
                        days_gap = (tip_dt - arrest_dt).total_seconds() / 86400.0
                        if days_gap > 7.0:
                            event_ids = f"{arrest_event_id},{tip_event_id}"
                            narrative = f"Test Identification Parade (TIP) conducted {days_gap:.0f} days after arrest — unexplained delay weakens identification value."
                            contradictions.append({
                                "bundle_id": str(bundle_id),
                                "rule_id": self.rule_id,
                                "severity": self.severity,
                                "event_ids": event_ids,
                                "narrative": narrative,
                                "statute": self.statute
                            })

        return contradictions


class NyayaAuditEngine:
    """
    Extensible Audit Engine executing registered rules and persisting findings into nyayatrace.db.
    """
    def __init__(self, db_path: str = "nyayatrace.db"):
        self.db_path = db_path
        self.rules: List[BaseRule] = []
        self._register_default_rules()

    def _register_default_rules(self):
        default_rules = [
            RuleCT01(), RuleCT02(), RuleCT03(), RuleCT04(), RuleCT05(),
            RuleCT06(), RuleCT07(), RuleCT08(), RuleCT09(), RuleCT10(),
            RuleCT11(), RuleCT12(), RuleCT13(), RuleCT14(), RuleCT15(),
            RuleCT16(), RuleCT17(), RuleCT18(), RuleCT19(), RuleCT20(), RuleCT21()
        ]
        for r in default_rules:
            self.register_rule(r)

    def register_rule(self, rule: BaseRule):
        self.rules.append(rule)

    def load_data(self, conn: sqlite3.Connection):
        ensure_db_schema(conn)
        docs_df = pd.read_sql_query("SELECT * FROM documents", conn)
        events_df = pd.read_sql_query("SELECT * FROM events", conn)
        actors_df = pd.read_sql_query("SELECT * FROM actors", conn)
        event_actors_df = pd.read_sql_query("SELECT * FROM event_actors", conn)
        seizures_df = pd.read_sql_query("SELECT * FROM seizures", conn)
        return docs_df, events_df, actors_df, event_actors_df, seizures_df

    def run(self, bundle_id: Optional[str] = None):
        print(f"Connecting to database '{self.db_path}'...")
        conn = sqlite3.connect(self.db_path)
        ensure_db_schema(conn)

        docs_df, events_df, actors_df, event_actors_df, seizures_df = self.load_data(conn)

        if bundle_id:
            docs_df = docs_df[docs_df["bundle_id"] == bundle_id]
            events_df = events_df[events_df["doc_id"].isin(docs_df["doc_id"])]

        total_inserted = 0

        for rule in self.rules:
            detected = rule.evaluate(events_df, docs_df, actors_df, event_actors_df, seizures_df)

            cursor = conn.cursor()
            for item in detected:
                cursor.execute("""
                    SELECT COUNT(*) FROM contradictions 
                    WHERE bundle_id = ? AND rule_id = ? AND event_ids = ? AND narrative = ?
                """, (item["bundle_id"], item["rule_id"], item["event_ids"], item["narrative"]))

                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO contradictions (bundle_id, rule_id, severity, event_ids, narrative, statute)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        item["bundle_id"],
                        item["rule_id"],
                        item["severity"],
                        item["item_ids"] if "item_ids" in item else item["event_ids"],
                        item["narrative"],
                        item["statute"]
                    ))
                    total_inserted += 1

        conn.commit()
        conn.close()
        print(f"Audit completed. Total new contradictions recorded: {total_inserted}")


if __name__ == "__main__":
    engine = NyayaAuditEngine("nyayatrace.db")
    engine.run()
