import cv2
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from insightface.app.common import Face
from insightface.data import get_image as ins_get_image
from PIL import Image
from pillow_heif import register_heif_opener
import os
import psycopg2
from helpers.db_connector import postgres_connection
from pgvector.psycopg2 import register_vector

import pandas as pd


# get medoid image (get the image which has the embedding with the higest average cosine similarity to all other embeddings)


conn = postgres_connection()
register_vector(conn)
cursor = conn.cursor()

cursor.execute("SELECT id, image_name, norm_embedded_tensor, bounding_box, image_labels FROM photo_analysis WHERE image_labels=44")
rows = cursor.fetchall()

df = pd.DataFrame(rows, columns=["id", "image_name", "norm_embedded_tensor", "bounding_box", "image_labels"])

avg_cosine_images = []
for row in df.itertuples():
    current_candidate_tensor = row.norm_embedded_tensor

    simil = np.array([])
    for another_row in df.itertuples():
        tensor = another_row.norm_embedded_tensor
        similarity = float(np.dot(current_candidate_tensor, tensor))
        simil = np.append(simil, similarity)
    print(f"The average cosine similarity score for image {row.image_name} is {np.mean(simil)}")
    avg_cosine_images.append(
        (row.image_name, np.mean(simil), row.bounding_box)
        )

best = max(avg_cosine_images, key=lambda x: x[1])
print(best)

img = cv2.imread(best[0])
bbox_data = best[2]
print(bbox_data)
start_point = (int(bbox_data[0]), int(bbox_data[1]))  # (x1, y1) -> (750, 2011)
end_point = (int(bbox_data[2]), int(bbox_data[3]))
cv2.rectangle(img, start_point, end_point, (0, 255, 0), 2)
cv2.imwrite('output_bounded.jpg', img)