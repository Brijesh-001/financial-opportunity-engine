
import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_PATH = Path(__file__).parent.parent / "data" / "normalized_opportunities.json"


def load_opportunities():
    with DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def build_text(item):
    """Create searchable text from documented fields."""
    fields = [
        item.get("name"),
        item.get("provider"),
        item.get("category"),
        item.get("risk"),
        item.get("return_type"),
    ]
    return " ".join(str(x) for x in fields if x)


def parse_budget(query):
    """Extract a budget amount from common query formats."""
    text = query.lower().replace(",", "")

    # Match currency-marked amounts first, e.g. ₹1 lakh or Rs. 50000
    match = re.search(
        r"(?:₹|rs\.?\s*)(\d+(?:\.\d+)?)\s*(lakh|lakhs|k)?",
        text
    )

    # Otherwise, match amounts written as "1 lakh"
    if not match:
        match = re.search(
            r"(\d+(?:\.\d+)?)\s*(lakh|lakhs)\b",
            text
        )

    if not match:
        return None

    amount = float(match.group(1))
    unit = match.group(2)

    if unit in ("lakh", "lakhs"):
        amount *= 100000
    elif unit == "k":
        amount *= 1000

    return amount

def parse_tenure(query):
    """Extract requested tenure range in months."""
    text = query.lower()
    
    number_words = {
        "one": "1", "two": "2", "three": "3",
        "four": "4", "five": "5", "six": "6",
        "seven": "7", "eight": "8", "nine": "9",
        "ten": "10", "eleven": "11", "twelve": "12"
    }

    for word, digit in number_words.items():
        text = re.sub(rf"\b{word}\b", digit, text)

    # Range: "3 to 5 years", "6-12 months"
    match = re.search(
        r"(\d+)\s*(?:to|-)\s*(\d+)\s*(months?|years?)",
        text
    )

    if match:
        low = int(match.group(1))
        high = int(match.group(2))
        unit = match.group(3)

        if unit.startswith("year"):
            low *= 12
            high *= 12

        return low, high

    # Open-ended minimum: "at least 3 years"
    match = re.search(
        r"(?:at least|minimum of|more than)\s*(\d+)\s*(months?|years?)",
        text
    )

    if match:
        low = int(match.group(1))
        if match.group(2).startswith("year"):
            low *= 12
        return low, None

    # Single duration: "around 2 years"
    match = re.search(
        r"(\d+)\s*(months?|years?)",
        text
    )

    if match:
        value = int(match.group(1))
        if match.group(2).startswith("year"):
            value *= 12
        return value, value

    return None

def parse_risk(query):
    text = query.lower()

    if "conservative" in text or "low risk" in text:
        return "Low"

    if "moderate risk" in text or "medium risk" in text:
        return "Moderate"

    if "high risk" in text:
        return "High"

    return None

def parse_return_preference(query):
    """Extract a requested return percentage and preference type."""
    text = query.lower()

    match = re.search(
        r"(?:above|over|at least|minimum of)\s*(\d+(?:\.\d+)?)\s*%",
        text
    )
    if match:
        return "minimum", float(match.group(1))

    match = re.search(
        r"(?:close to|around|approximately|about)\s*"
        r"(\d+(?:\.\d+)?)\s*%",
        text
    )
    if match:
        return "close", float(match.group(1))

    return None

def return_matches(preference, minimum, maximum):
    """Compare requested return with documented return range."""
    if preference is None or minimum is None:
        return None

    kind, target = preference

    # Missing upper bound: only the documented minimum is known.
    if maximum is None:
        maximum = minimum

    if kind == "minimum":
        return maximum > target

    if kind == "close":
        # Treat within 1 percentage point as "close".
        tolerance = 1.0
        return (
            minimum <= target + tolerance
            and maximum >= target - tolerance
        )

    return None


def risk_compatibility_score(requested, actual):
    """Return a documented label-match score, not a financial assessment."""
    if not requested or not actual:
        return None

    actual = actual.lower().replace("-", " ").strip()
    actual = " ".join(actual.split())

    # Normalize common documented labels.
    aliases = {
        "medium": "moderate",
        "moderately high": "moderate high",
    }
    actual = aliases.get(actual, actual)

    if requested == "Low":
        mapping = {
            "low": 1.0,
            "low to moderate": 0.5,
        }
    elif requested == "Moderate":
        mapping = {
            "moderate": 1.0,
            "low to moderate": 0.5,
            "moderate high": 0.5,
        }
    elif requested == "High":
        mapping = {
            "high": 1.0,
            "very high": 0.5,
        }
    else:
        return None

    return mapping.get(actual, 0.0)

