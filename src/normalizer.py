
import re


def normalize_investment(value):
    """Convert investment amounts to INR."""
    if not value:
        return None

    text = str(value).lower().replace(",", "").replace("₹", "")
    text = text.replace("rs.", "").replace("rs", "").strip()

    match = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lakhs)?", text)
    if not match:
        return None

    amount = float(match.group(1))

    if match.group(2):
        amount *= 100000

    return int(amount) if amount.is_integer() else amount


def normalize_tenure(value):
    """Return tenure minimum and maximum in months."""
    if not value:
        return None, None

    numbers = re.findall(r"\d+(?:\.\d+)?", str(value))
    if not numbers:
        return None, None

    numbers = [float(n) for n in numbers]

    minimum = numbers[0]
    maximum = numbers[1] if len(numbers) > 1 else numbers[0]

    return int(minimum), int(maximum)


def normalize_return(value):
    """Extract minimum and maximum percentage values."""
    if not value:
        return None, None

    numbers = re.findall(r"\d+(?:\.\d+)?", str(value))
    if not numbers:
        return None, None

    numbers = [float(n) for n in numbers]

    minimum = numbers[0]
    maximum = numbers[1] if len(numbers) > 1 else numbers[0]

    return minimum, maximum


def normalize_return_type(value):
    if not value:
        return None

    text = re.sub(r"\s+", " ", str(value).lower()).strip()

    if "notguaranteed" in text.replace(" ", ""):
        return "not guaranteed"

    return text


def normalize_opportunity(raw):
    """Convert one extracted record into the required schema."""
    tenure_min, tenure_max = normalize_tenure(
        raw.get("tenure_raw")
    )

    return_min, return_max = normalize_return(
        raw.get("expected_return_raw")
    )

    return {
        "opportunity_id": raw.get("opportunity_id"),
        "name": raw.get("name"),
        "provider": raw.get("provider"),
        "category": raw.get("category"),
        "minimum_investment_inr": normalize_investment(
            raw.get("minimum_investment_raw")
        ),
        "tenure_min_months": tenure_min,
        "tenure_max_months": tenure_max,
        "risk": raw.get("risk"),
        "expected_return_min_pct": return_min,
        "expected_return_max_pct": return_max,
        "return_type": normalize_return_type(
            raw.get("return_type")
        ),
        "source_document": raw.get("source_document"),
        "extraction_confidence": 1.0 # placeholder for future confidence scoring not implemented yet
    }


if __name__ == "__main__":
    tests = [
        "₹50,000",
        "2 lakh",
        "Rs. 25,000",
        "₹1,000,000"
    ]

    for value in tests:
        print(value, "->", normalize_investment(value))

    print("Tenure:", normalize_tenure("12-24 months"))
    print("Return:", normalize_return("14-18% p.a."))
    print("Return type:", normalize_return_type("notguaranteed"))