#!/usr/bin/env python3
import logging
import time
import argparse
from scraper import CVLVScraper
from database import get_session, JobListing
from analyzer import (
    analyze_teamwork_preference, analyze_learning_opportunity, analyze_company_size,
    analyze_remote_preference, analyze_career_growth, analyze_project_type,
    analyze_experience_required, analyze_stress_level, analyze_creativity_required, analyze_work_environment
)

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
                # Check if the job is already in the database
                existing_job = session.query(JobListing).filter_by(url=listing['url']).first()
                if existing_job:
                    logging.info(f"Job already exists: {listing['title']}")
                    continue
                
                logging.info(f"Processing: {listing['title']}")
                
                # Get detailed information
                details = scraper.get_job_details(listing['title'], listing['url'])
                
                # Skip image-only listings
                if details.get('is_image_only'):
                    logging.info(f"Skipping image-only listing: {listing['title']}")
                    continue
                
                # Extract text fields for analysis
                description = details.get('description', '')
                requirements = details.get('requirements', '')
                responsibilities = details.get('responsibilities', '')
                benefits = details.get('benefits', '')
                
                # Analyze various job aspects
                teamwork_preference = analyze_teamwork_preference(
                    listing['title'], description, requirements, responsibilities
                )
                    
                company_size = analyze_company_size(
                    listing['company'], description
                )
                
                # Estimate work environment based on other factors
                # This is separate from teamwork preference now
                work_environment = analyze_work_environment(
                    teamwork_preference, 
                    analyze_stress_level(description, responsibilities),
                    company_size
                )
                
                learning_opportunity = analyze_learning_opportunity(
                    listing['title'], description, requirements, responsibilities
                )
                
                remote_preference = analyze_remote_preference(
                    description, requirements
                )
                
                career_growth = analyze_career_growth(
                    listing['title'], description, benefits
                )
                
                project_type = analyze_project_type(
                    listing['title'], description, responsibilities
                )
                
                # New analyzers
                experience_required = analyze_experience_required(
                    listing['title'], description, requirements
                )
                
                stress_level = analyze_stress_level(
                    description, responsibilities
                )
                
                creativity_required = analyze_creativity_required(
                    listing['title'], description, responsibilities
                )
                
                # Create job listing object
                job = JobListing(
                    title=listing['title'],
                    company=listing['company'],
                    location=listing['location'],
                    salary_min=details.get('salary_min', listing['salary_min']),
                    salary_max=details.get('salary_max', listing['salary_max']),
                    description=description,
                    requirements=requirements,
                    responsibilities=responsibilities,
                    benefits=benefits,
                    deadline=details.get('deadline', ''),
                    teamwork_preference=teamwork_preference,
                    work_environment=work_environment,
                    learning_opportunity=learning_opportunity,
                    company_size=company_size,
                    remote_preference=remote_preference,
                    career_growth=career_growth,
                    project_type=project_type,
                    experience_required=experience_required,
                    stress_level=stress_level,
                    creativity_required=creativity_required,
                    url=listing['url']
                )
                
                # Save to database
                session.add(job)
                session.commit()
                
                logging.info(f"Saved job: {job.title}")
                logging.info(f"  - Teamwork preference: {teamwork_preference:.2f}")
                logging.info(f"  - Work environment: {work_environment:.2f}")
                logging.info(f"  - Learning opportunity: {learning_opportunity:.2f}")
                logging.info(f"  - Company size: {company_size:.2f}")
                logging.info(f"  - Remote preference: {remote_preference:.2f}")
                logging.info(f"  - Career growth: {career_growth:.2f}")
                logging.info(f"  - Project type: {project_type:.2f}")
                logging.info(f"  - Experience required: {experience_required:.2f}")
                logging.info(f"  - Stress level: {stress_level:.2f}")
                logging.info(f"  - Creativity required: {creativity_required:.2f}")
                
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
