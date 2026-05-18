# This script consumes data from a postgres db, stores them as a dataframe, and clusters datapoints together using hierarchial based scanning (hdbscan)
from sklearn.datasets import make_blobs
import pandas as pd
import hdbscan
import os
import psycopg2
import numpy as np
from pgvector.psycopg2 import register_vector

# Official docs https://hdbscan.readthedocs.io/en/latest/basic_hdbscan.html

# blobs, labels = make_blobs(n_samples=2000, n_features=10)

# print(blobs.shape)
# print(pd.DataFrame(blobs).head())



clusterer = hdbscan.HDBSCAN()

# clusterer.fit(blobs)



##### Downloading data

pg_pwd = os.getenv("POSTGRES_PW")
pg_usr = os.getenv("POSTGRES_USER")
pg_host = os.getenv("POSTGRES_HOST")
pg_port = os.getenv("POSTGRES_PORT")

conn = psycopg2.connect(
    database="postgres",
    user=pg_usr,
    password=pg_pwd,
    host=pg_host,
    port=pg_port
)
register_vector(conn)
cursor = conn.cursor()
cursor.execute("SELECT id, image_name, norm_embedded_tensor FROM photo_analysis")
rows = cursor.fetchall()
conn.close()



embeddings  = np.array([r[2] for r in rows])
print(embeddings.shape)

clusterer.fit(embeddings)

print(clusterer.labels_)
print(clusterer.labels_.max())
id = 1
for item in clusterer.labels_:
    if item == 30:
        print(f"30 found on image {rows[id-1][1]}")
    id+=1