from PIL import Image
import numpy as np
import cv2
# import easyocr
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
    """extracts image and spectrum from input numpy array

    Args:
        image (np.array): complete image including both object and spectrum

    Returns:
        spectrum (np.array), cropped_img (np.array): spectrum and cropped image returned as numpy arrays
    """
    #       spectrum     cropped image
    return image[:,:29], image[:,50:]


def get_enhanced_image(image_path, apply_ce=False, apply_blur=False, apply_clahe=False, apply_dilation=False):
    
    c_img = rotate_to_vertical(image_path)
    og_img = c_img
    c_img = cv2.cvtColor(c_img, cv2.COLOR_RGB2GRAY)
    
    if apply_clahe:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(32,32))
        c_img = clahe.apply(c_img)
    
    if apply_ce:
        c_img = cv2.equalizeHist(c_img)
    
    if apply_blur:
        c_img = cv2.GaussianBlur(c_img, (51, 51), 15)

    cvt_img = cv2.cvtColor(og_img, cv2.COLOR_RGB2LAB)
    # cvt_img = og_img
    # img_dilate = None
    
    enhanced_img = cv2.convertScaleAbs(cvt_img[...,0], alpha=2,beta=-70)
    if apply_dilation:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # Adjust kernel size as needed
        img_dilate = cv2.dilate(enhanced_img, kernel, iterations=2)
    
    return c_img, og_img, cvt_img, enhanced_img, img_dilate


def gamma_correction(image, gamma):
  image = image / 255.0
  corrected = np.power(image, gamma)
  return np.uint8(corrected * 255.0)

def mixed_pipeline(img_p, apply_erode=False):
    c_img, og_img, cvt_img, enhanced_img, img_dilate = get_enhanced_image(img_p, apply_dilation=True)
    red_green = og_img[...,:2].mean(axis=-1)
    red_green = cv2.GaussianBlur(red_green, (11, 11), 5)
    gamma_rg = gamma_correction(red_green, gamma=2.0)
    gamma_rg_int = (gamma_rg > 20).astype(np.uint8) * 255
    
    # blurred = cv2.GaussianBlur(enhanced_img, (11, 11), 5)
    # blurred = cv2.GaussianBlur(gamma_rg, (11, 11), 5)
    thresh = cv2.adaptiveThreshold(gamma_rg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,21, 5)
    
    if apply_erode:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))  # Adjust kernel size as needed
        thresh = cv2.erode(thresh, kernel, iterations=2)

    _, labels, bboxes, _ = cv2.connectedComponentsWithStats(gamma_rg_int, connectivity=8)

    for box in bboxes[1:]:
        x,y,w,h,area = box
        if area > 5000:
            thresh[y + h:og_img.shape[0],x-30:x+w+30] = 0

    return (bboxes, thresh, og_img)




