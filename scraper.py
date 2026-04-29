"""
scraper.py
----------
Scraping logic for all job sources.

Sources:
  1. RemoteOK   — public JSON API (all recent remote jobs)
  2. Jobicy     — public JSON API (supports keyword tag search)
  3. Remotive   — public JSON API (all recent remote jobs)
  4. Internshala — BeautifulSoup HTML scraper (India internships)

Design principle:
  Each scraper collects ALL available jobs for the given keyword
  and returns them as raw dicts. Filtering is handled centrally
  in utils.filter_jobs() — scrapers do NOT pre-filter by seniority.
"""

import time
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils import clean_text, parse_relative_date, is_within_last_7_days

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

DELAY = 1  # seconds between requests


# ══════════════════════════════════════════════════════════
# HELPER — detect job type from title + description
# ══════════════════════════════════════════════════════════

def _detect_job_type(title: str, description: str = "", tags: list = []) -> str:
    """
    Infers job type from title, description, and tags.
    Returns: 'Internship' | 'Entry-level' | 'Full-time'
    """
    text = (title + " " + description + " " + " ".join(tags)).lower()
    if any(k in text for k in ["intern", "internship", "trainee"]):
        return "Internship"
    if any(k in text for k in ["junior", "entry level", "entry-level",
                                "fresher", "graduate", "0-1 year",
                                "associate", "assistant"]):
        return "Entry-level"
    return "Full-time"


# ══════════════════════════════════════════════════════════
# SOURCE 1 — RemoteOK (public JSON API)
# ══════════════════════════════════════════════════════════

