
import re
from pathlib import Path


# Folder containing the 30 opportunity documents
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "opportunities"


def read_document(file_path):
    """Read one opportunity document as text."""
    return file_path.read_text(encoding="utf-8")



def extract_header(text):
    """Extract header fields from common document layouts."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    record = {
        "opportunity_id": None,
        "name": None,
        "provider": None,
        "category": None,
    }

    if not lines:
        return record

    # Format 1: OPP001: Opportunity Name
    match = re.match(
        r"^(OPP\d+)\s*[:\-]\s*(.+)$",
        lines[0],
        flags=re.IGNORECASE,
    )

    if match:
        record["opportunity_id"] = match.group(1).upper()
        record["name"] = match.group(2).strip()
    else:
        # Format 2: ID and name on separate lines
        if re.fullmatch(r"OPP\d+", lines[0], flags=re.IGNORECASE):
            record["opportunity_id"] = lines[0].upper()

            if len(lines) > 1:
                record["name"] = lines[1]

    for line in lines:
        match = re.match(
            r"^(Provider|Category)\s*:\s*(.+)$",
            line,
            flags=re.IGNORECASE,
        )

        if match:
            record[match.group(1).lower()] = match.group(2).strip()

    return record


def find_first(patterns, text, flags=re.IGNORECASE):
    """Return the first matching text, or None."""
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match.group(1).strip()
    return None



def extract_financial_details(text):
    """Extract raw financial details without normalizing them."""

    amount_pattern = (
        r"(?:₹|Rs\.?\s*)?\s*[\d,]+(?:\.\d+)?"
        r"(?:\s*(?:lakh|lakhs|crore|crores))?"
    )

    minimum_investment = find_first(
        [
            rf"(?:minimum investment|minimum amount|entry ticket|"
            rf"ticket size starts at|investors may participate from)"
            rf"\s*(?:is|of|starts at|from|:)?\s*({amount_pattern})",
        ],
        text,
    )

    tenure = find_first(
        [
            r"(\d+\s*(?:to|[-–—])\s*\d+\s*months?)",
            r"(\d+\s*months?)",
            r"(\d+\s*(?:to|[-–—])\s*\d+\s*years?)",
            r"(\d+\s*years?)",
        ],
        text,
    )

    risk = find_first(
        [
            r"(?:risk classification|risk(?:\s*level|\s*profile)?|"
            r"classified as)\s*(?:is|:)?\s*"
            r"(Low\s+to\s+Moderate|Moderate\s*[-–—]\s*High|"
            r"Moderate\s+to\s+High|Moderately\s+High|"
            r"Moderately\s+Low|Very\s+High|Very\s+Low|"
            r"Low|Moderate|Medium|High)",

            r"\b(Low\s+to\s+Moderate|Moderate\s*[-–—]\s*High|"
            r"Moderate\s+to\s+High|Moderately\s+High|"
            r"Moderately\s+Low|Very\s+High|Very\s+Low)\s+risk\b",
        ],
        text,
    )


    expected_return = find_first(
        [
            # Range: 14-18% or 14%-18%
            r"(\d+(?:\.\d+)?\s*%?\s*"
            r"(?:to|[-–—])\s*\d+(?:\.\d+)?\s*%"
            r"(?:\s*p\.?a\.?)?)",

            # Single value: 9.2% p.a. or 9.2% per annum
            r"(\d+(?:\.\d+)?\s*%\s*"
            r"(?:p\.?a\.?|per annum))",

            # Fallback: a percentage without a return period
            r"(\d+(?:\.\d+)?\s*%)",
        ],
        text,
    )

    lower_text = text.lower()
    return_type = None

    if expected_return:
        if re.search(r"not\s+guaranteed", lower_text):
            return_type = "not guaranteed"
        elif "historical" in lower_text:
            return_type = "historical"
        elif "illustrative" in lower_text:
            return_type = "illustrative"
        elif "coupon" in lower_text:
            return_type = "coupon"
        elif "variable" in lower_text:
            return_type = "variable"
        elif re.search(r"\bguaranteed\b", lower_text):
            return_type = "guaranteed"
        else:
            return_type = "unspecified"

    return {
        "minimum_investment_raw": minimum_investment,
        "tenure_raw": tenure,
        "risk": risk,
        "expected_return_raw": expected_return,
        "return_type": return_type,
    }


def extract_opportunity(file_path):
    """Extract one opportunity into a preliminary record."""
    text = read_document(file_path)

    record = extract_header(text)
    record.update(extract_financial_details(text))
    record["source_document"] = file_path.name

    return record


def extract_all_opportunities():
    """Extract all supported text documents in the data folder."""
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Opportunity folder not found: {DATA_DIR}"
        )

    files = sorted(
        path for path in DATA_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}
    )

    records = [extract_opportunity(path) for path in files]
    return records


if __name__ == "__main__":
    records = extract_all_opportunities()

    print(f"Documents found: {len(records)}")

    for record in records:
        print("-" * 50)
        print(record)