import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
from datetime import datetime

DATA_FILE = "jobs_data.csv"
URL = "https://example.com/jobs"  # Replace with actual job listing page

def scrape_jobs():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    for job_entry in soup.select(".job-card"):  # Update selector as needed
        title = job_entry.select_one(".job-title").text.strip()
        company = job_entry.select_one(".company").text.strip()
        location = job_entry.select_one(".location").text.strip()
        skills = job_entry.select_one(".skills").text.strip()

        jobs.append({
            "Title": title,
            "Company": company,
            "Location": location,
            "Skills": skills,
            "ScrapedAt": datetime.utcnow()
        })

    df_new = pd.DataFrame(jobs)

    # Load existing data
    try:
        df_old = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        df_old = pd.DataFrame()

    # Merge and drop duplicates
    df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=["Title", "Company", "Location", "Skills"])
    df_combined.to_csv(DATA_FILE, index=False)
    print(f"[{datetime.now()}] Scraped {len(df_new)} jobs. Total now: {len(df_combined)}.")

schedule.every().day.at("06:00").do(scrape_jobs)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