def scrape_remoteok(keyword: str = "intern") -> list[dict]:
    """
    Fetches all recent remote jobs from RemoteOK's public JSON API.
    RemoteOK does not support server-side keyword filtering — we fetch
    everything and let filter_jobs() handle matching.
    """
    jobs = []
    url = "https://remoteok.com/api"
    logger.info(f"[RemoteOK] Fetching {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"[RemoteOK] Failed: {e}")
        return jobs

    # First item is a legal notice dict — skip it
    listings = [x for x in data if isinstance(x, dict) and "position" in x]
    logger.info(f"[RemoteOK] {len(listings)} raw listings")

    for item in listings:
        try:
            title       = clean_text(item.get("position", ""))
            company     = clean_text(item.get("company", ""))
            link        = item.get("url") or item.get("apply_url") or "N/A"
            description = clean_text(item.get("description", ""))
            tags        = [t.lower() for t in item.get("tags", [])]

            # Date
            epoch = item.get("epoch", 0)
            posted_date = datetime.utcfromtimestamp(epoch) if epoch else None
            if posted_date and not is_within_last_7_days(posted_date):
                continue  # skip old jobs early

            job_type  = _detect_job_type(title, description, tags)
            work_mode = "Remote"
            resp_text = (description[:300] + "…") if len(description) > 300 else description

            jobs.append({
                "job_title":           title or "N/A",
                "company_name":        company or "N/A",
                "application_link":    link,
                "job_type":            job_type,
                "work_mode":           work_mode,
                "job_description":     description[:500] or "See link for details.",
                "key_responsibilities": resp_text or "Refer to the application link.",
                "posted_date":         posted_date.strftime("%Y-%m-%d") if posted_date else "Unknown",
                "source":              "RemoteOK",
            })
        except Exception as e:
            logger.warning(f"[RemoteOK] Parse error: {e}")

    time.sleep(DELAY)
    logger.info(f"[RemoteOK] {len(jobs)} jobs after date filter")
    return jobs


# ══════════════════════════════════════════════════════════
# SOURCE 2 — Jobicy (public JSON API, supports keyword tag)
# ══════════════════════════════════════════════════════════

def scrape_jobicy(keyword: str = "intern") -> list[dict]:
    """
    Fetches remote jobs from Jobicy's free public API.
    Supports a 'tag' parameter for keyword filtering.
    Docs: https://jobicy.com/jobs-rss-feed
    """
    jobs = []
    # Jobicy supports tag-based search — use the keyword directly
    url = f"https://jobicy.com/api/v2/remote-jobs?count=50&tag={keyword.replace(' ', '+')}"
    logger.info(f"[Jobicy] Fetching {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"[Jobicy] Failed: {e}")
        return jobs

    listings = data.get("jobs", [])
    logger.info(f"[Jobicy] {len(listings)} raw listings for '{keyword}'")

    for item in listings:
        try:
            title       = clean_text(item.get("jobTitle", ""))
            company     = clean_text(item.get("companyName", ""))
            link        = item.get("url", "N/A")
            description = clean_text(item.get("jobDescription", ""))
            tags        = [t.lower() for t in item.get("jobIndustry", [])]

            # Date — Jobicy uses "pubDate": "2026-04-28 12:00:00"
            pub_raw = item.get("pubDate", "")
            try:
                posted_date = datetime.strptime(pub_raw[:10], "%Y-%m-%d") if pub_raw else None
            except ValueError:
                posted_date = None

            if posted_date and not is_within_last_7_days(posted_date):
                continue

            # Work mode
            geo = item.get("jobGeo", "").lower()
            if "hybrid" in geo:
                work_mode = "Hybrid"
            elif "onsite" in geo or "office" in geo:
                work_mode = "Onsite"
            else:
                work_mode = "Remote"

            job_type  = _detect_job_type(title, description, tags)
            resp_text = (description[:300] + "…") if len(description) > 300 else description

            jobs.append({
                "job_title":           title or "N/A",
                "company_name":        company or "N/A",
                "application_link":    link,
                "job_type":            job_type,
                "work_mode":           work_mode,
                "job_description":     description[:500] or "See link for details.",
                "key_responsibilities": resp_text or "Refer to the application link.",
                "posted_date":         posted_date.strftime("%Y-%m-%d") if posted_date else "Unknown",
                "source":              "Jobicy",
            })
        except Exception as e:
            logger.warning(f"[Jobicy] Parse error: {e}")

    time.sleep(DELAY)
    logger.info(f"[Jobicy] {len(jobs)} jobs after date filter")
    return jobs


# ══════════════════════════════════════════════════════════
# SOURCE 3 — Remotive (public JSON API)
# ══════════════════════════════════════════════════════════

def scrape_remotive(keyword: str = "intern") -> list[dict]:
    """
    Fetches remote jobs from Remotive's free public API.
    Returns all recent jobs; keyword matching done in filter_jobs().
    """
    jobs = []
    url = "https://remotive.com/api/remote-jobs?limit=100"
    logger.info(f"[Remotive] Fetching {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"[Remotive] Failed: {e}")
        return jobs

    listings = data.get("jobs", [])
    logger.info(f"[Remotive] {len(listings)} raw listings")

    for item in listings:
        try:
            title       = clean_text(item.get("title", ""))
            company     = clean_text(item.get("company_name", ""))
            link        = item.get("url", "N/A")
            description = clean_text(item.get("description", ""))
            tags        = [t.lower() for t in item.get("tags", [])]

            # Date — "publication_date": "2026-04-28T10:00:00"
            pub_raw = item.get("publication_date", "")
            try:
                posted_date = datetime.strptime(pub_raw[:10], "%Y-%m-%d") if pub_raw else None
            except ValueError:
                posted_date = None

            if posted_date and not is_within_last_7_days(posted_date):
                continue

            job_type  = _detect_job_type(title, description, tags)
            work_mode = "Remote"
            resp_text = (description[:300] + "…") if len(description) > 300 else description

            jobs.append({
                "job_title":           title or "N/A",
                "company_name":        company or "N/A",
                "application_link":    link,
                "job_type":            job_type,
                "work_mode":           work_mode,
                "job_description":     description[:500] or "See link for details.",
                "key_responsibilities": resp_text or "Refer to the application link.",
                "posted_date":         posted_date.strftime("%Y-%m-%d") if posted_date else "Unknown",
                "source":              "Remotive",
            })
        except Exception as e:
            logger.warning(f"[Remotive] Parse error: {e}")

    time.sleep(DELAY)
    logger.info(f"[Remotive] {len(jobs)} jobs after date filter")
    return jobs


# ══════════════════════════════════════════════════════════
# SOURCE 4 — Internshala (BeautifulSoup HTML scraper)
# ══════════════════════════════════════════════════════════

def scrape_internshala(keyword: str = "fresher", location: str = "") -> list[dict]:
    """
    Scrapes internship listings from Internshala using BeautifulSoup.
    All results are tagged as Internship since that's what Internshala lists.
    """
    jobs = []
    base = "https://internshala.com"
    path = f"/internships/keywords-{keyword.replace(' ', '%20')}"
    if location:
        path += f"/location-{location.replace(' ', '%20')}"
    url = base + path
    logger.info(f"[Internshala] Fetching {url}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"[Internshala] Failed: {e}")
        return jobs

    soup  = BeautifulSoup(resp.text, "lxml")
    cards = soup.find_all("div", class_="internship_meta")
    logger.info(f"[Internshala] {len(cards)} cards found")

    for card in cards:
        try:
            title_tag = card.find("h3", class_="job-internship-name")
            title     = clean_text(title_tag.get_text()) if title_tag else "N/A"

            co_tag  = card.find("h4", class_="company-name")
            company = clean_text(co_tag.get_text()) if co_tag else "N/A"

            parent = card.find_parent("div", class_="internship_list_container")
            anchor = parent.find("a", href=True) if parent else None
            link   = (base + anchor["href"]) if anchor else "N/A"

            loc_tag  = card.find("div", id=lambda x: x and "location_names" in x)
            loc_text = clean_text(loc_tag.get_text()).lower() if loc_tag else ""
            work_mode = "Remote" if ("work from home" in loc_text or "remote" in loc_text) else "Onsite"

            date_tag    = card.find("div", class_="status-inactive") or card.find("span", class_="status-success")
            posted_text = clean_text(date_tag.get_text()) if date_tag else ""
            posted_date = parse_relative_date(posted_text)

            stipend_tag = card.find("span", class_="stipend")
            stipend     = clean_text(stipend_tag.get_text()) if stipend_tag else "Not specified"

            dur_tag  = card.find("div", id=lambda x: x and "duration" in str(x))
            duration = clean_text(dur_tag.get_text()) if dur_tag else "N/A"

            jobs.append({
                "job_title":           title,
                "company_name":        company,
                "application_link":    link,
                "job_type":            "Internship",
                "work_mode":           work_mode,
                "job_description":     f"Duration: {duration} | Stipend: {stipend}",
                "key_responsibilities": "Refer to the application link for full details.",
                "posted_date":         posted_date.strftime("%Y-%m-%d") if posted_date else "Unknown",
                "source":              "Internshala",
            })
        except Exception as e:
            logger.warning(f"[Internshala] Parse error: {e}")
        time.sleep(0.2)

    logger.info(f"[Internshala] {len(jobs)} jobs extracted")
    return jobs
