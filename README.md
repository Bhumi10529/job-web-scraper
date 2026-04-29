# 🧑‍💻 Job Web Scraper — Fresher & Internship Finder

A Python + Flask web application that automatically collects **fresher-level and internship job postings** published within the **last 7 days** from multiple public job platforms.

---

## 📌 Project Overview

This project demonstrates:
- Web scraping using **BeautifulSoup** and **Requests**
- JSON API integration with public job boards
- Data cleaning, filtering, and deduplication with **Pandas**
- A **Flask** web interface to search and download results
- Modular, professional Python project structure
- Ethical scraping practices

---

## 🗂️ Project Structure


job-web-scraper/
│
├── app.py             # Flask app — entry point, routes, and pipeline orchestration
├── scraper.py         # Scraping logic for each job source
├── utils.py           # Filtering, cleaning, deduplication helpers
├── requirements.txt   # Python dependencies
│
├── data/
│   └── jobs.csv       # Final output CSV (generated after running a search)
│
├── logs/              # Execution logs (generated at runtime)
│
├── static/
│   ├── css/style.css  # Stylesheet
│   └── js/main.js     # Frontend JavaScript
│
├── templates/
│   ├── base.html      # Base layout template
│   ├── index.html     # Search form page
│   └── results.html   # Results display page
│
└── README.md          # This file




## 🛠️ Technologies Used

| Library          | Purpose                                      |
|------------------|----------------------------------------------|
| `flask`          | Web framework — UI, routes, and CSV download |
| `requests`       | HTTP requests to fetch web pages / APIs      |
| `beautifulsoup4` | Parse HTML from Internshala                  |
| `pandas`         | Data cleaning, deduplication, CSV export     |
| `lxml`           | Fast HTML/XML parser used by BeautifulSoup   |
| `tqdm`           | Progress bar in the terminal                 |
| `playwright`     | (Optional) Scraping JavaScript-heavy pages   |



## 🌐 Job Sources

| Source        | Method       | Notes                                      |
|---------------|--------------|--------------------------------------------|
| **Internshala** | HTML scraper | India-focused internships, keyword + location support |
| **RemoteOK**    | JSON API     | Remote jobs globally; all results fetched, filtered locally |
| **Jobicy**      | JSON API     | Remote jobs with tag-based keyword search  |
| **Remotive**    | JSON API     | Remote jobs globally; all results fetched, filtered locally |

---

## ⚙️ Setup & Installation

### 1. Clone or download the project

```bash
git clone https://github.com/your-username/job-web-scraper.git
cd job-web-scraper
```

### 2. Create a virtual environment (recommended)


python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate


### 3. Install dependencies

pip install -r requirements.txt

### 4. (Optional) Install Playwright browsers

Only needed if you extend the project to scrape JavaScript-heavy sites.


playwright install chromium


---

## 🚀 How to Run


python app.py

Then open your browser and go to: **http://localhost:5000**

From the web UI you can:
- Enter a **search keyword** — e.g. `python`, `data analyst`, `marketing` (default: `intern`)
- Enter an optional **location filter** — e.g. `delhi`, `remote`, `mumbai`
- Click **Search** to run the scraping pipeline
- **Download** the results as a CSV file

---

## � API Endpoint

A JSON API is also available for programmatic access:


GET /api/jobs?keyword=python&location=remote


**Response:**
```json
{
  "status": "success",
  "keyword": "python",
  "location": "remote",
  "total_scraped": 87,
  "total_filtered": 34,
  "total_final": 29,
  "jobs": [ ... ]
}
```

---

## 📊 Pipeline Summary

The scraping pipeline runs in this order:

1. **Scrape** — collect jobs from all 4 sources
2. **Filter** — keep only jobs matching the keyword and posted within the last 7 days
3. **Deduplicate** — remove duplicate entries by title + company
4. **Clean** — fill missing fields with sensible defaults
5. **Save** — write results to `data/jobs.csv`

---

## 📋 Data Fields

| Field                  | Description                                              |
|------------------------|----------------------------------------------------------|
| `Job Title`            | Title of the job/internship role                         |
| `Company Name`         | Name of the hiring company                               |
| `Application Link`     | Direct URL to apply                                      |
| `Job Type`             | Internship, Entry-level, or Full-time                    |
| `Work Mode`            | Remote / Onsite / Hybrid                                 |
| `Job Description`      | Brief description of the role                            |
| `Key Responsibilities` | Main tasks expected from the candidate                   |
| `Posted Date`          | Date the job was published (YYYY-MM-DD)                  |
| `Source`               | Which website the job was scraped from                   |

---

## ⚖️ Ethical Scraping Practices

This project follows responsible scraping guidelines:
- ✅ Adds `time.sleep()` delays between requests
- ✅ Uses a realistic `User-Agent` header
- ✅ Only scrapes **publicly available** data
- ✅ Does not overload servers with rapid requests
- ✅ Respects the intent of `robots.txt` policies

---

## 🔧 Extending the Project

- Add more sources by creating a new `scrape_<source>()` function in `scraper.py` and registering it in `app.py`
- Add email notifications when new jobs are found
- Schedule the scraper to run daily using `cron` (Linux) or Task Scheduler (Windows)
- Deploy the Flask app to a cloud platform like Render, Railway, or Heroku
