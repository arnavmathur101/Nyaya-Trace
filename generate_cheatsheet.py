"""
NyayaTrace Cross-Examination Cheat Sheet Generator
Generates targeted cross-examination questions grouped by witness/officer
based on contradictions found in nyayatrace.db for a given bundle_id.
"""

import sys
import os
import sqlite3
import pandas as pd

def map_rule_to_actor(rule_id: str) -> str:
    """Maps audit rule_id to target officer or witness for cross-examination."""
    io_rules = ["CT-01", "CT-02", "CT-05", "CT-08", "CT-10", "CT-11", "CT-12", "CT-14", "CT-15", "CT-18", "CT-19", "CT-21"]
    panch_rules = ["CT-03", "CT-07", "CT-09", "CT-16"]
    custody_rules = ["CT-04", "CT-06", "CT-13", "CT-17", "CT-20"]
    
    if rule_id in io_rules:
        return "Investigating Officer (IO) / Seizure Officer"
    elif rule_id in panch_rules:
        return "Independent Panch Witness"
    elif rule_id in custody_rules:
        return "Malkhana In-Charge / FSL Custodian"
    else:
        return "Prosecution Witness / IO"


def generate_questions_for_contradiction(rule_id: str, narrative: str, statute: str, event_ids: str) -> list:
    """Generates 1-2 factual cross-examination questions strictly derived from stored database narrative."""
    questions = []
    
    if rule_id == "CT-01":
        questions.append(f"Q: Officer, according to the records ({event_ids}), the seizure event occurred BEFORE the FIR registration. Under what legal authority was this seizure conducted prior to registering an FIR under {statute}?")
        questions.append(f"Q: Did you record any Station Diary entry or preliminary inquiry notes before conducting the seizure?")
    elif rule_id == "CT-02":
        questions.append(f"Q: Officer, you are shown as participating in two events ({event_ids}) across distant locations within an impossible timeframe. How did you travel between these locations?")
        questions.append("Q: Can you produce official logbooks, toll receipts, or vehicle GPS records verifying your location at that timestamp?")
    elif rule_id == "CT-03":
        questions.append(f"Q: Witness, your registered residence is over 20 km from the seizure spot ({event_ids}). Why were you chosen as a panch witness instead of local residents under {statute}?")
        questions.append("Q: Have you acted as a panch witness for the police in any other cases prior to this?")
    elif rule_id == "CT-04":
        questions.append(f"Q: Custodian, there is a material discrepancy in the weight of contraband recorded in seizure memo vs later documents ({event_ids}). Where did the missing quantity vanish while in police custody?")
        questions.append("Q: Was the sample weighed on a calibrated scale, and were seal integrity logs maintained at the Malkhana?")
    elif rule_id == "CT-05":
        questions.append(f"Q: Inspector, you signed documents for two separate events ({event_ids}) at distant locations at virtually the same time. Which of these documents contains a fabricated timestamp?")
        questions.append("Q: Does your official mobile tower location record confirm your presence at the seizure site at the time of signing?")
    elif rule_id == "CT-06":
        questions.append(f"Q: Custodian, the seized samples were forwarded to FSL after an unexplained delay exceeding 7 days ({event_ids}). Under whose custody were the samples kept during this delay?")
        questions.append(f"Q: Were seal condition checks recorded daily in the Malkhana register as mandated under {statute}?")
    elif rule_id == "CT-07":
        questions.append(f"Q: Officer, the search memo ({event_ids}) lists fewer than two independent panch witnesses. Did you make any written request to local residents to join as witnesses under {statute}?")
        questions.append("Q: Did you record the names of any local persons who allegedly refused to witness the search?")
    elif rule_id == "CT-12":
        questions.append(f"Q: Officer, the records ({event_ids}) confirm no written Section 50 consent memo was prepared before searching the accused person. Did you inform the accused of his statutory right to be searched before a Magistrate?")
        questions.append("Q: Is there any document bearing the signature of the accused acknowledging his consent?")
    elif rule_id == "CT-13":
        questions.append(f"Q: Officer, no Magistrate sample certification under Section 52A NDPS was obtained for the seized items ({event_ids}). Were the samples drawn in the presence of a Judicial Magistrate?")
        questions.append("Q: In the absence of a Section 52A certificate, how can these samples be verified as primary court evidence?")
    else:
        questions.append(f"Q: [{rule_id}] Reference {event_ids}: Explain why statutory procedure under {statute} was not strictly adhered to as noted: '{narrative}'?")
        questions.append(f"Q: Was this irregularity ({rule_id}) reported to senior officers or documented in the GD entry?")

    return questions


