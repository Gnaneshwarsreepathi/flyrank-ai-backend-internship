import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError


# =========================================================
# CONFIGURATION
# =========================================================

BASE_URL = "https://books.toscrape.com"
START_URL = f"{BASE_URL}/catalogue/page-1.html"

HEADERS = {
    "User-Agent": (
        "FlyRankInternship-A9/1.0 "
        "(educational scraping project)"
    )
}

REQUEST_TIMEOUT = 10
REQUEST_DELAY = 1.0

CACHE_DIR = Path("cache")
OUTPUT_DIR = Path("output")

CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# =========================================================
# RUN STATISTICS
# =========================================================

run_stats = {
    "pages_fetched": 0,
    "cache_hits": 0,
    "failed_pages": []
}


# =========================================================
# PYDANTIC MODEL
# =========================================================

class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: HttpUrl
    fetched_at: str


# =========================================================
# CACHE
# =========================================================

def get_cache_path(url: str) -> Path:

    url_hash = hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()

    return CACHE_DIR / f"{url_hash}.html"


# =========================================================
# FETCH PAGE
# =========================================================

def fetch_page(url: str) -> str | None:
    """
    Fetch one page safely.

    Rules:
    - use cache when available
    - timeout on requests
    - only HTTP 200 is success
    - retry timeout / 5xx once
    - do not retry 403 / 404
    - wait between real requests
    - record failures
    """

    cache_path = get_cache_path(url)

    # -----------------------------------------------------
    # CACHE
    # -----------------------------------------------------

    if cache_path.exists():

        try:

            html = cache_path.read_text(
                encoding="utf-8"
            )

            run_stats["cache_hits"] += 1

            print(
                f"CACHE HIT: {url} "
                f"size={len(html)}"
            )

            return html

        except OSError as error:

            print(
                f"CACHE READ ERROR: {error}"
            )

    # Maximum two attempts:
    # original request + one retry
    for attempt in range(1, 3):

        try:

            print(
                f"FETCH: {url} "
                f"attempt={attempt}"
            )

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )

            run_stats["pages_fetched"] += 1

            status = response.status_code

            # ---------------------------------------------
            # SUCCESS
            # ---------------------------------------------

            if status == 200:

                html = response.text

                try:

                    cache_path.write_text(
                        html,
                        encoding="utf-8"
                    )

                except OSError as error:

                    print(
                        "CACHE WRITE ERROR: "
                        f"{error}"
                    )

                print(
                    f"FETCHED: {url} "
                    f"status=200 "
                    f"size={len(html)}"
                )

                time.sleep(
                    REQUEST_DELAY
                )

                return html

            # ---------------------------------------------
            # DO NOT RETRY 403 / 404
            # ---------------------------------------------

            if status in (403, 404):

                print(
                    f"FAILED: {url} "
                    f"status={status} "
                    f"no_retry=True"
                )

                record_failure(
                    url,
                    f"HTTP {status}"
                )

                return None

            # ---------------------------------------------
            # RETRY SERVER 5xx ONCE
            # ---------------------------------------------

            if 500 <= status <= 599:

                print(
                    f"SERVER ERROR: "
                    f"{url} status={status}"
                )

                if attempt == 1:

                    print(
                        "RETRY: waiting "
                        "2 seconds..."
                    )

                    time.sleep(2)

                    continue

                record_failure(
                    url,
                    f"HTTP {status}"
                )

                return None

            # ---------------------------------------------
            # OTHER NON-200
            # ---------------------------------------------

            print(
                f"FAILED: {url} "
                f"status={status}"
            )

            record_failure(
                url,
                f"HTTP {status}"
            )

            return None

        # -------------------------------------------------
        # TIMEOUT -> RETRY ONCE
        # -------------------------------------------------

        except requests.Timeout:

            print(
                f"TIMEOUT: {url}"
            )

            if attempt == 1:

                print(
                    "RETRY: waiting "
                    "2 seconds..."
                )

                time.sleep(2)

                continue

            record_failure(
                url,
                "Request timeout"
            )

            return None

        # -------------------------------------------------
        # OTHER REQUEST ERROR
        # -------------------------------------------------

        except requests.RequestException as error:

            print(
                f"REQUEST ERROR: "
                f"{url} error={error}"
            )

            record_failure(
                url,
                str(error)
            )

            return None

    return None


# =========================================================
# FAILURE TRACKING
# =========================================================

def record_failure(
    url: str,
    reason: str
):
    """
    Record each failed URL once.
    """

    for failure in run_stats[
        "failed_pages"
    ]:

        if failure["url"] == url:
            return

    run_stats[
        "failed_pages"
    ].append(
        {
            "url": url,
            "reason": reason
        }
    )


# =========================================================
# DISCOVER BOOKS
# =========================================================

