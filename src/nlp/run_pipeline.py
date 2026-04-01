"""
NHS Data Pipeline - NLP Pipeline Runner
=========================================
Orchestrates the full NLP pipeline:
1. Read clinical notes from DuckDB
2. Process through Clinical NER engine
3. Store extracted entities back to DuckDB
"""

import csv
import time
from pathlib import Path

import duckdb

from src.nlp.clinical_ner import ClinicalNER

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DUCKDB_PATH = PROJECT_ROOT / "data" / "duckdb" / "nhs_pipeline.duckdb"


def run_nlp_pipeline():
    """Run the full NLP pipeline."""
    print("=" * 60)
    print("NHS Data Pipeline - Clinical NLP Pipeline")
    print("=" * 60)
    print()

    # Initialize NER engine
    ner = ClinicalNER()

    # Connect to DuckDB
    conn = duckdb.connect(str(DUCKDB_PATH))
    print(f"\n📂 Connected to DuckDB: {DUCKDB_PATH}")

    # Read clinical notes
    print("\n📝 Reading clinical notes...")
    notes = conn.execute("""
        SELECT note_id, episode_id, patient_id, note_text, note_type
        FROM raw.raw_clinical_notes
    """).fetchall()
    print(f"   Found {len(notes):,} clinical notes to process")

    # Process notes
    print("\n🧠 Processing notes through NLP engine...")
    all_entities = []
    note_summaries = []
    start_time = time.time()

    for i, (note_id, episode_id, patient_id, note_text, note_type) in enumerate(notes):
        # Extract entities
        entities = ner.process_note(note_id, note_text)

        # Add episode and patient context to each entity
        for entity in entities:
            entity["episode_id"] = episode_id
            entity["patient_id"] = patient_id
            entity["note_type"] = note_type

        all_entities.extend(entities)

        # Create note summary
        conditions = [e for e in entities if e["entity_type"] == "condition"]
        medications = [e for e in entities if e["entity_type"] == "medication"]
        symptoms = [e for e in entities if e["entity_type"] == "symptom"]
        vitals = [e for e in entities if e["entity_type"] == "vital_sign"]

        note_summaries.append({
            "note_id": note_id,
            "episode_id": episode_id,
            "patient_id": patient_id,
            "note_type": note_type,
            "total_entities": len(entities),
            "condition_count": len(conditions),
            "medication_count": len(medications),
            "symptom_count": len(symptoms),
            "vital_sign_count": len(vitals),
            "conditions_found": "|".join([e["entity_name"] for e in conditions]),
            "medications_found": "|".join([e["entity_name"] for e in medications]),
            "symptoms_found": "|".join([e["entity_name"] for e in symptoms]),
            "note_length": len(note_text),
            "processing_method": "rule_based_spacy",
        })

        # Progress update
        if (i + 1) % 500 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            print(f"   Processed {i + 1:,}/{len(notes):,} notes ({rate:.0f} notes/sec)")

    elapsed = time.time() - start_time
    print(f"\n✅ Processing complete in {elapsed:.1f} seconds")
    print(f"   Total entities extracted: {len(all_entities):,}")

    # Save entities to CSV
    print("\n💾 Saving results...")
    entities_path = RAW_DATA_DIR / "nlp_extracted_entities.csv"
    summaries_path = RAW_DATA_DIR / "nlp_note_summaries.csv"

    if all_entities:
        with open(entities_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_entities[0].keys())
            writer.writeheader()
            writer.writerows(all_entities)
        print(f"   ✅ Entities: {entities_path.name} ({len(all_entities):,} rows)")

    if note_summaries:
        with open(summaries_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=note_summaries[0].keys())
            writer.writeheader()
            writer.writerows(note_summaries)
        print(f"   ✅ Summaries: {summaries_path.name} ({len(note_summaries):,} rows)")

    # Load into DuckDB
    print("\n📊 Loading NLP results into DuckDB...")
    conn.execute("CREATE SCHEMA IF NOT EXISTS nlp")

    # Load entities
    conn.execute("DROP TABLE IF EXISTS nlp.nlp_extracted_entities")
    conn.execute(f"""
        CREATE TABLE nlp.nlp_extracted_entities AS
        SELECT * FROM read_csv_auto('{entities_path}', header=true)
    """)

    # Load summaries
    conn.execute("DROP TABLE IF EXISTS nlp.nlp_note_summaries")
    conn.execute(f"""
        CREATE TABLE nlp.nlp_note_summaries AS
        SELECT * FROM read_csv_auto('{summaries_path}', header=true)
    """)

    # Print summary statistics
    print()
    print("=" * 60)
    print("NLP PIPELINE RESULTS")
    print("=" * 60)

    # Entity type breakdown
    entity_stats = conn.execute("""
        SELECT
            entity_type,
            COUNT(*) as count,
            COUNT(DISTINCT entity_name) as unique_entities,
            ROUND(AVG(confidence), 2) as avg_confidence
        FROM nlp.nlp_extracted_entities
        GROUP BY entity_type
        ORDER BY count DESC
    """).fetchall()

    print("\n📊 Entity Extraction Summary:")
    print(f"   {'Type':<15} {'Count':>8} {'Unique':>8} {'Avg Conf':>10}")
    print(f"   {'-'*15} {'-'*8} {'-'*8} {'-'*10}")
    for row in entity_stats:
        print(f"   {row[0]:<15} {row[1]:>8,} {row[2]:>8} {row[3]:>10}")

    # Top conditions
    top_conditions = conn.execute("""
        SELECT entity_name, COUNT(*) as count
        FROM nlp.nlp_extracted_entities
        WHERE entity_type = 'condition'
        GROUP BY entity_name
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()

    print("\n🏥 Top 10 Conditions Extracted:")
    for name, count in top_conditions:
        print(f"   {name:<30} {count:>6}")

    # Top medications
    top_meds = conn.execute("""
        SELECT entity_name, COUNT(*) as count
        FROM nlp.nlp_extracted_entities
        WHERE entity_type = 'medication'
        GROUP BY entity_name
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()

    print("\n💊 Top 10 Medications Extracted:")
    for name, count in top_meds:
        print(f"   {name:<30} {count:>6}")

    # Coverage stats
    coverage = conn.execute("""
        SELECT
            COUNT(*) as total_notes,
            SUM(CASE WHEN total_entities > 0 THEN 1 ELSE 0 END) as notes_with_entities,
            ROUND(AVG(total_entities), 1) as avg_entities_per_note,
            ROUND(AVG(condition_count), 1) as avg_conditions_per_note,
            ROUND(AVG(medication_count), 1) as avg_medications_per_note
        FROM nlp.nlp_note_summaries
    """).fetchone()

    print(f"\n📈 Coverage Statistics:")
    print(f"   Total notes processed:     {coverage[0]:,}")
    print(f"   Notes with entities found:  {coverage[1]:,} ({coverage[1]*100//coverage[0]}%)")
    print(f"   Avg entities per note:      {coverage[2]}")
    print(f"   Avg conditions per note:    {coverage[3]}")
    print(f"   Avg medications per note:   {coverage[4]}")

    conn.close()
    print()
    print("=" * 60)
    print("NLP PIPELINE COMPLETE ✅")
    print("=" * 60)


if __name__ == "__main__":
    run_nlp_pipeline()