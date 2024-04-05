import numpy as np
import time
import cv2
from pygame import mixer

snare_beat_played = False
hat_beat_played = False

# Initialize the mixer
mixer.init() 

# Importing drum beats
hat_sound = mixer.Sound('./sounds/high_hat_2.wav')
snare_sound = mixer.Sound('./sounds/snare_1.wav')
kick_drum_sound = mixer.Sound('./sounds/high_hat_3.wav')

# This function plays the corresponding drum beat if a green color object is detected in the region
def play_beat(detected, sound, beat_played_flag):
    global snare_beat_played, hat_beat_played

    # If it is detected and the beat hasn't been played yet, play the corresponding drum beat
    if detected and not beat_played_flag:
        sound.play()
        if sound == snare_sound:
            snare_beat_played = True
        elif sound == hat_sound:
            hat_beat_played = True

     
# This function is used to check if green color is present in the small region
def detect_in_region(frame, sound, beat_played_flag):
    global snare_beat_played, hat_beat_played

    # Converting to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define lower and upper bounds for green color in HSV
    lower_green = np.array([40, 40, 40])  # Adjust these values as needed
    upper_green = np.array([70, 255, 255]) # Adjust these values as needed

    # Creating mask
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Calculating the number of green pixels
    detected = np.sum(mask)

    # Call the function to play the drum beat
    play_beat(detected, sound, beat_played_flag)

    # Update the beat played flag based on whether green color is detected or not
    if detected:
        beat_played_flag = True
    else:
        beat_played_flag = False

    return mask, beat_played_flag

# A flag variable to choose whether to show the region that is being detected
verbose = False

# Set HSV range for detecting green color
greenLower = (25,50,50)
greenUpper = (32,255,255)

# Obtain input from the webcam
camera = cv2.VideoCapture(0)
ret, frame = camera.read()
H, W = frame.shape[:2]

kernel = np.ones((7,7), np.uint8)

# Load the images
hat_img = cv2.imread('./images/high_hat.png')
snare_img = cv2.imread('./images/Snare.webp')
kick_drum_img = cv2.imread('./images/BassDrum.webp')

