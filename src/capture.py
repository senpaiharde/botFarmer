# src/capture.py
import mss, numpy as np, cv2
from config import GAME_REGION

def capture_screen():
    with mss.mss() as sct:
        mon = GAME_REGION
        img = np.array(sct.grab(mon))[:, :, :3]    # drop alpha
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
