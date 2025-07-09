import cv2
import numpy as np
from mss import mss
from config import GAME_REGION

sct = mss()

def grab_frame():
    img = np.array(sct.grab(GAME_REGION))
    bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return bgr, gray