# Define the dimensions of the regions
hat_thickness = [200,100]
snare_thickness = [200,100]
kick_drum_thickness = [180,100]
kick_drum_btm = [W * 7 // 8, H * 6 // 8]
kick_drum_top = [kick_drum_btm[0] - kick_drum_thickness[0], kick_drum_btm[1] - kick_drum_thickness[1]]

# Resize the images to match the region dimensions
hat = cv2.resize(hat_img, (hat_thickness[0], hat_thickness[1]))
snare = cv2.resize(snare_img, (snare_thickness[0], snare_thickness[1]))
kick_drum = cv2.resize(kick_drum_img, (kick_drum_btm[0] - kick_drum_top[0], kick_drum_btm[1] - kick_drum_top[1]))


# Set the region area for detecting green color
hat_center = [np.shape(frame)[1] * 2 // 8, np.shape(frame)[0] * 2 // 8]
snare_center = [np.shape(frame)[1] * 2 // 8, np.shape(frame)[0] * 6 // 8]

hat_thickness = [200,100]
hat_top = [hat_center[0] - hat_thickness[0] // 2, hat_center[1] - hat_thickness[1] // 2]
hat_btm = [hat_center[0] + hat_thickness[0] // 2, hat_center[1] + hat_thickness[1] // 2]
hat_top = [hat_top[0] - 50, hat_top[1]]  # Adjust the x-coordinate as needed
hat_btm = [hat_btm[0] - 50, hat_btm[1]]  # Adjust the x-coordinate as needed


snare_thickness = [200,100]
snare_top = [snare_center[0] - snare_thickness[0] // 2, snare_center[1] - snare_thickness[1] // 2]
snare_btm = [snare_center[0] + snare_thickness[0] // 2, snare_center[1] + snare_thickness[1] // 2]
snare_top = [snare_top[0] - 50, snare_top[1]]  # Adjust the x-coordinate as needed
snare_btm = [snare_btm[0] - 50, snare_btm[1]]  # Adjust the x-coordinate as needed


# Set the region for kick drum display
kick_drum_center = [np.shape(frame)[1] * 7 // 8, np.shape(frame)[0] * 6 // 8]

kick_drum_thickness = [200, 100]
kick_drum_top = [kick_drum_center[0] - kick_drum_thickness[0] // 2, kick_drum_center[1] - kick_drum_thickness[1] // 2]
kick_drum_btm = [kick_drum_center[0] + kick_drum_thickness[0] // 2, kick_drum_center[1] + kick_drum_thickness[1] // 2]
time.sleep(1)

# Initialize toggle flags for each region
snare_toggle = False
hat_toggle = False
kick_drum_toggle = False

while True:
    
    # Select the current frame
    ret, frame = camera.read()
    frame = cv2.flip(frame, 1)

    if not ret:
        break
    
    # Reset the beat played flags if the green object is not detected in any region
    if not snare_beat_played:
        snare_toggle = False
    if not hat_beat_played:
        hat_toggle = False
    if not kick_drum_toggle:
        kick_drum_toggle = False
    
    # Select region corresponding to the Snare drum
    snare_region = np.copy(frame[snare_top[1]:snare_btm[1], snare_top[0]:snare_btm[0]])
    mask, snare_toggle = detect_in_region(snare_region, snare_sound, snare_toggle)

    # Select region corresponding to the High Hat
    hat_region = np.copy(frame[hat_top[1]:hat_btm[1], hat_top[0]:hat_btm[0]])
    mask, hat_toggle = detect_in_region(hat_region, hat_sound, hat_toggle)

    # Select region corresponding to the Kick Drum
    kick_drum_region = np.copy(frame[kick_drum_top[1]:kick_drum_btm[1], kick_drum_top[0]:kick_drum_btm[0]])
    mask, kick_drum_toggle = detect_in_region(kick_drum_region, kick_drum_sound, kick_drum_toggle)

    # Output project title
    cv2.putText(frame, "Your text here", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (20, 20, 20), 2)

    
    # If flag is selected, display the region under detection
    if verbose:
        frame[snare_top[1]:snare_btm[1], snare_top[0]:snare_btm[0]] = cv2.bitwise_and(frame[snare_top[1]:snare_btm[1], snare_top[0]:snare_btm[0]], frame[snare_top[1]:snare_btm[1], snare_top[0]:snare_btm[0]], mask=mask[snare_top[1]:snare_btm[1], snare_top[0]:snare_btm[0]])
    
    # If flag is not selected, display the drums
    frame[snare_top[1]:snare_btm[1], snare_top[0]:snare_btm[0]] = cv2.addWeighted(snare, 1, frame[snare_top[1]:snare_btm[1], snare_top[0]:snare_btm[0]], 1, 0)
    frame[hat_top[1]:hat_btm[1], hat_top[0]:hat_btm[0]] = cv2.addWeighted(hat, 1, frame[hat_top[1]:hat_btm[1], hat_top[0]:hat_btm[0]], 1, 0)
    frame[kick_drum_top[1]:kick_drum_btm[1], kick_drum_top[0]:kick_drum_btm[0]] = kick_drum

    # Increase the window size to full screen
    cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Output', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Calculate aspect ratios
    aspect_ratio_frame = frame.shape[1] / frame.shape[0]
    aspect_ratio_screen = 16 / 9  # Assuming 16:9 aspect ratio for fullscreen

    # Resize the frame while maintaining aspect ratio
    if aspect_ratio_frame > aspect_ratio_screen:
        new_width = int(frame.shape[1] * (aspect_ratio_screen / aspect_ratio_frame))
        frame = cv2.resize(frame, (new_width, int(new_width / aspect_ratio_frame)))
    else:
        new_height = int(frame.shape[0] * (aspect_ratio_frame / aspect_ratio_screen))
        frame = cv2.resize(frame, (int(new_height * aspect_ratio_frame), new_height))

    cv2.imshow('Output', frame)
    key = cv2.waitKey(1) & 0xFF
    # 'Q' to exit
    if key == ord("q"):
        break

# Clean up the open windows
camera.release()
cv2.destroyAllWindows()
