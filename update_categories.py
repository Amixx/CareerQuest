#!/usr/bin/env python3
import argparse
import logging
import re
import sqlite3
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

JOB_CATEGORIES = [
    "Administrēšana, Asistēšana",
    "Apsardze, Drošība",
    "Bankas, Apdrošināšana, Finanses, Grāmatvedība",
    "Būvniecība, Nekustamais īpašums, Ceļu būve",
    "Elektronika, Telekomunikācijas, Enerģētika",
    "Informāciju tehnoloģijas, Datori",
    "Inženiertehnika",
    "Izglītība, Zinātne",
    "Jurisprudence, Tieslietas",
    "Kultūra, Māksla, Izklaide",
    "Lauksaimniecība, Mežsaimniecība, Vide",
    "Mājsaimniecība, Apkope",
    "Mārketings, Reklāma, PR, Mediji",
    "Pakalpojumi",
    "Pārdošana, Tirdzniecība, Klientu apkalpošana",
    "Personāla vadība",
    "Prakse, Brīvprātīgais darbs",
    "Ražošana, Rūpniecība",
    "Transports, Loģistika, Piegāde",
    "Tūrisms, Viesnīcas, Ēdināšana",
    "Vadība",
    "Valsts un pašvaldību pārvalde",
    "Veselības aprūpe, Farmācija"
]

# Define keywords for each category
CATEGORY_KEYWORDS = {
    "Administrēšana, Asistēšana": ["administr", "asistent", "sekretār", "biroj", "office", "lietvedi", "dokumentu"],
    "Apsardze, Drošība": ["apsarg", "drošīb", "security", "aizsardzīb", "uzraudzīb"],
    "Bankas, Apdrošināšana, Finanses, Grāmatvedība": ["bank", "finans", "grāmatved", "apdrošināšan", "kredīt", "auditor", "naudas", "accounting", "finance"],
    "Būvniecība, Nekustamais īpašums, Ceļu būve": ["būvniecīb", "nekustam", "celtniecīb", "būvinženier", "arhitekt", "construction", "property", "real estate"],
    "Elektronika, Telekomunikācijas, Enerģētika": ["elektron", "elektrik", "telekomunikāc", "enerģētik", "electronic", "telecommunication", "electric"],
    "Informāciju tehnoloģijas, Datori": ["program", "it", "datori", "developer", "software", "sistem", "datortīkl", "web", "administrat", "code", "kodēšana", "programmer"],
    "Inženiertehnika": ["inženier", "tehnisk", "mechanic", "mehānik", "engineer", "technical"],
    "Izglītība, Zinātne": ["izglītīb", "skolotāj", "pasniedzēj", "zinātne", "pētnieks", "education", "teacher", "science"],
    "Jurisprudence, Tieslietas": ["jurist", "advokāt", "legal", "tiesisk", "tieslietas", "lawyer", "attorney"],
    "Kultūra, Māksla, Izklaide": ["kultūr", "māksla", "mākslinieks", "izklaide", "mūzik", "art", "entertainment", "culture"],
    "Lauksaimniecība, Mežsaimniecība, Vide": ["lauksaimniecīb", "mežsaimniecīb", "vide", "dārznieks", "ecology", "agriculture", "forestry", "environment"],
    "Mājsaimniecība, Apkope": ["mājsaimniecīb", "apkopēj", "tīrīšan", "housekeeping", "cleaning"],
    "Mārketings, Reklāma, PR, Mediji": ["mārketings", "reklām", "sabiedriskās attiecības", "medij", "marketing", "advertising", "pr", "media"],
    "Pakalpojumi": ["pakalpojum", "service", "apkalpošan"],
    "Pārdošana, Tirdzniecība, Klientu apkalpošana": ["pārdošan", "tirdzniecīb", "klient", "sales", "retail", "veikala", "customer"],
    "Personāla vadība": ["personāla", "hr", "cilvēkresurs", "human resources", "recruitment"],
    "Prakse, Brīvprātīgais darbs": ["prakse", "praktikant", "brīvprātīg", "intern", "internship", "volunteer"],
    "Ražošana, Rūpniecība": ["ražošan", "rūpniecīb", "production", "manufacturing", "factory", "montāž"],
    "Transports, Loģistika, Piegāde": ["transport", "loģistik", "piegād", "šofer", "autovadītāj", "kravas", "driver", "logistics", "delivery"],
    "Tūrisms, Viesnīcas, Ēdināšana": ["tūrism", "viesnīc", "ēdināšan", "pavārs", "restorān", "tourism", "hotel", "restaurant", "food"],
    "Vadība": ["vadītāj", "direktors", "manager", "management", "director", "vadība"],
    "Valsts un pašvaldību pārvalde": ["valsts", "pašvaldīb", "government", "municipal"],
    "Veselības aprūpe, Farmācija": ["veselīb", "medicīn", "ārsts", "farmāc", "health", "medical", "nurse", "doctor", "pharmacy"]
}

