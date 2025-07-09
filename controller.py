# controller.py
import cv2
import numpy as np
import pyautogui
import time
import random
import keyboard
from capture import grab_frame
from config import (
    TREE_TEMPLATES, MARKER_TEMPLATE,
    GAME_REGION, TREE_THRESHOLD, MARKER_THRESHOLD,
    HARVEST_KEY, QUIT_KEY,
    AFTER_MOVE_DELAY, AFTER_HARVEST_DELAY, CAMERA_PAN_DURATION
)

# Load all tree templates
tree_templates = []
for path in TREE_TEMPLATES:
    tpl = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if tpl is None:
        raise FileNotFoundError(f"Cannot load tree template {path}")
    tree_templates.append((path.name, tpl))

# Load marker template
marker = cv2.imread(str(MARKER_TEMPLATE), cv2.IMREAD_GRAYSCALE)
if marker is None:
    raise FileNotFoundError(f"Cannot load marker template {MARKER_TEMPLATE}")
th_m, tw_m = marker.shape[:2]


def detect_best_template(gray, templates, threshold):
    """
    Returns (name, loc, tpl_h, tpl_w) of the best match above threshold, else None.
    """
    best = None
    for name, tpl in templates:
        res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold and (best is None or max_val > best[0]):
            best = (max_val, name, max_loc, tpl.shape[0], tpl.shape[1])
    return best  # (score, name, loc, h, w) or None


def move_and_click(x, y):
    pyautogui.moveTo(x, y, duration=AFTER_MOVE_DELAY)
    pyautogui.press(HARVEST_KEY)


def pan_camera():
    # simple right-drag for a small random pan
    dx = random.randint(-100,100)
    dy = random.randint(-20,20)
    pyautogui.mouseDown(button='right')
    pyautogui.moveRel(dx, dy, duration=CAMERA_PAN_DURATION)
    pyautogui.mouseUp(button='right')


def find_tree_and_move():
    bgr, gray = grab_frame()
    hit = detect_best_template(gray, tree_templates, TREE_THRESHOLD)
    if hit:
        _, name, (x, y), h, w = hit
        abs_x = GAME_REGION['left'] + x + w//2
        abs_y = GAME_REGION['top'] + y + h//2
        move_and_click(abs_x, abs_y)
        print(f"Moving to tree {name} at ({abs_x},{abs_y})")
        time.sleep(AFTER_HARVEST_DELAY)
        return True
    return False


def find_marker_and_harvest():
    bgr, gray = grab_frame()
    # treat marker as single-item list
    hit = detect_best_template(gray, [(MARKER_TEMPLATE.name, marker)], MARKER_THRESHOLD)
    if hit:
        _, name, (x, y), h, w = hit
        abs_x = GAME_REGION['left'] + x + w//2
        abs_y = GAME_REGION['top'] + y + h//2
        move_and_click(abs_x, abs_y)
        print(f"Harvested marker at ({abs_x},{abs_y})")
        time.sleep(AFTER_HARVEST_DELAY)
        return True
    return False

www
def cleanup():
    cv2.destroyAllWindows()