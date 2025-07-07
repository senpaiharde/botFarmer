# src/mover.py

import time, random, pyautogui
from config import GAME_REGION, INTERACTION_KEY, COOLDOWN, MIN_DELAY, MAX_DELAY

# You can ignore the old E-icon dims; for trees we just click and press INTERACTION_KEY.

_last_action = 0

def human_delay():
    return MIN_DELAY + random.random() * (MAX_DELAY - MIN_DELAY)

def move_and_interact(point):
    """
    point: (x, y) within GAME_REGION where a tree icon was found.
    Clicks the tree, then presses INTERACTION_KEY (e.g. "e").
    """
    global _last_action
    now = time.time()
    if now - _last_action < COOLDOWN:
        return False

    x, y = point
    abs_x = GAME_REGION["left"] + x
    abs_y = GAME_REGION["top"]  + y

    # 1) Move & click
    pyautogui.moveTo(
        abs_x + random.randint(-5, 5),
        abs_y + random.randint(-5, 5),
        duration=random.uniform(0.3, 0.7)
    )
    time.sleep(human_delay())
    pyautogui.click()
    time.sleep(human_delay())

    # 2) Press the interaction key (harvest)
    pyautogui.press(INTERACTION_KEY)

    _last_action = now
    return True
