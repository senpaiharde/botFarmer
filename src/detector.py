# src/detector.py
import cv2, numpy as np
from config import TEMPLATE_PATH, THRESHOLD

_template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
_h, _w = _template.shape

def find_trees(screen_gray):
    res = cv2.matchTemplate(screen_gray, _template, cv2.TM_CCOEFF_NORMED)
    ys, xs = np.where(res >= THRESHOLD)
    # cluster points so you don’t chop the same tree 5 times:
    unique = {(int(x/_w)*_w, int(y/_h)*_h) for x, y in zip(xs, ys)}
    return list(unique)
