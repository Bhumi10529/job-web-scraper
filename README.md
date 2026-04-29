# 🧑‍💻 Job Web Scraper — Fresher & Internship Finder

A Python-based web scraping system that automatically collects **fresher-level and internship job postings** published within the **last 7 days** from multiple public job platforms.

---

## 📌 Project Overview

This project was built as an academic practical to demonstrate:
- Web scraping using **BeautifulSoup** and **Requests**
- Data cleaning and filtering with **Pandas**
- Modular, professional Python project structure
- Ethical scraping practices

---

## 🗂️ Project Structure

```
job-web-scraper/
│
├── main.py            # Entry point — orchestrates the full pipeline
├── scraper.py         # Scraping logic for each job source
├── utils.py           # Filtering, cleaning, deduplication helpers
├── requirements.txt   # Python dependencies
│
├── data/
│   └── jobs.csv       # Final output CSV (generated after running)
│
├── logs/
│   └── scraper.log    # Execution log (generated after running)
│
└── README.md          # This file
```

---

## 🛠️ Technologies Used

| Library         | Purpose                                      |
|-----------------|----------------------------------------------|
| `requests`      | HTTP requests to fetch web pages / APIs      |
| `beautifulsoup4`| Parse HTML from static web pages             |
| `pandas`        | Data cleaning, deduplication, CSV export     |
| `tqdm`          | Progress bar in the terminal                 |
| `playwright`    | (Optional) Scraping JavaScript-heavy pages   |
| `lxml`          | Fast HTML/XML parser used by BeautifulSoup   |

---

## ⚙️ Setup & Installation

### 1. Clone or download the project

```bash
git clone https://github.com/your-username/job-web-scraper.git
cd job-web-scraper
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Install Playwright browsers

Only needed if you extend the project to scrape JavaScript-heavy sites.

```bash
playwright install chromium
```

---

## 🚀 How to Run

```bash
python main.py
```

You will be prompted to enter:
- **Search keyword** — e.g. `python`, `data analyst`, `marketing` (default: `intern`)
- **Location filter** — e.g. `delhi`, `remote`, `mumbai` (default: any)

The scraper will then:
1. Collect jobs from **Internshala**, **RemoteOK**, and **Himalayas**
2. Filter to only fresher/intern roles posted in the **last 7 days**
3. Remove duplicate entries
4. Save results to `data/jobs.csv`
5. Print a summary in the terminal

---

## 📊 Sample Output

### Terminal Summary

```
==================================================
         📊  SCRAPING SUMMARY
==================================================
  Total jobs scraped       : 87
  After filtering          : 34
  After deduplication      : 29
  Duplicates removed       : 5
==================================================
```

### CSV Preview (`data/jobs.csv`)

| Job Title              | Company Name   | Application Link          | Job Type    | Work Mode | Posted Date |
|------------------------|----------------|---------------------------|-------------|-----------|-------------|
| Python Intern          | TechCorp       | https://remoteok.com/...  | Internship  | Remote    | 2025-04-27  |
| Junior Data Analyst    | DataHub Inc    | https://himalayas.app/... | Full-time   | Remote    | 2025-04-26  |
| Software Trainee       | StartupXYZ     | https://internshala.com/..| Internship  | Onsite    | 2025-04-25  |

---

## 📋 Data Fields Explained

| Field                 | Description                                              |
|-----------------------|----------------------------------------------------------|
| `Job Title`           | Title of the job/internship role                         |
| `Company Name`        | Name of the hiring company                               |
| `Application Link`    | Direct URL to apply or contact email                     |
| `Job Type`            | Internship or Full-time                                  |
| `Work Mode`           | Remote / Onsite / Hybrid                                 |
| `Job Description`     | Brief description of the role                            |
| `Key Responsibilities`| Main tasks expected from the candidate                   |
| `Posted Date`         | Date the job was published (YYYY-MM-DD)                  |
| `Source`              | Which website the job was scraped from                   |

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

- Add more sources by creating a new `scrape_<source>()` function in `scraper.py`
- Add email notifications when new jobs are found
- Schedule the scraper to run daily using `cron` (Linux) or Task Scheduler (Windows)
- Build a simple web dashboard using Flask or Streamlit

---

## 🎓 Viva Questions & Answers

### Q1. What is web scraping?
**A:** Web scraping is the automated process of extracting data from websites using code. Instead of manually copying information, a program sends HTTP requests, downloads the HTML, and parses the content to extract specific data.

---

### Q2. What is BeautifulSoup and why did you use it?
**A:** BeautifulSoup is a Python library that parses HTML and XML documents. It creates a parse tree from the page source, making it easy to find and extract specific elements using tag names, class names, or CSS selectors. We used it to extract job titles, company names, and dates from Internshala's HTML.

---

### Q3. What is the difference between static and dynamic scraping?
**A:** Static scraping (using Requests + BeautifulSoup) works when the page content is present in the initial HTML response. Dynamic scraping (using Playwright or Selenium) is needed when content is loaded by JavaScript after the page loads. Internshala is mostly static; sites like LinkedIn require dynamic scraping.

---

### Q4. How did you filter jobs to only show the last 7 days?
**A:** Each job has a `posted_date` field. We parse relative strings like "2 days ago" into actual `datetime` objects using the `parse_relative_date()` function in `utils.py`. Then we compare the date against `datetime.now() - timedelta(days=7)`. Jobs older than 7 days are excluded.

---

### Q5. How did you remove duplicate job entries?
**A:** We created a composite key by combining the normalised job title and company name (lowercased, punctuation removed). We stored seen keys in a Python `set`. If a job's key was already in the set, it was skipped. This is implemented in the `deduplicate_jobs()` function in `utils.py`.

---

### Q6. What is Pandas and how did you use it here?
**A:** Pandas is a Python data analysis library. We used it to convert our list of job dictionaries into a `DataFrame` and then export it as a CSV file using `df.to_csv()`. It also makes it easy to rename columns and handle encoding for Excel compatibility.

---

### Q7. What ethical rules did you follow during scraping?
**A:** We added `time.sleep()` delays between requests to avoid overloading servers, used a realistic browser `User-Agent` header, only scraped publicly available data, and avoided scraping at high frequency. We also checked that the sites we scraped do not explicitly prohibit scraping in their terms.

---

### Q8. What is the purpose of the `User-Agent` header?
**A:** The `User-Agent` header tells the server what browser or client is making the request. Many websites block requests that don't have a valid User-Agent (since they look like bots). By setting a realistic browser User-Agent, our requests appear to come from a normal web browser.

---

### Q9. What happens if a field is missing from a scraped job?
**A:** The `handle_missing_values()` function in `utils.py` checks every required field. If a field is empty or missing, it fills it with a sensible default (e.g., "Not specified" for job type, "N/A" for links). This ensures the CSV has no blank cells.

---

### Q10. How would you scale this project to scrape thousands of jobs?
**A:** We could use `concurrent.futures` or `asyncio` for parallel requests, add a database (SQLite or PostgreSQL) instead of CSV for storage, implement rotating proxies and rate limiting, use a job queue (like Celery), and schedule runs with a cron job. We'd also add retry logic for failed requests.

---

## 👨‍🎓 Author

Built as an academic practical project demonstrating Python web scraping, data engineering, and software design principles.
