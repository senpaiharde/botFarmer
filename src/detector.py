# src/detector.py

import cv2
import numpy as np
from config import TREE_TEMPLATES, THRESHOLD

# 1) Preload all your tree icons at import-time
_templates = []
_dims = []
for path in TREE_TEMPLATES:
    tpl = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if tpl is None:
        raise FileNotFoundError(f"Cannot load template: {path}")
    _templates.append(tpl)
    _dims.append(tpl.shape[::-1])  # (width, height)

def find_trees(screen_gray):
    """
    Returns a list of (x, y) coordinates for every tree icon found.
    """
    hits = []
    # 2) For each template, run matchTemplate
    for tpl, (w, h) in zip(_templates, _dims):
        res = cv2.matchTemplate(screen_gray, tpl, cv2.TM_CCOEFF_NORMED)
        ys, xs = np.where(res >= THRESHOLD)
        # 3) Snap each hit to the grid of that template size
        uniques = {(int(x / w) * w, int(y / h) * h) for x, y in zip(xs, ys)}
        hits.extend(uniques)
    # 4) Dedupe across different templates
    return list(set(hits))
