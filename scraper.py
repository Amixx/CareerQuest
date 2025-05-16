import re
import time
import random
import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from update_categories import determine_category

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class CVLVScraper:
    def __init__(self, base_url, delay_range=(1, 3), headless=True):
        self.base_url = base_url
        self.delay_range = delay_range
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,lv;q=0.8',
        })
        
        # Setup Selenium WebDriver
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    
    def get_page_content(self, url):
        """Make a request to the given URL and return the BeautifulSoup object"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def get_job_listings(self, page=1):
        """Scrape job listings from the list view page using Selenium to handle dynamic content"""
        url = self.base_url
        if page > 1:
            offset = (page - 1) * 20
            url = url.replace('offset=0', f'offset={offset}')
        
        logging.info(f"Loading URL in Selenium: {url}")
        try:
            self.driver.get(url)
            
            # Wait for job listings to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.vacancies-list__item"))
            )
            
            # Small additional wait to ensure all elements are loaded
            time.sleep(2)
            
            # Get the page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            listing_items = soup.select('li.vacancies-list__item')
            logging.info(f"Found {len(listing_items)} job listings on page {page}")
            
            listings = []
            for item in listing_items:
                try:
                    listing_data = self._parse_listing_item(item)
                    if listing_data:
                        listings.append(listing_data)
                except Exception as e:
                    logging.error(f"Error parsing listing: {e}")
            
            return listings
            
        except Exception as e:
            logging.error(f"Error loading page with Selenium: {e}")
            return []
    
    def _parse_listing_item(self, item):
        """Extract data from a job listing item"""
        title_elem = item.select_one('a.vacancy-item__title')
        if not title_elem:
            return None
            
        # Extract basic data
        title = title_elem.text.strip()
        relative_url = title_elem.get('href', '')
        url = urljoin('https://cv.lv', relative_url)
        
        # Extract company
        company_elem = item.select_one('a[href^="/lv/search/employer"]')
        company = company_elem.text.strip() if company_elem else "Unknown"
        
        # Extract location
        location_elem = item.select_one('div.vacancy-item__locations')
        location = location_elem.text.strip() if location_elem else "Unknown"
        
        # Extract salary
        salary_elem = item.select_one('span.salary-label')
        salary_min, salary_max = self._parse_salary(salary_elem.text.strip() if salary_elem else "")
        
        return {
            'title': title,
            'company': company,
            'location': location,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'url': url
        }
    
    def get_job_details(self, title, url):
        """Scrape detailed information from a job listing page using Selenium"""
        try:
            logging.info(f"Loading job details from: {url}")
            self.driver.get(url)
            
            # Wait for content to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='tabpanel']"))
            )
            
            # Small additional wait
            time.sleep(1)
            
            # Get the page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            details = {}
            
            # Extract description tab content - this is the first tab panel
            description_panel = soup.select_one('div.react-tabs__tab-panel--selected')
            if description_panel:
                # Check if this is an image-only listing (contains vacancy-details__image but no meaningful text)
                image_only = False
                image_div = description_panel.select_one('div.vacancy-details__image')
                
                if image_div:
                    # Extract all text from the description panel, excluding script tags
                    desc_text = description_panel.get_text(strip=True)
                    # If panel has almost no text but has an image, consider it image-only
                    if len(desc_text) < 50:  # Very little text
                        image_only = True
                        logging.warning(f"Skipping image-only job listing: {url}")
                        details['is_image_only'] = True
                        return details
                
                # Get the full description text
                details['description'] = description_panel.text.strip()

                details['job_category'] = determine_category(title, details['description'])
            
                # Try to extract specific sections if they exist
                details.update(self._extract_job_sections(description_panel))
            
            # Extract additional info from the second tab (Pamatinformācija)
            # Click on the second tab
            try:
                second_tab = self.driver.find_element(By.XPATH, "//ul[@role='tablist']/li[2]")
                second_tab.click()
                time.sleep(1)  # Wait for tab content to load
                
                # Get updated page source
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Extract salary and benefits
                salary_section = soup.select_one('div.vacancy-highlights__salary')
                if salary_section:
                    salary_amount = salary_section.select_one('span.vacancy-highlights__salary-amount')
                    if salary_amount:
                        salary_text = salary_amount.text.strip()
                        min_salary, max_salary = self._parse_salary(salary_text)
                        if min_salary is not None:
                            details['salary_min'] = min_salary
                        if max_salary is not None:
                            details['salary_max'] = max_salary
                    
                    # Extract benefits
                    benefits_elem = salary_section.select_one('h3')
                    if benefits_elem and "Papildu informācija" in benefits_elem.text:
                        benefits_text = benefits_elem.text.replace("Papildu informācija:", "").strip()
                        details['benefits'] = benefits_text
                
                # Extract deadline
                deadline_elem = soup.select_one('span.vacancy-info__deadline')
                if deadline_elem:
                    deadline_text = deadline_elem.text.strip()
                    deadline_match = re.search(r'Termiņš: (\d{1,2}\.\d{1,2}\.\d{4})', deadline_text)
                    if deadline_match:
                        details['deadline'] = deadline_match.group(1)
            
            except Exception as e:
                logging.warning(f"Could not extract data from second tab: {e}")
            
            return details
            
        except Exception as e:
            logging.error(f"Error getting job details with Selenium: {e}")
            return {}
    
    def _extract_job_sections(self, description_element):
        """Extract requirements, responsibilities, and benefits from the description text"""
        result = {
            'requirements': '',
            'responsibilities': '',
            'benefits': ''
        }
        
        # Try to find structured content first
        section_keywords = {
            'requirements': ['Prasības:', 'Prasības', 'Requirements:', 'Requirements'],
            'responsibilities': ['Pienākumi:', 'Pienākumi', 'Darba pienākumi:', 'Tasks:', 'Responsibilities:'],
            'benefits': ['Piedāvājums:', 'Piedāvājums', 'Piedāvājam:', 'Mēs piedāvājam:', 'We offer:', 'What we offer']
        }
        
        desc_text = description_element.get_text()
        
        # Look for each section in the text
        for section, keywords in section_keywords.items():
            for keyword in keywords:
                pattern = f"{re.escape(keyword)}(.*?)("
                
                # Create a pattern that finds text between this keyword and the next section keyword
                next_keywords = []
                for other_keywords in section_keywords.values():
                    next_keywords.extend(other_keywords)
                
                # Remove the current keyword from next_keywords
                next_keywords = [k for k in next_keywords if k != keyword]
                
                # Add some common end patterns
                next_keywords.extend(["Atalgojums:", "Alga:", "Salary:", "Termins:", "Deadline:"])
                
                # Create the regex pattern
                end_pattern = "|".join(re.escape(k) for k in next_keywords)
                if end_pattern:
                    pattern += f"({end_pattern})|$)"
                else:
                    pattern += "$)"
                
                # Find the section text
                match = re.search(pattern, desc_text, re.DOTALL | re.IGNORECASE)
                if match:
                    section_text = match.group(1).strip()
                    
                    # If text is found and it's reasonable in length, save it
                    if section_text and len(section_text) > 10:
                        result[section] = section_text
                        break
        
        # Find any bullet points in the content which might be requirements/responsibilities
        if not any(result.values()):
            list_items = description_element.select('ul li')
            if list_items:
                # Group list items by their parent ul
                lists = {}
                for li in list_items:
                    parent = li.parent
                    if parent not in lists:
                        lists[parent] = []
                    lists[parent].append(li.text.strip())
                
                # Try to determine which list belongs to which section based on preceding text
                for ul, items in lists.items():
                    prev_elem = ul.find_previous()
                    if prev_elem:
                        prev_text = prev_elem.get_text().lower()
                        if any(kw.lower() in prev_text for kw in section_keywords['requirements']):
                            result['requirements'] = '\n'.join(items)
                        elif any(kw.lower() in prev_text for kw in section_keywords['responsibilities']):
                            result['responsibilities'] = '\n'.join(items)
                        elif any(kw.lower() in prev_text for kw in section_keywords['benefits']):
                            result['benefits'] = '\n'.join(items)
        
        return result
    
    def _parse_salary(self, salary_text):
        """Parse salary range from text"""
        if not salary_text:
            return None, None
        
        # Try to extract salary range (e.g., "€ 2300 - 3000")
        match = re.search(r'€?\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)', salary_text)
        if match:
            return float(match.group(1)), float(match.group(2))
        
        # Single salary value
        match = re.search(r'€?\s*(\d+(?:\.\d+)?)', salary_text)
        if match:
            value = float(match.group(1))
            return value, value
        
        return None, None
    
    def close(self):
        """Close the WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