def discover_books():

    current_url = START_URL

    catalogue_pages = 0
    discovered_books = []

    while (
        current_url
        and catalogue_pages < 3
    ):

        print()
        print(
            "CATALOGUE PAGE "
            f"{catalogue_pages + 1}"
        )

        html = fetch_page(
            current_url
        )

        if html is None:
            break

        catalogue_pages += 1

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        book_links = soup.select(
            "article.product_pod h3 a"
        )

        for link in book_links:

            href = link.get("href")

            if href:

                product_url = urljoin(
                    current_url,
                    href
                )

                discovered_books.append(
                    {
                        "product_url":
                            product_url,

                        "source_page":
                            current_url
                    }
                )

        print(
            f"Page {catalogue_pages}: "
            f"{len(book_links)} books"
        )

        if catalogue_pages >= 3:
            break

        next_link = soup.select_one(
            "li.next a"
        )

        if next_link:

            href = next_link.get(
                "href"
            )

            current_url = (
                urljoin(
                    current_url,
                    href
                )
                if href
                else None
            )

        else:

            current_url = None

    # Deduplicate by product URL

    unique = {}

    for book in discovered_books:

        unique[
            book["product_url"]
        ] = book

    result = list(
        unique.values()
    )

    print()
    print("==============================")
    print("DISCOVERY SUMMARY")
    print("==============================")

    print(
        f"catalogue_pages="
        f"{catalogue_pages}"
    )

    print(
        f"discovered="
        f"{len(discovered_books)}"
    )

    print(
        f"unique_urls="
        f"{len(result)}"
    )

    return result


# =========================================================
# EXTRACT ONE BOOK
# =========================================================

def extract_book(
    product_url: str,
    source_page: str
):

    html = fetch_page(
        product_url
    )

    if html is None:

        print(
            f"SKIPPED: {product_url}"
        )

        return None

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    product = soup.select_one(
        "div.product_main"
    )

    if product is None:

        record_failure(
            product_url,
            "Product section not found"
        )

        return None

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title_element = (
        product.select_one("h1")
    )

    title = (
        title_element.get_text(
            strip=True
        )
        if title_element
        else None
    )

    # -----------------------------------------------------
    # PRICE
    # -----------------------------------------------------

    price_element = (
        product.select_one(
            "p.price_color"
        )
    )

    price_text = (
        price_element.get_text(
            strip=True
        )
        if price_element
        else None
    )

    # -----------------------------------------------------
    # AVAILABILITY
    # -----------------------------------------------------

    availability_element = (
        product.select_one(
            "p.availability"
        )
    )

    availability_text = (
        availability_element.get_text(
            " ",
            strip=True
        )
        if availability_element
        else None
    )

    # -----------------------------------------------------
    # RATING
    # -----------------------------------------------------

    rating_text = None

    rating_element = (
        product.select_one(
            "p.star-rating"
        )
    )

    if rating_element:

        classes = rating_element.get(
            "class",
            []
        )

        for class_name in classes:

            if (
                class_name
                != "star-rating"
            ):

                rating_text = (
                    class_name
                )

                break

    # -----------------------------------------------------
    # DESCRIPTION
    # -----------------------------------------------------

    description = None

    description_heading = soup.find(
        "div",
        id="product_description"
    )

    if description_heading:

        description_element = (
            description_heading
            .find_next_sibling("p")
        )

        if description_element:

            description = (
                description_element
                .get_text(
                    " ",
                    strip=True
                )
            )

    # -----------------------------------------------------
    # TIMESTAMP
    # -----------------------------------------------------

    fetched_at = datetime.now(
        timezone.utc
    ).isoformat().replace(
        "+00:00",
        "Z"
    )

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text":
            availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }


# =========================================================
# EXTRACT ALL
# =========================================================

def extract_all_books(
    discovered_books
):

    records = []

    total = len(
        discovered_books
    )

    for index, book in enumerate(
        discovered_books,
        start=1
    ):

        print()
        print(
            "------------------------------"
        )

        print(
            f"BOOK {index}/{total}"
        )

        try:

            record = extract_book(
                book["product_url"],
                book["source_page"]
            )

            if record is not None:

                records.append(
                    record
                )

        except Exception as error:

            # One broken page must not
            # crash the whole scraper.

            print(
                f"BOOK ERROR: "
                f"{error}"
            )

            record_failure(
                book["product_url"],
                str(error)
            )

    return records


# =========================================================
# PRICE NORMALIZATION
# =========================================================

def normalize_price(
    price_text: str
) -> float:

    if not price_text:

        raise ValueError(
            "Missing price"
        )

    cleaned = (
        price_text
        .replace("£", "")
        .strip()
    )

    return float(cleaned)


# =========================================================
# VALIDATION
# =========================================================

