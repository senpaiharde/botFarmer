# src/detector.py

import cv2
import numpy as np
from config import TREE_TEMPLATES, MARKER_TEMPLATE, THRESHOLD

# --- Preload all tree templates ---
_tree_templates = []
_tree_dims      = []
for path in TREE_TEMPLATES:
    tpl = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if tpl is None:
        raise FileNotFoundError(f"Cannot load tree template: {path}")
    h, w = tpl.shape
    _tree_templates.append(tpl)
    _tree_dims.append((w, h))
print(f"[DEBUG] Loaded {len(_tree_templates)} tree templates, dims={_tree_dims}")

# --- Preload the E-marker template ---
_marker = cv2.imread(MARKER_TEMPLATE, cv2.IMREAD_GRAYSCALE)
if _marker is None:
    raise FileNotFoundError(f"Cannot load marker template: {MARKER_TEMPLATE}")
_marker_h, _marker_w = _marker.shape
print(f"[DEBUG] Loaded marker template size: {_marker_w}×{_marker_h}")


def find_trees(screen_gray):
    """
    Detects all tree-icon matches in the gray screenshot.
    Returns a list of (x, y) offsets within screen_gray.
    """
    hits = set()
    img_h, img_w = screen_gray.shape

    for tpl, (w, h) in zip(_tree_templates, _tree_dims):
        # skip templates larger than the crop
        if w > img_w or h > img_h:
            print(f"[WARN] Skipping tree tpl {w}×{h} (larger than {img_w}×{img_h})")
            continue

        res = cv2.matchTemplate(screen_gray, tpl, cv2.TM_CCOEFF_NORMED)
        ys, xs = np.where(res >= THRESHOLD)
        print(f"[DEBUG] find_trees: template {w}×{h} raw matches = {len(xs)}")

        # cluster nearby hits by snapping to the template grid
        for x, y in zip(xs, ys):
            grid_x = (x // w) * w
            grid_y = (y // h) * h
            hits.add((grid_x, grid_y))

    print(f"[DEBUG] find_trees returning {len(hits)} hits: {hits}")
    return list(hits)


def find_markers(screen_gray):
    """
    Detects all “press-E” marker matches in the gray screenshot.
    Returns a list of (x, y) offsets within screen_gray.
    """
    hits = set()
    img_h, img_w = screen_gray.shape

    # skip if marker is larger than the crop
    if _marker_w > img_w or _marker_h > img_h:
        print(f"[WARN] Marker tpl {_marker_w}×{_marker_h} larger than crop {img_w}×{img_h}")
        return []

    res = cv2.matchTemplate(screen_gray, _marker, cv2.TM_CCOEFF_NORMED)
    ys, xs = np.where(res >= THRESHOLD)
    print(f"[DEBUG] find_markers raw matches = {len(xs)}")

    for x, y in zip(xs, ys):
        grid_x = (x // _marker_w) * _marker_w
        grid_y = (y // _marker_h) * _marker_h
        hits.add((grid_x, grid_y))

    print(f"[DEBUG] find_markers returning {len(hits)} hits: {hits}")

    # Optional: save a debug image to logs/debug_markers.png
    debug = cv2.cvtColor(screen_gray, cv2.COLOR_GRAY2BGR)
    for gx, gy in hits:
        cv2.rectangle(debug, (gx, gy), (gx+_marker_w, gy+_marker_h), (0,255,0), 2)
    cv2.imwrite("logs/debug_markers.png", debug)

    return list(hits)
