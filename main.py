import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from insightface.app.common import Face
from insightface.data import get_image as ins_get_image
from PIL import Image
from pillow_heif import register_heif_opener
import os
# Source - https://stackoverflow.com/a/75837322
# Posted by Vegarus, modified by community. See post 'Timeline' for change history
# Retrieved 2026-05-11, License - CC BY-SA 4.0

np.float = float    
np.int = int   #module 'numpy' has no attribute 'int'
np.object = object    #module 'numpy' has no attribute 'object'
np.bool = bool    #module 'numpy' has no attribute 'bool'


def main():
    app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    register_heif_opener()
    target_face = "vinayak_images/20231202_145957.jpg"
    target_image = cv2.imread(target_face)
    target_face_embedding = app.get(target_image)[0].normed_embedding


    directory = "vinayak_images"
    contents = os.listdir(directory)
    contents_fixed = [directory+"/"+x for x in contents]

    
   


    for image in contents_fixed:
        opened = Image.open(image)
        opened.convert("RGB").save("image.jpg", "JPEG")
        
        
        img = cv2.imread('image.jpg')
        faces = app.get(img)[0].normed_embedding
        similarity = float(np.dot(target_face_embedding, faces))
        print(f"cosine similarity for image {image}:", similarity)

        # for face in faces:
            # print(face.embedding_norm, face.normed_embedding, face.sex)
    # rimg = app.draw_on(img, faces)
    # cv2.imwrite("./t1_output.jpg", rimg)


if __name__ == "__main__":
    main()
