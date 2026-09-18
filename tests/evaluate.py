# evaluate.py

import csv
import sys
from pathlib import Path

# Fix Windows Unicode output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from retrieval import search_opportunities, parse_tenure

CSV_PATH = ROOT / "data" / "labelled_examples.csv"
K = 5

def precision_at_k(retrieved_ids, relevant_ids):
    return len(set(retrieved_ids[:K]) & relevant_ids) / K


def recall_at_k(retrieved_ids, relevant_ids):
    if not relevant_ids:
        return 0.0
    return len(set(retrieved_ids[:K]) & relevant_ids) / len(relevant_ids)


def hit_rate_at_k(retrieved_ids, relevant_ids):
    return float(bool(set(retrieved_ids[:K]) & relevant_ids))


def main():
    precisions = []
    recalls = []
    hits = []

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            query_id = row["query_id"]
            query = row["query"]
            relevant_ids = {
                x.strip()
                for x in row["relevant_ids"].split(";")
                if x.strip()
            }

            # Call your actual retrieval function
            results = search_opportunities(query, top_k=K)
            retrieved_ids = [
                item["opportunity_id"]
                for item in results
                if item.get("opportunity_id")
            ]

            p = precision_at_k(retrieved_ids, relevant_ids)
            r = recall_at_k(retrieved_ids, relevant_ids)
            h = hit_rate_at_k(retrieved_ids, relevant_ids)

            precisions.append(p)
            recalls.append(r)
            hits.append(h)

            print(f"\n{query_id}: {query}")
            print("Parsed tenure:", parse_tenure(query))
            print("Relevant IDs:", sorted(relevant_ids))
            print("Retrieved IDs:", retrieved_ids)
            print(f"Precision@{K}: {p:.3f}")
            print(f"Recall@{K}:    {r:.3f}")
            print(f"Hit Rate@{K}:  {h:.0f}")

    if precisions:
        n = len(precisions)
        print("\n===== EVALUATION SUMMARY =====")
        print(f"Queries evaluated: {n}")
        print(f"Mean Precision@{K}: {sum(precisions) / n:.3f}")
        print(f"Mean Recall@{K}:    {sum(recalls) / n:.3f}")
        print(f"Hit Rate@{K}:       {sum(hits) / n:.3f}")


if __name__ == "__main__":
    main()