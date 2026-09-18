
import argparse
import json
from pathlib import Path

from src.extractor import extract_all_opportunities
from src.normalizer import normalize_opportunity
from src.retrieval import search_opportunities


def main():
    parser = argparse.ArgumentParser(
        description="Financial Opportunity Analysis Engine"
    )

    parser.add_argument(
        "--query",
        type=str,
        help="Natural-language investment query"
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of opportunities to return"
    )

    args = parser.parse_args()

    # Search mode
    if args.query:
        results = search_opportunities(
            args.query,
            top_k=args.top_k
        )

        if not results:
            print("No supported matches found.")
            return

        # Handle safeguard message responses
        messages = [
            item for item in results
            if isinstance(item, dict) and "message" in item
        ]

        if messages:
            for item in messages:
                print("\n" + item["message"])
            return

        # Display opportunity results
        for rank, item in enumerate(results, start=1):
            print(
                f"\n{rank}. "
                f"{item['opportunity_id']} - {item['name']}"
            )

            print(f"Score: {item['score']:.4f}")

            print("Reasons:")
            for reason in item.get("reasons", []):
                print(f"  - {reason}")

            print(
                "Matched attributes:",
                item.get("matched_attributes", {})
            )

            print(
                "Source:",
                item.get("source_document", "Not available")
            )

        return

    # Extraction and normalization mode
    opportunities = extract_all_opportunities()

    normalized = [
        normalize_opportunity(item)
        for item in opportunities
    ]

    output_path = Path("data/normalized_opportunities.json")
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            normalized,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Documents processed: {len(normalized)}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()