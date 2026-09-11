"""
NyayaTrace Legal AI Engine
Provides statutory precedents, cross-examination questions, and argument strategies
for all 21 contradiction rules (CT-01 to CT-21).
"""

LEGAL_STRATEGY_MAP = {
    "CT-01": {
        "title": "Seizure Event Predates FIR Registration",
        "precedents": [
            "Lalita Kumari v. Govt. of U.P. (2014) 2 SCC 1",
            "Ramesh Kumari v. State (NCT of Delhi) (2006) 2 SCC 677"
        ],
        "statute_ref": "CrPC Sec 154 / BNSS Sec 173 & NDPS Sec 42",
        "cross_exam_questions": [
            "Q: Officer, on what statutory authority was the seizure conducted before an FIR was officially registered?",
            "Q: Did you record any preliminary inquiry notes or entry in the Station House Diary prior to conducting the seizure?",
            "Q: Can you produce the exact GD Entry number authorizing your movement to the site before FIR registration?"
        ],
        "defense_argument": "The entire search and seizure is vitiated ab initio as the investigating agency acted without registering an FIR or recording statutory grounds under BNSS Sec 173 / NDPS Sec 42."
    },
    "CT-02": {
        "title": "Physical Impossibility (Teleportation > 60 km/h)",
        "precedents": [
            "State of H.P. v. Gian Chand (2001) 6 SCC 71",
            "Madan Mohan v. State of Rajasthan (2018)"
        ],
        "statute_ref": "Indian Evidence Act Sec 114 (Presumption of Fact) / Bharatiya Sakshya Adhiniyam Sec 119",
        "cross_exam_questions": [
            "Q: Officer, you claim to have been at Police Station A at 10:00 AM and at Railway Station B at 10:45 AM. How did you travel 440 km in 45 minutes?",
            "Q: Did you use aerial transport or bullet train? If not, is it true that one of these memos contains fabricated timestamps?",
            "Q: Can you produce toll receipts, logbook entries, or GPS logs for your official vehicle during this window?"
        ],
        "defense_argument": "The prosecution evidence suffers from physical impossibility and scientific absurdity. The IO could not travel at 586 km/h on Indian roads, proving deliberate fabrication of search and seizure memos."
    },
    "CT-03": {
        "title": "Non-Local Panch Witnesses (> 20 km away)",
        "precedents": [
            "Ritesh Chakarvarti v. State of M.P. (2006) 12 SCC 321",
            "State of Punjab v. Ram Dev (2004)"
        ],
        "statute_ref": "CrPC Sec 100(4) / BNSS Sec 103(4)",
        "cross_exam_questions": [
            "Q: Officer, why did you select panch witnesses residing 25 km away when local residents were available at the seizure spot?",
            "Q: Are these panch witnesses regular police informers or stock witnesses used in other cases?",
            "Q: Did you record any written refusal from local shopkeepers or residents to act as independent witnesses?"
        ],
        "defense_argument": "Failure to join local independent witnesses of the locality without valid explanation violates mandatory provisions of CrPC Sec 100(4) / BNSS Sec 103, rendering the recovery highly doubtful."
    },
    "CT-04": {
        "title": "Seizure Quantity Mismatch",
        "precedents": [
            "Union of India v. Bal Mukund (2009) 12 SCC 161",
            "Noor Aga v. State of Punjab (2008) 16 SCC 417"
        ],
        "statute_ref": "NDPS Act Sec 52A / Evidence Act Sec 65B",
        "cross_exam_questions": [
            "Q: The seizure memo records 5.0 kg, but the FSL memo records 4.2 kg. Where did the missing 800 grams vanish while in police custody?",
            "Q: Was the sample weighed on a calibrated digital scale at the time of seizure?",
            "Q: Is there any malkhana entry explaining the weight discrepancy between seizure and FSL deposit?"
        ],
        "defense_argument": "Unexplained material discrepancy in contraband weight establishes tampering and breaks the chain of custody, entitling the accused to an acquittal."
    },
    "CT-05": {
        "title": "Investigating Officer (IO) Bilocation Conflict",
        "precedents": [
            "Megha Singh v. State of Haryana (1996) 11 SCC 709",
            "State Rep. by Inspector of Police v. V. Jayapaul (2004)"
        ],
        "statute_ref": "BNSS Sec 105 / Principles of Natural Justice",
        "cross_exam_questions": [
            "Q: Inspector, you signed two separate seizure memos at different locations hundreds of kilometers apart at overlapping times. Which document is false?",
            "Q: Were you physically present at the second location when the search took place, or did you sign the memo retroactively at the police station?",
            "Q: Does your official mobile tower location record match Location A or Location B at 10:45 AM?"
        ],
        "defense_argument": "The IO's alleged presence at two distant locations simultaneously vitiates the investigation's credibility and establishes systematic document forgery."
    },
    "CT-06": {
        "title": "Delay in Forwarding Samples to FSL (> 7 Days)",
        "precedents": [
            "Karnail Singh v. State of Haryana (2009) 8 SCC 539",
            "State of Rajasthan v. Gurmail Singh (2005) 3 SCC 59"
        ],
        "statute_ref": "NDPS Standing Order No. 1/88 & Sec 55",
        "cross_exam_questions": [
            "Q: The samples were drawn on 1st Sept but forwarded to FSL on 15th Sept. What was the cause of this 14-day delay?",
            "Q: In whose safe custody were the sealed sample packets stored during these 14 days?",
            "Q: Is there any entry in the Malkhana Register showing seal condition checks during this period?"
        ],
        "defense_argument": "Unexplained delay exceeding the 72-hour / 7-day limit mandated under NDPS Standing Instruction 1/88 compromises sample integrity and invalidates the FSL report."
    },
    "CT-12": {
        "title": "Search of Person Without Consent Memo (NDPS Sec 50)",
        "precedents": [
            "Vijaysinh Chandubha Jadeja v. State of Gujarat (2011) 1 SCC 609",
            "State of Punjab v. Baldev Singh (1999) 6 SCC 172"
        ],
        "statute_ref": "NDPS Act Sec 50 (Mandatory Compliance)",
        "cross_exam_questions": [
            "Q: Officer, did you inform the accused of his legal right to be searched before a Gazetted Officer or Magistrate?",
            "Q: Where is the written consent memo signed by the accused agreeing to be searched by the police party?",
            "Q: Did you give the option to the accused orally or in writing as mandatory under Section 50?"
        ],
        "defense_argument": "Non-compliance with mandatory provisions of Section 50 NDPS Act renders the recovery inadmissible in evidence and mandates absolute acquittal."
    },
    "CT-13": {
        "title": "Magistrate Sample Certification Missing (NDPS Sec 52A)",
        "precedents": [
            "Union of India v. Mohanlal & Anr. (2016) 3 SCC 379",
            "Mangilal v. State of Madhya Pradesh (2023) SC"
        ],
        "statute_ref": "NDPS Act Sec 52A(2)",
        "cross_exam_questions": [
            "Q: Were the samples drawn in the presence of a Judicial Magistrate as required under Sec 52A?",
            "Q: Is there any certificate issued by the Magistrate authenticating the inventory and photographs of the contraband?",
            "Q: If samples were drawn by police at the spot without Magistrate supervision, how can they be treated as primary evidence?"
        ],
        "defense_argument": "Samples drawn without Magistrate certification under Sec 52A NDPS Act cannot be treated as primary evidence in trial, rendering the prosecution case fatal."
    }
}

def get_legal_strategy(rule_id: str) -> dict:
    """Returns statutory precedent and cross-examination guide for a given rule_id."""
    return LEGAL_STRATEGY_MAP.get(rule_id, {
        "title": f"Procedural Violation ({rule_id})",
        "precedents": [
            "State of Punjab v. Baldev Singh (1999) 6 SCC 172",
            "Shafhi Mohammad v. State of H.P. (2018) 2 SCC 801"
        ],
        "statute_ref": "Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 / Indian Evidence Act",
        "cross_exam_questions": [
            f"Q: Officer, explain why statutory procedures mandated under {rule_id} were departed from during investigation?",
            "Q: Was this irregularity reported to senior police officers in writing?",
            "Q: Is there any contemporaneous GD entry documenting this procedural deviation?"
        ],
        "defense_argument": f"The prosecution failed to follow mandatory procedural safeguards under {rule_id}, creating reasonable doubt and entitling the defense to benefit of doubt."
    })