def validate_records(
    raw_records
):

    valid_records = []
    errors = []

    for record in raw_records:

        try:

            normalized = {
                **record,

                "price_gbp":
                    normalize_price(
                        record.get(
                            "price_text"
                        )
                    )
            }

            validated = BookRecord(
                **normalized
            )

            valid_records.append(
                validated.model_dump(
                    mode="json"
                )
            )

        except (
            ValidationError,
            ValueError,
            TypeError
        ) as error:

            errors.append(
                {
                    "product_url":
                        record.get(
                            "product_url"
                        ),

                    "reason":
                        str(error)
                }
            )

    return (
        valid_records,
        errors
    )


# =========================================================
# DEDUPLICATE
# =========================================================

def deduplicate_records(
    records
):

    unique = {}

    for record in records:

        unique[
            record["product_url"]
        ] = record

    return list(
        unique.values()
    )


# =========================================================
# SAVE JSON
# =========================================================

def save_json(
    filename,
    data
):

    path = OUTPUT_DIR / filename

    with path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"SAVED: {path}"
    )


# =========================================================
# RUN REPORT
# =========================================================

def create_run_report(
    started_at,
    start_time,
    valid_records,
    errors
):

    finished_at = datetime.now(
        timezone.utc
    )

    duration = round(
        time.time() - start_time,
        2
    )

    report = {
        "started_at":
            started_at,

        "finished_at":
            finished_at
            .isoformat()
            .replace(
                "+00:00",
                "Z"
            ),

        "duration_seconds":
            duration,

        "pages_fetched":
            run_stats[
                "pages_fetched"
            ],

        "cache_hits":
            run_stats[
                "cache_hits"
            ],

        "valid_records":
            len(valid_records),

        "invalid_records":
            len(errors),

        "failed_pages":
            len(
                run_stats[
                    "failed_pages"
                ]
            ),

        "failures":
            run_stats[
                "failed_pages"
            ]
    }

    save_json(
        "run-report.json",
        report
    )

    return report


# =========================================================
# MAIN
# =========================================================

def main():

    # Reset counters in case main()
    # is reused in the same process.

    run_stats[
        "pages_fetched"
    ] = 0

    run_stats[
        "cache_hits"
    ] = 0

    run_stats[
        "failed_pages"
    ] = []

    start_time = time.time()

    started_at = datetime.now(
        timezone.utc
    ).isoformat().replace(
        "+00:00",
        "Z"
    )

    print()
    print("==============================")
    print("THE POLITE SCRAPER")
    print("STAGE 5")
    print("==============================")

    # -----------------------------------------------------
    # DISCOVER REAL BOOKS
    # -----------------------------------------------------

    discovered_books = (
        discover_books()
    )

    print()
    print(
        f"Real books discovered="
        f"{len(discovered_books)}"
    )

    # -----------------------------------------------------
    # DELIBERATE BROKEN URL TEST
    # -----------------------------------------------------

    fake_book = {
        "product_url": (
            "https://books.toscrape.com/"
            "catalogue/"
            "flyrank-deliberately-broken-book/"
            "index.html"
        ),

        "source_page":
            START_URL
    }

    books_to_process = (
        discovered_books
        + [fake_book]
    )

    print()
    print(
        "Added one deliberate "
        "broken URL for Stage 5."
    )

    print(
        f"URLs to process="
        f"{len(books_to_process)}"
    )

    # -----------------------------------------------------
    # EXTRACT
    # -----------------------------------------------------

    raw_records = (
        extract_all_books(
            books_to_process
        )
    )

    # -----------------------------------------------------
    # VALIDATE
    # -----------------------------------------------------

    valid_records, errors = (
        validate_records(
            raw_records
        )
    )

    valid_records = (
        deduplicate_records(
            valid_records
        )
    )

    # -----------------------------------------------------
    # SAVE GOOD + INVALID DATA
    # -----------------------------------------------------

    save_json(
        "books.json",
        valid_records
    )

    save_json(
        "errors.json",
        errors
    )

    # -----------------------------------------------------
    # RUN REPORT
    # -----------------------------------------------------

    report = create_run_report(
        started_at,
        start_time,
        valid_records,
        errors
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print()
    print("==============================")
    print("STAGE 5 SUMMARY")
    print("==============================")

    print(
        f"valid_records="
        f"{len(valid_records)}"
    )

    print(
        f"invalid_records="
        f"{len(errors)}"
    )

    print(
        f"failed_pages="
        f"{report['failed_pages']}"
    )

    print(
        f"pages_fetched="
        f"{report['pages_fetched']}"
    )

    print(
        f"cache_hits="
        f"{report['cache_hits']}"
    )

    print(
        f"duration_seconds="
        f"{report['duration_seconds']}"
    )

    print()

    if (
        len(valid_records) == 60
        and report[
            "failed_pages"
        ] == 1
    ):

        print(
            "STAGE 5 CHECK: PASS"
        )

    else:

        print(
            "STAGE 5 CHECK: "
            "REVIEW REQUIRED"
        )

    print()
    print(
        "Output files:"
    )

    print(
        "output/books.json"
    )

    print(
        "output/errors.json"
    )

    print(
        "output/run-report.json"
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()