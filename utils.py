
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

FRESHER_KEYWORDS = [
    "fresher", "fresh graduate", "entry level", "entry-level",
    "intern", "internship", "trainee", "graduate", "junior",
    "0 years", "0-1 year", "no experience", "beginner", "entry",
]

# ── TEXT CLEANING 

def clean_text(text: str) -> str:
    """Remove non-printable chars and collapse whitespace."""
    if not text:
        return ""
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── DATE PARSING

def parse_relative_date(date_text: str) -> datetime | None:
    """Convert relative date strings like '2 days ago' to datetime objects."""
    if not date_text:
        return None

    text = date_text.lower().strip()
    now  = datetime.now()

    if any(kw in text for kw in ["just", "today", "hour", "minute", "second"]):
        return now
    if "yesterday" in text:
        return now - timedelta(days=1)

    m = re.search(r"(\d+)\s*day", text)
    if m:
        return now - timedelta(days=int(m.group(1)))

    m = re.search(r"(\d+)\s*week", text)
    if m:
        return now - timedelta(weeks=int(m.group(1)))

    m = re.search(r"(\d+)\s*month", text)
    if m:
        return now - timedelta(days=int(m.group(1)) * 30)

    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    logger.debug(f"Could not parse date: '{date_text}'")
    return None


def is_within_last_7_days(date: datetime) -> bool:
    """Return True if date is within the last 7 days."""
    return date >= datetime.now() - timedelta(days=7)


# ── JOB FILTERING 

def filter_jobs(jobs: list[dict], keyword: str = "", location: str = "") -> list[dict]:
    
    filtered      = []
    keyword_lower = keyword.lower().strip()

    # These broad keywords mean "show me everything recent" — no text filter
    BROAD = {
        "intern", "internship", "fresher", "junior", "entry level",
        "entry-level", "graduate", "trainee", "beginner", "entry", "",
    }
    is_broad = keyword_lower in BROAD

    for job in jobs:

        # 1. Date filter 
        posted_str = job.get("posted_date", "")
        if posted_str and posted_str != "Unknown":
            try:
                posted_dt = datetime.strptime(posted_str, "%Y-%m-%d")
                if not is_within_last_7_days(posted_dt):
                    continue
            except ValueError:
                pass  # keep if unparseable

        # 2. Keyword filter 
        if not is_broad:
            title = job.get("job_title", "").lower()
            desc  = job.get("job_description", "").lower()
            blob  = f"{title} {desc}"

            # Split keyword into words, match if ANY significant word found
            kw_words = [w for w in keyword_lower.split() if len(w) > 2]
            full_match = keyword_lower in blob
            part_match = any(w in blob for w in kw_words)

            if not full_match and not part_match:
                continue

        # 3. Location filter
        if location:
            work_mode = job.get("work_mode", "").lower()
            if work_mode != "remote":
                loc_blob = job.get("location", "").lower() + " " + work_mode
                if location.lower() not in loc_blob:
                    continue

        filtered.append(job)

    return filtered


# ── DEDUPLICATION 

def deduplicate_jobs(jobs: list[dict]) -> list[dict]:
    """Remove duplicates using composite key: normalised title + company."""
    seen       = set()
    unique     = []

    for job in jobs:
        t_key = re.sub(r"[^a-z0-9]", "", job.get("job_title",    "").lower())
        c_key = re.sub(r"[^a-z0-9]", "", job.get("company_name", "").lower())
        key   = f"{t_key}|{c_key}"

        if key not in seen:
            seen.add(key)
            unique.append(job)
        else:
            logger.debug(f"Duplicate: {job.get('job_title')} @ {job.get('company_name')}")

    return unique


# ── MISSING VALUE HANDLING 

def handle_missing_values(jobs: list[dict]) -> list[dict]:
    """Fill empty/missing fields with sensible defaults."""
    defaults = {
        "job_title":           "Not specified",
        "company_name":        "Not specified",
        "application_link":    "N/A",
        "job_type":            "Not specified",
        "work_mode":           "Not specified",
        "job_description":     "No description available.",
        "key_responsibilities": "Refer to the application link.",
        "posted_date":         "Unknown",
        "source":              "Unknown",
    }
    cleaned = []
    for job in jobs:
        clean_job = {
            field: (job.get(field) or "").strip() or default
            for field, default in defaults.items()
        }
        cleaned.append(clean_job)
    return cleaned


# ── SUMMARY PRINTER 

def print_summary(total_scraped: int, total_filtered: int, total_deduplicated: int) -> None:
    """Print a formatted pipeline summary to stdout."""
    print("\n" + "=" * 50)
    print("         📊  SCRAPING SUMMARY")
    print("=" * 50)
    print(f"  Total jobs scraped       : {total_scraped}")
    print(f"  After filtering          : {total_filtered}")
    print(f"  After deduplication      : {total_deduplicated}")
    print(f"  Duplicates removed       : {total_filtered - total_deduplicated}")
    print("=" * 50 + "\n")
