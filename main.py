#!/usr/bin/env python3
import logging
import time
import argparse
from scraper import CVLVScraper
from database import get_session, JobListing
from analyzer import analyze_team_likelihood

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

def main():
    parser = argparse.ArgumentParser(description='Scrape job listings from cv.lv')
    parser.add_argument('--pages', type=int, default=1, help='Number of pages to scrape')
    parser.add_argument('--delay', type=int, default=2, help='Delay between requests in seconds')
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    args = parser.parse_args()
    
    # Initialize scraper
    base_url = "https://cv.lv/lv/search?limit=20&offset=0&fuzzy=true"
    scraper = CVLVScraper(base_url, delay_range=(args.delay, args.delay + 2), headless=args.headless)
    
    # Initialize database session
    session = get_session()
    
    try:
        # Scrape specified number of pages
        for page in range(1, args.pages + 1):
            logging.info(f"Scraping page {page}...")
            listings = scraper.get_job_listings(page)
            
            for listing in listings:
                try:
                    # Check if the job is already in the database
                    existing_job = session.query(JobListing).filter_by(url=listing['url']).first()
                    if existing_job:
                        logging.info(f"Job already exists: {listing['title']}")
                        continue
                    
                    logging.info(f"Processing: {listing['title']}")
                    
                    # Get detailed information
                    details = scraper.get_job_details(listing['url'])
                    
                    # Skip image-only listings
                    if details.get('is_image_only'):
                        logging.info(f"Skipping image-only listing: {listing['title']}")
                        continue
                    
                    # Analyze team work likelihood
                    team_likelihood = analyze_team_likelihood(
                        listing['title'],
                        details.get('description', ''),
                        details.get('requirements', ''),
                        details.get('responsibilities', '')
                    )
                    
                    # Create job listing object
                    job = JobListing(
                        title=listing['title'],
                        company=listing['company'],
                        location=listing['location'],
                        salary_min=details.get('salary_min', listing['salary_min']),
                        salary_max=details.get('salary_max', listing['salary_max']),
                        description=details.get('description', ''),
                        requirements=details.get('requirements', ''),
                        responsibilities=details.get('responsibilities', ''),
                        benefits=details.get('benefits', ''),
                        deadline=details.get('deadline', ''),
                        team_work_likelihood=team_likelihood,
                        url=listing['url']
                    )
                    
                    # Save to database
                    session.add(job)
                    session.commit()
                    
                    logging.info(f"Saved job: {job.title} (Team likelihood: {team_likelihood:.2f})")
                    
                except Exception as e:
                    logging.error(f"Error processing job {listing.get('title', 'Unknown')}: {e}")
                    session.rollback()
            
            # Wait before fetching the next page
            if page < args.pages:
                time.sleep(args.delay)
                
    except KeyboardInterrupt:
        logging.info("Scraping interrupted by user")
    finally:
        scraper.close()  # Ensure browser is closed
        session.close()
        logging.info("Job scraping completed")

if __name__ == "__main__":
    main()
