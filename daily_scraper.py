import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import joblib
from scipy.cluster.hierarchy import fcluster
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.cluster.hierarchy import linkage

headers = {'User-Agent': 'Mozilla/5.0'}
base_url = "https://www.karkidi.com/Find-Jobs/{}/all/India"
jobs_list = []

for page in range(1, 31):
    url = base_url.format(page)
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, "html.parser")
    job_blocks = soup.find_all("div", class_="ads-details")

    for job in job_blocks:
        try:
            title = job.find("h4").get_text(strip=True)
            company = job.find("a", href=lambda x: x and "Employer-Profile" in x).get_text(strip=True)
            location = job.find("p").get_text(strip=True)
            skills_tag = job.find("span", string="Key Skills")
            skills = skills_tag.find_next("p").get_text(strip=True) if skills_tag else ""
            jobs_list.append({
                "Title": title,
                "Company": company,
                "Location": location,
                "Skills": skills
            })
        except:
            continue
    time.sleep(1)

df = pd.DataFrame(jobs_list)
df.to_csv("data/jobs.csv", index=False)

# TF-IDF vectorizer & clustering
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(df["Skills"].fillna(""))
Z = linkage(X.toarray(), method='ward')

# Save
joblib.dump(vectorizer, "model/vectorizer.pkl")
joblib.dump(Z, "model/linkage_matrix.pkl")
