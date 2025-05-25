import streamlit as st
import pandas as pd
import joblib
from scipy.cluster.hierarchy import fcluster, linkage, dendrogram
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt

# --- Load Data and Models ---
@st.cache_data
def load_data():
    df = pd.read_csv("jobs_data.csv")  # You need to save your df as CSV
    vectorizer = joblib.load("vectorizer.pkl")
    Z = joblib.load("linkage_matrix.pkl")
    return df, vectorizer, Z

df, vectorizer, Z = load_data()

# --- Sidebar ---
st.sidebar.title("Cluster Explorer")
num_clusters = st.sidebar.slider("Select Number of Clusters", 2, 20, 4)

# --- Apply Clustering ---
df['Cluster'] = fcluster(Z, num_clusters, criterion='maxclust')

# --- Title ---
st.title("Job Clustering Dashboard")
st.write(f"Clustering jobs into **{num_clusters}** clusters based on required skills.")

# --- Show Cluster Distribution ---
st.subheader("Cluster Distribution")
st.bar_chart(df['Cluster'].value_counts().sort_index())

# --- Keyword Summary ---
st.subheader("Top Keywords per Cluster")
tfidf_matrix = vectorizer.transform(df['Skills']).toarray()
feature_names = vectorizer.get_feature_names_out()
tfidf_df = pd.DataFrame(tfidf_matrix)
tfidf_df['Cluster'] = df['Cluster'].values

def get_top_keywords(cluster_id, top_n=10):
    cluster_tfidf = tfidf_df[tfidf_df['Cluster'] == cluster_id].drop('Cluster', axis=1)
    mean_tfidf = cluster_tfidf.mean(axis=0)
    top_indices = mean_tfidf.argsort()[::-1][:top_n]
    return [feature_names[i] for i in top_indices]

for cluster_id in sorted(df['Cluster'].unique()):
    st.markdown(f"**Cluster {cluster_id}**")
    keywords = get_top_keywords(cluster_id)
    st.write(", ".join(keywords))

# --- View Jobs by Cluster ---
st.subheader("Browse Job Titles by Cluster")
selected_cluster = st.selectbox("Select Cluster", sorted(df['Cluster'].unique()))
filtered = df[df['Cluster'] == selected_cluster]
st.write(f"Found {len(filtered)} job postings in Cluster {selected_cluster}")
st.dataframe(filtered[['Title', 'Company', 'Location', 'Skills']].reset_index(drop=True))

# --- Optional: Dendrogram Plot ---
st.subheader("Dendrogram")
fig, ax = plt.subplots(figsize=(10, 5))
dendrogram(Z, truncate_mode='lastp', p=num_clusters, leaf_rotation=90., leaf_font_size=10., show_contracted=True, ax=ax)
st.pyplot(fig)
