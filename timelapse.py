import cv2
import os

image_folder = '/home/allsky/allsky/images/20211020/sequence'

images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

writer = cv2.VideoWriter('./timelapse.mp4', cv2.VideoWriter_fourcc(*"MP4V"), 30,  (width,height))
for image in images:
    writer.write(cv2.imread(os.path.join(image_folder, image)))
writer.release()
