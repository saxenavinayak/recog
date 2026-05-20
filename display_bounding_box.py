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

# np.float = float    
# np.int = int   #module 'numpy' has no attribute 'int'
# np.object = object    #module 'numpy' has no attribute 'object'
# np.bool = bool    #module 'numpy' has no attribute 'bool'

# app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
# app.prepare(ctx_id=0, det_size=(640, 640))
# register_heif_opener()

# img = cv2.imread("/mnt/e/whyyy/AAGM9623.JPG")
# faces = app.get(img)
# for face in faces:
#     bbox_data=face.bbox.astype(np.int)

#     start_point = (int(bbox_data[0]), int(bbox_data[1]))  # (2011, 738)
#     end_point   = (int(bbox_data[2]), int(bbox_data[3]))  # (2306, 1091)
    
#     cv2.rectangle(img, start_point, end_point, (0, 255, 0), 2)
#     cv2.imwrite('output_bounded.jpg', img)




# get medoid image (get the image which has the embedding with the higest average cosine similarity to all other embeddings)
# Algo
"""
a = [
    ("image1", "x1,y1, x2,y2", "tensor", label)
    ("image2", "x1,y1, x2,y2", "tensor", label)
    ("image3", "x1,y1, x2,y2", "tensor", label)
    ("image4", "x1,y1, x2,y2", "tensor", label)
    ("image5", "x1,y1, x2,y2", "tensor", label)
]
avg_cosine_images = []
for each image in label:
    current_candidate_tensor = image.tensor
    simil = []
    for each image2 in label:
        s = cosine.simil(current_candidate_tensor, image2.tensor)
        simil.append(s)
    average = mean(simil)
    avg_cosine_images.append((image, average))
best_candidate_image = max(avg_cosine_images, key=average)

        
    
        
"""

img = cv2.imread("/mnt/e/whyyy/JAXW0072.JPG")


# height, width, _ = image.shape
# print(f"Loaded image size: {width}x{height}")


bbox_data = [2441.0, 1693.0, 2639.0, 1980.0]

# # Map them correctly by extracting the X and Y coordinates
# # Remember: OpenCV wants (X, Y)
start_point = (int(bbox_data[0]), int(bbox_data[1]))  # (x1, y1) -> (750, 2011)
end_point = (int(bbox_data[2]), int(bbox_data[3]))
cv2.rectangle(img, start_point, end_point, (0, 255, 0), 2)
cv2.imwrite('output_bounded.jpg', img)