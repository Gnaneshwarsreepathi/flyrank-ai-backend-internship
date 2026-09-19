# The Polite Scraper

FlyRank Internship Backend Track - Week 5 Assignment

## Overview

The Polite Scraper is a Python web scraping pipeline built for the Books to Scrape practice website.

The pipeline follows:

**Classify → Fetch → Extract → Normalize → Validate → Store → Report**

The scraper:

- visits exactly the first 3 catalogue pages
- discovers 60 unique books
- visits all 60 book detail pages
- extracts structured book information
- converts price text into a numeric GBP value
- validates records using Pydantic
- caches HTML during development
- handles failed pages without crashing
- generates JSON output and a run report

## Target Classification

**Target:** Books to Scrape  
**Website:** https://books.toscrape.com/

Books to Scrape is a public practice sandbox specifically designed for web scraping exercises.

### Scope

This project only processes:

- the first 3 catalogue pages
- the 60 books discovered from those pages
- each discovered book's detail page

The scraper does not crawl the entire website.

### Data Collected

For each book, the scraper collects:

- title
- product URL
- original price text
- numeric GBP price
- availability
- rating
- description
- catalogue source page
- fetch timestamp

## robots.txt Result

I checked:

https://books.toscrape.com/robots.txt

No robots file was found.

A missing robots.txt file is not treated as permission to scrape. The target was selected because Books to Scrape is a public sandbox intended for scraping practice.

I will not reuse this code on another site without checking its rules and terms first.

## Technology

Python 3.12

Libraries:

- Requests
- Beautiful Soup
- Pydantic

## Installation

Clone the repository:

```bash
git clone <YOUR-GITHUB-REPO-URL>
cd week-5-polite-scraper
```

Create a virtual environment:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

From the project root:

```bash
python src/main.py
```

The scraper creates:

```text
output/
├── books.json
├── errors.json
└── run-report.json
```

## Record Schema

Each validated book contains:

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "Book description or null",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "UTC timestamp"
}
```

The product URL is used as the canonical identity for deduplication.

## Validation

Pydantic is used to validate normalized records.

Valid records are written to:

```text
output/books.json
```

Validation failures are written to:

```text
output/errors.json
```

The output file is overwritten on each run rather than appended, making the scraper idempotent.

A successful run contains exactly 60 unique books. Running the scraper again still produces 60 records rather than 120.

## Politeness Rules

The scraper follows these rules:

1. Uses an identifying User-Agent.
2. Uses an HTTP request timeout.
3. Checks HTTP response status.
4. Waits at least 500 ms between real requests.
5. Uses local HTML caching during development.
6. Retries timeouts and HTTP 5xx responses only once.
7. Does not retry HTTP 403 or HTTP 404.
8. Limits scraping to the required three catalogue pages.

## Failure Handling

The scraper processes pages independently.

For testing, one deliberately invalid book URL is added.

The invalid URL returns HTTP 404. It is logged and skipped without stopping the scraper.

The 60 valid book records remain available in `books.json`.

## Run Report

Each execution generates:

```text
output/run-report.json
```

The report contains:

- start time
- finish time
- duration
- pages fetched
- cache hits
- valid records
- invalid records
- failed pages
- failure details

A successful Stage 5 test produces 60 valid records and one deliberately failed page.

## Why No Browser Automation?

Browser automation is not required because the book catalogue and product information are already present in the HTML returned by the server.

Using a browser would add unnecessary execution time, memory usage, dependencies, and complexity for data that can be obtained directly through HTTP requests.

## Ethics

When an official API exists and provides the required data, I would prefer the API instead of scraping.

I would not use scraping to bypass authentication, logins, paywalls, access controls, rate limits, or blocking mechanisms.

I would only collect information needed for the stated purpose and would check the site's rules and terms before adapting this scraper to another website.

## Limitation

This scraper depends on the current HTML structure and CSS selectors used by Books to Scrape. If the website changes its markup, some extraction selectors may need to be updated.

## Project Structure

```text
week-5-polite-scraper/
├── src/
│   └── main.py
├── output/
│   ├── books.json
│   ├── errors.json
│   └── run-report.json
├── README.md
├── requirements.txt
└── .gitignore
```

The local `cache/` directory is intentionally excluded from Git.