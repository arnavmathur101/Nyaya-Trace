import sqlite3
import pandas as pd
from rules import (
    NyayaAuditEngine,
    RuleCT01, RuleCT02, RuleCT03, RuleCT04, RuleCT05,
    RuleCT06, RuleCT07, RuleCT08, RuleCT09, RuleCT10,
    RuleCT11, RuleCT12, RuleCT13, RuleCT14, RuleCT15,
    RuleCT16, RuleCT17, RuleCT18, RuleCT19, RuleCT20, RuleCT21
)

def verify():
    engine = NyayaAuditEngine('nyayatrace.db')
    rules_list = [
        RuleCT01(), RuleCT02(), RuleCT03(), RuleCT04(), RuleCT05(),
        RuleCT06(), RuleCT07(), RuleCT08(), RuleCT09(), RuleCT10(),
        RuleCT11(), RuleCT12(), RuleCT13(), RuleCT14(), RuleCT15(),
        RuleCT16(), RuleCT17(), RuleCT18(), RuleCT19(), RuleCT20(), RuleCT21()
    ]
    for r in rules_list:
        engine.register_rule(r)

    engine.run(bundle_id='CASE-2026-OCR-DEMO')

    conn = sqlite3.connect('nyayatrace.db')
    df = pd.read_sql_query("SELECT rule_id, severity, statute, narrative FROM contradictions WHERE bundle_id = 'CASE-2026-OCR-DEMO'", conn)
    conn.close()

    print("\n=================================================================")
    print(f" FIRED RULES ON BUNDLE CASE-2026-OCR-DEMO (Total: {len(df)}):")
    print("=================================================================")
    for idx, row in df.iterrows():
        print(f" -> [{row['rule_id']}] ({row['severity']}) - {row['statute']}")
        print(f"    Narrative: {row['narrative']}")
    print("=================================================================")

if __name__ == "__main__":
    verify()
