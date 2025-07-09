import pyautogui
from pathlib import Path

# Screen capture region
W, H = pyautogui.size()
GAME_REGION = dict(
    left=W//2 - 300,
    top=H - 650,
    width=600,
    height=450
)

# Template folders
TREE_TEMPLATES = list(Path('templates').glob('Screenshot_*.png'))
MARKER_TEMPLATE = Path('templates/E.png')  # the E icon

# Detection thresholds
TREE_THRESHOLD = 0.7
MARKER_THRESHOLD = 0.75

# Keys
HARVEST_KEY = 'e'
QUIT_KEY = 'q'

# Timing
LOOP_SLEEP = 0.1
AFTER_MOVE_DELAY = 0.5
AFTER_HARVEST_DELAY = 1.0
CAMERA_PAN_DURATION = 0.3  # seconds