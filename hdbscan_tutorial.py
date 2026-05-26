# This script consumes data from a postgres db, stores them as a dataframe, and clusters datapoints together using hierarchial based scanning (hdbscan)
from sklearn.datasets import make_blobs
import pandas as pd
import hdbscan
import os
import psycopg2
import numpy as np
from pgvector.psycopg2 import register_vector
from helpers.db_connector import postgres_connection
# Official docs https://hdbscan.readthedocs.io/en/latest/basic_hdbscan.html

# blobs, labels = make_blobs(n_samples=2000, n_features=10)

# print(blobs.shape)
# print(pd.DataFrame(blobs).head())



clusterer = hdbscan.HDBSCAN()

# clusterer.fit(blobs)



##### Downloading data
conn = postgres_connection()
register_vector(conn)
cursor = conn.cursor()
cursor.execute("SELECT id, image_name, norm_embedded_tensor, bounding_box FROM photo_analysis")
rows = cursor.fetchall()


df = pd.DataFrame(rows, columns=["id", "image_name", "embedding", "bounding_box"])
embeddings  = np.array([r[2] for r in rows])


clusterer.fit(embeddings)

df["image_labels"] = clusterer.labels_
print(df.head())

new_label_row = """
ALTER TABLE photo_analysis
ADD COLUMN IF NOT EXISTS image_labels INTEGER
"""

cursor.execute(new_label_row)
for index, row in df.iterrows():
    cursor.execute(
        "UPDATE photo_analysis SET image_labels = %s WHERE id = %s",
        (
            int(row["image_labels"]),
            int(row["id"])
        )
    )

conn.commit()
conn.close()


print(df[(df["image_labels"] == 2)])
