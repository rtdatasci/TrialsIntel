"""
One-shot pipeline: fetch trials → extract entities → store in SQLite.
Run: python run_pipeline.py
"""
import time
from src.fetch_trials import fetch_trials_from_api
from src.extract_entities import extract_with_claude
from src.database import init_db, save_trial

QUERIES = ["cancer", "immunology"]
MAX_PER_QUERY = 25  # 25 * 2 queries = ~50 trials total


def build_trial_text(trial: dict) -> str:
    return f"{trial['title']}. {trial['summary']}"


def main():
    init_db()
    total = 0

    for query in QUERIES:
        print(f"\nFetching trials for query: '{query}'")
        trials = fetch_trials_from_api(query=query, max_results=MAX_PER_QUERY)
        print(f"  Got {len(trials)} trials")

        for i, trial in enumerate(trials):
            print(f"  [{i+1}/{len(trials)}] Extracting: {trial['nct_id']}")
            entities = extract_with_claude(build_trial_text(trial))
            # Merge API fields with Claude-extracted entities
            combined = {**trial, **entities}
            # Fill sponsor/phase from API if Claude returned None
            if not combined.get("sponsor"):
                combined["sponsor"] = trial.get("sponsor", "")
            if not combined.get("phase"):
                combined["phase"] = trial.get("phase", "")
            save_trial(combined)
            total += 1
            time.sleep(0.5)  # Be polite to the API

    print(f"\nDone. Saved {total} trials to database.")


if __name__ == "__main__":
    main()
