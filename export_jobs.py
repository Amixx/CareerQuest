#!/usr/bin/env python3
import json
import argparse
import sqlite3
import os
from datetime import datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def export_jobs_to_json(db_path, output_file):
    """Export job listings from SQLite database to JSON file"""
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' not found.")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables accessing columns by name
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, company, location, salary_min, salary_max, 
                   description, requirements, responsibilities, benefits, 
                   deadline, team_work_likelihood, url, scraped_at
            FROM job_listings
        """)
        
        jobs = [dict(row) for row in cursor.fetchall()]
        
        # Add placeholder fields for matching algorithm
        for job in jobs:
            # These are placeholder fields that will be used for matching
            job['work_environment'] = float(job['team_work_likelihood']) * 10  # Scale 0-10
            job['tech_level'] = 5  # Placeholder, 0-10 scale
            job['experience_required'] = 3  # Placeholder, 0-10 scale
            job['stress_level'] = 5  # Placeholder, 0-10 scale
            job['creativity_required'] = 4  # Placeholder, 0-10 scale
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, default=json_serial, indent=2)
            
        print(f"Successfully exported {len(jobs)} jobs to {output_file}")
        return True
    
    except Exception as e:
        print(f"Error exporting data: {e}")
        return False
    
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='Export job listings to JSON')
    parser.add_argument('--db', default='job_listings.db', help='Path to SQLite database')
    parser.add_argument('--output', default='website/data/jobs.json', help='Output JSON file')
    args = parser.parse_args()
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    export_jobs_to_json(args.db, args.output)

if __name__ == "__main__":
    main()
