import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from insightface.app.common import Face
from insightface.data import get_image as ins_get_image
from PIL import Image
from pillow_heif import register_heif_opener
import os

from helpers.db_connector import get_db
from models.recog_models import PhotoResource
# Source - https://stackoverflow.com/a/75837322
# Posted by Vegarus, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-11, License - CC BY-SA 4.0


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
        app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        register_heif_opener()
        paths_to_images = self.get_list_of_image_paths(path)

        for image in paths_to_images:
            with get_db() as db:
                exists = db.query(PhotoResource).filter(PhotoResource.image_name == image).first()
                img = cv2.imread(image)
                if img is None:
                    continue
                if exists:
                    print(f"{image} has been previously analyzed, skipping")
                    continue
                faces = app.get(img)
                for face in faces:
                    embedding = face.normed_embedding
                    face_box = face.bbox.astype(np.int)

                    exists = db.query(PhotoResource).filter(PhotoResource.image_name == image).first()
                    new_photo_asset = PhotoResource(
                        image_name = image,
                        norm_embedded_tensor = embedding.tolist(),
                        bounding_box = face_box.tolist()
                    )
                    db.add(new_photo_asset)

new_job = IngestImages()
new_job.run_photo_analysis(path="/mnt/e/whyyy/")