def generate_cheatsheet(bundle_id: str, db_path: str = "nyayatrace.db") -> str:
    """Queries nyayatrace.db and writes CrossExam_CheatSheet_{bundle_id}.md."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database {db_path} not found.")

    conn = sqlite3.connect(db_path)
    query = """
    SELECT rule_id, severity, narrative, statute, event_ids, created_at
    FROM contradictions
    WHERE bundle_id = ?
    ORDER BY 
        CASE severity
            WHEN 'CRITICAL' THEN 1
            WHEN 'HIGH' THEN 2
            WHEN 'MEDIUM' THEN 3
            ELSE 4
        END, rule_id
    """
    df = pd.read_sql_query(query, conn, params=(bundle_id,))
    conn.close()

    if df.empty:
        print(f"No contradictions found in {db_path} for bundle '{bundle_id}'.")
        return ""

    # Group questions by actor
    actor_groups = {
        "Investigating Officer (IO) / Seizure Officer": [],
        "Independent Panch Witness": [],
        "Malkhana In-Charge / FSL Custodian": [],
        "Prosecution Witness / IO": []
    }

    for idx, row in df.iterrows():
        actor = map_rule_to_actor(row['rule_id'])
        questions = generate_questions_for_contradiction(
            row['rule_id'], row['narrative'], str(row['statute']), str(row['event_ids'])
        )
        
        actor_groups[actor].append({
            "rule_id": row['rule_id'],
            "severity": row['severity'],
            "statute": row['statute'],
            "event_ids": row['event_ids'],
            "narrative": row['narrative'],
            "questions": questions
        })

    # Generate Markdown Content
    md = []
    md.append(f"# Cross-Examination Strategy Cheat Sheet")
    md.append(f"**Case Bundle:** `{bundle_id}`  ")
    md.append(f"**Generated By:** NyayaTrace™ Trial Court Evidence Audit Engine  ")
    md.append(f"**Total Contradictions Flagged:** {len(df)}  ")
    md.append("\n---\n")

    for actor, findings in actor_groups.items():
        if not findings:
            continue
        
        md.append(f"## 🏛️ Target Witness: {actor}\n")
        
        for item in findings:
            sev_badge = "🔴 CRITICAL" if item['severity'] == "CRITICAL" else ("🟠 HIGH" if item['severity'] == "HIGH" else "🟡 MEDIUM")
            md.append(f"### Finding [{item['rule_id']}] - {sev_badge}")
            md.append(f"- **Statute / Ground:** `{item['statute']}`")
            md.append(f"- **Events Involved:** `{item['event_ids']}`")
            md.append(f"- **Audit Narrative:** {item['narrative']}\n")
            md.append("**Targeted Cross-Examination Questions:**")
            for q in item['questions']:
                md.append(f"  - {q}")
            md.append("")

    filename = f"CrossExam_CheatSheet_{bundle_id}.md"
    filepath = os.path.abspath(filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"[SUCCESS] Generated Cross-Exam Cheat Sheet for '{bundle_id}' at: {filepath}")
    return filepath


if __name__ == "__main__":
    target_bundle = sys.argv[1] if len(sys.argv) > 1 else "CASE-2026-GAMMA"
    generate_cheatsheet(target_bundle)
