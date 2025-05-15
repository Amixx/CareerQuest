# CV.lv Job Listings Scraper

This script scrapes job listings from cv.lv, processes the data, and stores it in a SQLite database.

## Features

- Scrapes job listings from cv.lv
- Extracts detailed information including salary, requirements, responsibilities, and benefits
- Analyzes whether the job is likely to be team-based or individual work
- Stores data in a SQLite database

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the main script:

```bash
python main.py --pages 5 --delay 2
```

Arguments:

- `--pages`: Number of pages to scrape (default: 1)
- `--delay`: Delay between requests in seconds (default: 2)

## Database

The data is stored in a SQLite database (`job_listings.db`) with the following structure:

- `id`: Primary key
- `title`: Job title
- `company`: Company name
- `location`: Job location
- `salary_min`: Minimum salary
- `salary_max`: Maximum salary
- `description`: Full job description
- `requirements`: Job requirements
- `responsibilities`: Job responsibilities
- `benefits`: Benefits offered
- `deadline`: Application deadline
- `team_work_likelihood`: Score indicating likelihood of teamwork (0-1)
- `url`: URL of the job listing
- `scraped_at`: Timestamp when the data was scraped

## Team Work Analysis

The script analyzes job descriptions to determine if the job is more likely to be team-based or individual work. This analysis is based on keywords in Latvian and English that indicate:

- Team work: 'komanda', 'team', 'collaborate', 'koordinēt', etc.
- Individual work: 'patstāvīgi', 'independent', 'autonoms', etc.

The result is a score between 0 and 1, where values closer to 1 indicate team work and values closer to 0 indicate individual work.