def determine_category(title, description=None):
    """
    Determine the most appropriate job category based on title and description
    
    Args:
        title (str): Job title
        description (str, optional): Job description
    
    Returns:
        str: The best matching job category
    """
    if not title:
        return "Unknown"
    
    # Combine title and description for matching
    text = title.lower()
    if description:
        text += " " + description.lower()
    
    # Count matches for each category
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in text:
                # Give more weight to matches in the title
                if keyword.lower() in title.lower():
                    score += 2
                else:
                    score += 1
        category_scores[category] = score
    
    # Get category with highest score
    best_category = max(category_scores.items(), key=lambda x: x[1])
    
    # If no matches found, return Unknown
    if best_category[1] == 0:
        return "Unknown"
    
    return best_category[0]

def extract_category_from_url(url):
    """Extract category from CV.lv URL if possible"""
    try:
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Example URL: /lv/search/category-it-jobs
        if 'category-' in path:
            category_part = re.search(r'category-(.+?)(?:-jobs)?(?:/|$)', path)
            if category_part:
                category_slug = category_part.group(1)
                # Map slug back to category name (simplified example)
                if category_slug == 'it':
                    return "Informāciju tehnoloģijas, Datori"
                # Add more mappings as needed
        return None
    except:
        return None

def column_exists(cursor, table_name, column_name):
    """
    Check if a column exists in a specific table
    
    Args:
        cursor: SQLite cursor
        table_name (str): Name of the table
        column_name (str): Name of the column to check
    
    Returns:
        bool: True if the column exists, False otherwise
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(column[1] == column_name for column in columns)

def add_column_if_not_exists(cursor, table_name, column_name, column_type):
    """
    Add a column to a table if it doesn't already exist
    
    Args:
        cursor: SQLite cursor
        table_name (str): Name of the table
        column_name (str): Name of the column to add
        column_type (str): SQL type of the column
    """
    if not column_exists(cursor, table_name, column_name):
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            logging.info(f"Added column {column_name} to table {table_name}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding column {column_name} to {table_name}: {e}")
            return False
    return False

def update_job_categories(db_path):
    """
    Update job categories in the database for jobs with missing or unknown categories
    
    Args:
        db_path (str): Path to SQLite database
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add job_category column if it doesn't exist
        add_column_if_not_exists(cursor, "job_listings", "job_category", "VARCHAR(100)")
        
        # Get jobs with missing or unknown categories
        cursor.execute("""
            SELECT id, title, description, url, job_category 
            FROM job_listings 
            WHERE job_category IS NULL OR job_category = 'Unknown'
        """)
        jobs = cursor.fetchall()
        
        updated_count = 0
        for job_id, title, description, url, current_category in jobs:
            # Try to extract from URL first
            category = extract_category_from_url(url)
            
            # If not found in URL, determine from content
            if not category:
                category = determine_category(title, description)
            
            # If a valid category was determined, update the database
            if category != "Unknown":
                cursor.execute(
                    "UPDATE job_listings SET job_category = ? WHERE id = ?",
                    (category, job_id)
                )
                updated_count += 1
        
        conn.commit()
        logging.info(f"Updated {updated_count} job categories out of {len(jobs)} total jobs with missing categories")
    
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def main():
    parser = argparse.ArgumentParser(description='Update job categories in the database')
    parser.add_argument('--db', required=True, help='Path to SQLite database')
    args = parser.parse_args()
    
    logging.info("Starting job category update process")
    update_job_categories(args.db)
    logging.info("Job category update completed")

if __name__ == "__main__":
    main()
