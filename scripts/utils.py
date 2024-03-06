from PIL import Image
import numpy as np
import cv2
import easyocr
import pandas as pd
import os


def interpret_orientation(orientation):
    orientation_map = {
        1: "Normal (no rotation)",
        2: "Mirror horizontally",
        3: "Rotate 180°",
        4: "Mirror vertically",
        5: "Mirror horizontally and rotate 270° clockwise",
        6: "Rotate 90° clockwise",
        7: "Mirror horizontally and rotate 90° clockwise",
        8: "Rotate 270° clockwise"
    }
    return orientation_map.get(orientation, "Unknown")


def rotate_to_vertical(image_path):
    with Image.open(image_path) as img:
        exif = img._getexif()
        orientation = exif.get(274, 1) if exif else 1

        # Map orientations to rotation angle and mirror flag
        orientation_map = {
            1: (0, False),
            2: (0, True),
            3: (180, False),
            4: (180, True),
            5: (-270, True),
            6: (-90, False),
            7: (-90, True),
            8: (-270, False)
        }

        rotation_angle, mirror = orientation_map.get(orientation, (0, False))

        # Rotate image
        rotated_img = img.rotate(rotation_angle, expand=True)

        # Mirror image if necessary
        if mirror:
            rotated_img = rotated_img.transpose(Image.FLIP_LEFT_RIGHT)

        return np.array(rotated_img)
 
   
def get_temperatures(image):
  top_left_corner = image[0:50, 30:100]  # Adjust these values based on the image size and text location
  bottom_left_corner = image[-50:, 30:80]  # Adjust these values based on the image size and text location

  # Convert to gray scale
  gray_top_left = cv2.cvtColor(top_left_corner, cv2.COLOR_RGB2GRAY)
  gray_bottom_left = cv2.cvtColor(bottom_left_corner, cv2.COLOR_RGB2GRAY)

  reader = easyocr.Reader(['en'])

  # Use EasyOCR on the numpy array
  top_temperature = reader.readtext(gray_top_left)
  bottom_temperature = reader.readtext(gray_bottom_left)
  
  return {
      'high_temp': int(top_temperature[0][-2]),
      'low_temp': int(bottom_temperature[0][-2])
  }
  
  
def create_temp_annotations(images_full_paths):
  temp_df = pd.DataFrame(columns=['image_name','high_temperature','low_temperature'])

  for img_path in images_full_paths:
    img = rotate_to_vertical(img_path)
    temperatures = get_temperatures(img)
    temp_df.loc[len(temp_df)] = [os.path.basename(img_path), temperatures['high_temp'], temperatures['low_temp']]

  return temp_df


def extract_image_and_spectrum(image: np.array):
    #       spectrum     cropped image
    return image[:,:50], image[:,50:]


