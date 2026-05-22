#  This script consumes images, at a specified path, generates normed embeddings usiung insightFace, and uploads embeddings as pgvector to postgres


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
# Source - https://stackoverflow.com/a/75837322
# Posted by Vegarus, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-11, License - CC BY-SA 4.0

# Goated guide on fixing onxx + wsl2 
# https://kevinskii.dev/posts/onnx-runtime-gpu-in-wsl2/ 
np.float = float    
np.int = int   #module 'numpy' has no attribute 'int'
np.object = object    #module 'numpy' has no attribute 'object'
np.bool = bool    #module 'numpy' has no attribute 'bool'

class IngestImages:
    def get_list_of_image_paths(self, path: str):
        images = os.listdir(path)
        images = [item for item in images if "JPG" in item]
        if len(images) == 0:
            print(f"no images in dir {path}, or no .JPG images found, exiting")
            return
        print(f"Detecting faces for {len(images)} images")
        full_path = [f"{path}{item}" for item in images]
        return full_path


    def run_photo_analysis(self, path: str):
        paths_to_images = self.get_list_of_image_paths(path)



conn = postgres_connection()
# Add pgvector extension
cursor = conn.cursor()
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

cursor.execute("""
CREATE TABLE IF NOT EXISTS photo_analysis (
    id SERIAL PRIMARY KEY,
    image_name TEXT NOT NULL,
    norm_embedded_tensor VECTOR(512) NOT NULL,
    bounding_box VECTOR(4) NOT NULL
)               
""")
conn.commit()

query = "INSERT INTO photo_analysis (image_name, norm_embedded_tensor, bounding_box) VALUES (%s, %s, %s)"

path = "/mnt/e/whyyy/"
images = os.listdir(path)
images = [item for item in images if "JPG" in item]
path_to_media = [f"{path}{item}" for item in images]



app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))
register_heif_opener()

for image in path_to_media:
    img = cv2.imread(image)
    # We may have corrupted images here
    if img is not None:
        faces = app.get(img)
        genders = []
        for face in faces:
            genders += face.sex
            embedding = face.normed_embedding
            face_box = face.bbox.astype(np.int)
            cursor.execute(query, (image, embedding.tolist(), face_box.tolist()))
        conn.commit()
        print(f"For Image: {image}, genders are {genders} ")

