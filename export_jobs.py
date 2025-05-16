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
                   deadline, teamwork_preference, work_environment, learning_opportunity,
                   company_size, remote_preference, career_growth, project_type,
                   experience_required, stress_level, creativity_required,
                   url, scraped_at
            FROM job_listings
        """)
        
        jobs = [dict(row) for row in cursor.fetchall()]
        
        # Process jobs data for frontend use
        for job in jobs:
            # Convert values from 0-1 scale to 0-10 scale
            job['teamwork_preference'] = round(float(job.get('teamwork_preference', 0.5)) * 10)
            job['work_environment'] = round(float(job.get('work_environment', 0.5)) * 10)
            job['learning_opportunity'] = round(float(job.get('learning_opportunity', 0.5)) * 10)
            job['company_size'] = round(float(job.get('company_size', 0.4)) * 10)
            job['remote_preference'] = round(float(job.get('remote_preference', 0.3)) * 10)
            job['career_growth'] = round(float(job.get('career_growth', 0.5)) * 10)
            job['project_type'] = round(float(job.get('project_type', 0.5)) * 10)
            job['experience_required'] = round(float(job.get('experience_required', 0.5)) * 10)
            job['stress_level'] = round(float(job.get('stress_level', 0.5)) * 10)
            job['creativity_required'] = round(float(job.get('creativity_required', 0.5)) * 10)
        
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
    parser.add_argument('--output', default='a/data/jobs.json', help='Output JSON file')
    args = parser.parse_args()
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    export_jobs_to_json(args.db, args.output)

if __name__ == "__main__":
    main()
