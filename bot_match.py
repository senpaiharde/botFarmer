import time
import random
import cv2
import pyautogui
import numpy as np
import mss
import keyboard

# === Load template ===
template = cv2.imread("./Templates/E.png", cv2.IMREAD_GRAYSCALE)
h, w = template.shape[:2]

# === Set crop region (center-bottom of screen) ===
screen_width, screen_height = pyautogui.size()
crop_width, crop_height = 600, 450  # Tighten crop = faster
left = (screen_width // 2) - (crop_width // 2)
top = screen_height - crop_height - 200

def match_template(screen_img, template_img, threshold=0.7):
    result = cv2.matchTemplate(screen_img, template_img, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    print("🎯 Match confidence:", max_val)
    cv2.rectangle(gray, max_loc, (max_loc[0]+w, max_loc[1]+h), (255, 0, 0), 2)
    cv2.imwrite("debug_box.png", gray)
    return max_val >= threshold, max_loc
    
while True:
    with mss.mss() as sct:
        monitor = {"top": top, "left": left, "width": crop_width, "height": crop_height}
        sct_img = sct.grab(monitor)
        frame = np.array(sct_img)[:, :, :3]  # remove alpha
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    matched, max_loc = match_template(gray, template)

    if matched:
        pyautogui.press('e')
        print("🟢 Pressed E")
    else:
        print("🔴 No match")
    if keyboard.is_pressed('q'):
    print("🛑 Stopping bot.")
    break
    BASE_DELAY = 0.1
    RAND_RANGE = 0.2
    time.sleep(BASE_DELAY + random.random() * RAND_RANGE)  # ultra-fast loop
