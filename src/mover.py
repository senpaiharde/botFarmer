# src/mover.py
import time, random, pyautogui
from config import GAME_REGION, HARVEST_KEY, COOLDOWN, MIN_DELAY, MAX_DELAY

_last_chop = 0

def human_delay():
    return MIN_DELAY + random.random()*(MAX_DELAY - MIN_DELAY)

def move_and_chop(point):
    global _last_chop
    now = time.time()
    if now - _last_chop < COOLDOWN:
        return False

    x, y = point
    abs_x = GAME_REGION["left"] + x + _w//2
    abs_y = GAME_REGION["top"]  + y + _h//2
    # move with slight randomness
    pyautogui.moveTo(abs_x + random.randint(-5,5),
                     abs_y + random.randint(-5,5),
                     duration=random.uniform(0.3,0.7))
    time.sleep(human_delay())
    pyautogui.click()
    time.sleep(human_delay())
    pyautogui.press(HARVEST_KEY)
    _last_chop = now
    return True
