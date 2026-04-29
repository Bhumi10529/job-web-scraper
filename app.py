
import os
import io
import logging
import pandas as pd
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    jsonify,
    session,
)

from scraper import scrape_internshala, scrape_remoteok, scrape_jobicy, scrape_remotive
from utils import (
    filter_jobs,
    deduplicate_jobs,
    handle_missing_values,
)

# App setup
app = Flask(__name__)
app.secret_key = "job_scraper_secret_2024"   # needed for session

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# CSV output path
DATA_DIR = "data"
OUTPUT_CSV = os.path.join(DATA_DIR, "jobs.csv")
os.makedirs(DATA_DIR, exist_ok=True)

CSV_COLUMNS = [
    "job_title", "company_name", "application_link",
    "job_type", "work_mode", "job_description",
    "key_responsibilities", "posted_date", "source",
]

# HELPER — run the full scraping pipeline

def run_pipeline(keyword: str, location: str) -> dict:
    """
    Scrape → filter → dedup → clean pipeline.

    Sources:
      - Internshala : HTML scraper, keyword passed in URL
      - RemoteOK    : JSON API, no keyword filter (fetches all recent jobs)
      - Jobicy      : JSON API, supports tag-based keyword search
      - Remotive    : JSON API, fetches all recent remote jobs

    filter_jobs() handles keyword matching centrally.
    """
    all_jobs       = []
    sources_status = []

    sources = [
        ("Internshala", lambda: scrape_internshala(keyword=keyword, location=location)),
        ("RemoteOK",    lambda: scrape_remoteok(keyword=keyword)),
        ("Jobicy",      lambda: scrape_jobicy(keyword=keyword)),
        ("Remotive",    lambda: scrape_remotive(keyword=keyword)),
    ]

    for name, fn in sources:
        try:
            results = fn()
            all_jobs.extend(results)
            sources_status.append({"name": name, "count": len(results), "status": "success"})
            logger.info(f"{name}: {len(results)} jobs")
        except Exception as e:
            logger.error(f"{name} failed: {e}")
            sources_status.append({"name": name, "count": 0, "status": "failed", "error": str(e)})

    total_scraped = len(all_jobs)

    # ── Filter ─────────────────────────────────────────────────────────
    filtered = filter_jobs(all_jobs, keyword=keyword, location=location)
    total_filtered = len(filtered)

    # ── Deduplicate 
    unique = deduplicate_jobs(filtered)

    # ── Clean missing value
    clean = handle_missing_values(unique)
    total_final = len(clean)

    # ── Save CSV 
    if clean:
        df = pd.DataFrame(clean, columns=CSV_COLUMNS)
        df.columns = [c.replace("_", " ").title() for c in df.columns]
        df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
        logger.info(f"CSV saved: {OUTPUT_CSV}")

    return {
        "jobs": clean,
        "total_scraped": total_scraped,
        "total_filtered": total_filtered,
        "total_final": total_final,
        "duplicates_removed": total_filtered - total_final,
        "sources_status": sources_status,
        "keyword": keyword,
        "location": location,
    }

# ROUTES

@app.route("/")
def index():
    """Home page — shows the search form."""
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    """
    Handles form submission.
    Runs the scraping pipeline and renders the results page.
    """
    keyword  = request.form.get("keyword", "intern").strip() or "intern"
    location = request.form.get("location", "").strip()

    logger.info(f"Search request — keyword='{keyword}', location='{location}'")

    result = run_pipeline(keyword, location)

    # Store summary in session so the download route can reference it
    session["last_keyword"]  = keyword
    session["last_location"] = location

    return render_template("results.html", **result)


@app.route("/download")
def download():
    """
    Streams the saved CSV file as a download.
    Falls back gracefully if no CSV exists yet.
    """
    if not os.path.exists(OUTPUT_CSV):
        return redirect(url_for("index"))

    return send_file(
        OUTPUT_CSV,
        mimetype="text/csv",
        as_attachment=True,
        download_name="fresher_jobs.csv",
    )


@app.route("/api/jobs")
def api_jobs():
    """
    JSON API endpoint — returns the last scraped results.
    Useful for testing or extending the project.

    Query params:
      keyword  (str)  : search keyword
      location (str)  : location filter
    """
    keyword  = request.args.get("keyword", "intern").strip()
    location = request.args.get("location", "").strip()

    result = run_pipeline(keyword, location)
    return jsonify({
        "status": "success",
        "keyword": keyword,
        "location": location,
        "total_scraped": result["total_scraped"],
        "total_filtered": result["total_filtered"],
        "total_final": result["total_final"],
        "jobs": result["jobs"],
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
