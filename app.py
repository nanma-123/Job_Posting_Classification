import streamlit as st
import pandas as pd
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import fcluster
from streamlit.components.v1 import html

# Load job data and models
@st.cache_data(ttl=60)
def load_jobs():
    return pd.read_csv("data/jobs.csv")

@st.cache_resource
def load_models():
    vectorizer = joblib.load("vectorizer.pkl")
    linkage_matrix = joblib.load("linkage_matrix.pkl")
    return vectorizer, linkage_matrix

df = load_jobs()
vectorizer, Z = load_models()

st.title("🧠 Job Recommender with Skill Clustering")

# User input
user_skill = st.text_input("Enter your skills (comma-separated):")

if user_skill:
    # Vectorize user input
    user_vector = vectorizer.transform([user_skill])
    
    # Predict cluster
    user_cluster = fcluster(Z,t=4, criterion='maxclust')  # Must match training k
    job_vectors = vectorizer.transform(df["Skills"].fillna(""))
    all_clusters = fcluster(Z,t=4, criterion='maxclust')  # Assign clusters to jobs
    df["Cluster"] = all_clusters

    # Find similar jobs in same cluster
    cluster_id = fcluster(Z,t=4, criterion='maxclust')[0]
    matched_jobs = df[df["Cluster"] == cluster_id]

    # Rank by similarity
    similarities = cosine_similarity(user_vector, job_vectors[matched_jobs.index])
    matched_jobs["Similarity"] = similarities[0]
    top_matches = matched_jobs.sort_values("Similarity", ascending=False).head(10)

    if not top_matches.empty:
        st.success(f"Found {len(top_matches)} jobs in your cluster 🎯")
        st.dataframe(top_matches[["Title", "Company", "Location", "Skills", "Similarity"]])
        
        # 🔔 JavaScript Notification
        html(f"""
            <script>
                Notification.requestPermission().then(function(permission) {{
                    if (permission === "granted") {{
                        new Notification("🎯 Matched Jobs Found", {{
                            body: "Top jobs for your skills have been found!",
                            icon: "https://cdn-icons-png.flaticon.com/512/565/565547.png"
                        }});
                    }}
                }});
            </script>
        """)
    else:
        st.warning("No job matches found.")