def asks_for_guarantee(query):
    text = query.lower()
    return "guaranteed" in text or "guarantee" in text

def search_opportunities(query, top_k=5):
    opportunities = load_opportunities()

    documents = [build_text(item) for item in opportunities]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
    )

    matrix = vectorizer.fit_transform(documents + [query])
    text_scores = cosine_similarity(
        matrix[-1],
        matrix[:-1],
    ).flatten()

    budget = parse_budget(query)
    tenure = parse_tenure(query)
    risk = parse_risk(query)
    if asks_for_guarantee(query):
        return [{
            "message": (
                "No supported match found. "
                "The query requests a guaranteed return, "
                "but the system does not verify guarantees."
            ),
            "reasons": [
                "The dataset must explicitly support any guarantee.",
                "Indicative or historical returns are not guarantees."
            ]
        }]
    

    results = []

    for item, text_score in zip(opportunities, text_scores):
        matched_attributes = {}
        reasons = []
        score = 0.15 * float(text_score)

        # Budget match
        if budget is not None:
            minimum = item.get("minimum_investment_inr")

            if minimum is not None and minimum <= budget:
                score += 0.25
                reasons.append("Minimum investment is within budget")
                matched_attributes["budget"] = {
                    "requested_inr": budget,
                    "documented_minimum_inr": minimum
                }
            elif minimum is not None:
                reasons.append(
                    f"Minimum investment ₹{minimum} exceeds budget ₹{budget}"
                )


        # Risk compatibility
        if risk:
            risk_score = risk_compatibility_score(
                risk,
                item.get("risk")
            )

            if risk_score is not None:
                score += 0.25 * risk_score

                # Record the risk match
                if risk_score > 0:
                    matched_attributes["risk"] = {
                        "requested": risk,
                        "documented": item.get("risk")
                    }

                if risk_score == 1.0:
                    reasons.append("Exact documented risk-label match")
                elif risk_score == 0.5:
                    reasons.append("Adjacent documented risk-label match")
                else:
                    reasons.append(
                        "Risk label differs from requested category"
                    )

        # Tenure range match
        if tenure is not None:
            requested_low, requested_high = tenure

            low = item.get("tenure_min_months")
            high = item.get("tenure_max_months")

            if low is not None and high is not None:
                if requested_high is None:
                    # User wants this duration or longer
                   matched = high >= requested_low
                else:
                    # Check whether the ranges overlap
                    matched = (
                        low <= requested_high
                        and high >= requested_low
                    )

                if matched:
                    matched_attributes["tenure_months"] = {
                        "requested": [requested_low, requested_high],
                        "documented": [low, high]
                    }
                    score += 0.20
                    reasons.append("Tenure overlaps requested duration")
                else:
                    reasons.append(
                        "Tenure does not overlap requested duration"
                    )

        # Return preference: compare against documented return values.
        return_preference = parse_return_preference(query)

        if return_preference is not None:
            minimum_return = item.get("expected_return_min_pct")
            maximum_return = item.get("expected_return_max_pct")

            matched = return_matches(
                return_preference,
                minimum_return,
                maximum_return
            )

            if matched:
                score += 0.15
                reasons.append("Documented return range matches preference")
            elif matched is False:
                reasons.append("Documented return range does not match preference")
            else:
                reasons.append("Return data is missing or incomplete")

        results.append({
            "opportunity_id": item.get("opportunity_id"),
            "name": item.get("name"),
            "provider": item.get("provider"),
            "category": item.get("category"),
            "minimum_investment_inr": item.get(
                "minimum_investment_inr"
            ),
            "risk": item.get("risk"),
            "tenure_min_months": item.get("tenure_min_months"),
            "tenure_max_months": item.get("tenure_max_months"),
            "expected_return_min_pct": item.get(
                "expected_return_min_pct"
            ),
            "expected_return_max_pct": item.get(
                "expected_return_max_pct"
            ),
            "return_type": item.get("return_type"),
            "source_document": item.get("source_document"),
            "matched_attributes": matched_attributes,
            "score": round(score, 4),
            "text_similarity": round(float(text_score), 4),
            "reasons": reasons,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    query = input("Enter your financial opportunity query: ")
    results = search_opportunities(query)

    print("\nTop matches:\n")

    for rank, item in enumerate(results, start=1):
        print(f"{rank}. {item['name']} ({item['opportunity_id']})")
        print(f"   Score: {item['score']}")
        print(f"   Risk: {item['risk']}")
        print(f"   Source: {item['source_document']}")
        print(f"   Reasons: {item['reasons']}")
        print()