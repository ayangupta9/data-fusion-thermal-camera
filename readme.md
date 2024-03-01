# Practical Course: Data Fusion

## Topic: Thermal Camera

### Objective: In this project the goal is to estimate how much of a coffee cup is filled using a thermal camera.  This can be done on pictures and videos, using estimation techniques to improve the accuracy.

## What do we have at hand this moment

- Dataset
    - Image and videos
    - The dataset has some annotations merged
    - The visualizations don't really do a good job at scaling the temperature to RGB values (Change in maximum temperature in the scene; refer video of 2 cups)

Enter dataset path in `config.yaml` file or download from `Kaggle`

## Possible next steps
- get familiar with the thermal camera
    - install the seek Thermal App (Android)
    - record some pictures and videos
- visualize videos
    - turn off extra info in the app 
    - visualize videos in, e.g., matplotlib
- separate the coffee mug from the background
    - think of different ways, e.g, thresholds oder more advanced methods
- estimate how much of the coffee mug is filled
- repeat this for a video
    - use your estimation per frame as measurements
    - implement a Kalman Filter to get a smooth estimate over time
    - think of appropriate process and measurement models
- visualize your results

## Tasks to do:
- Improve dataset by seperating images and particular annotations
    - If possible create an in-sync scaling of temperature to RGB values
    - Extract max,min temperatures from the image
    - Resize the images to a particular size
- For the next possible steps, check out algorithms to carry out the tasks
    [ ] Thresholding, edge detection, connected components, watershed or even ML for object extraction
    [ ] Estimation of height from the cup.
        - Depends on the size of the image and size of the cup. 
            - Probably can do % filled

## Deadline
Poster session will possibly be on 22th March. We have 22 days. 1st week should be heavily focused on coding and algorithms. 