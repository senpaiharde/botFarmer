# src/mover.py
import time, random, pyautogui
from config import GAME_REGION, HARVEST_KEY, COOLDOWN, MIN_DELAY, MAX_DELAY
from src.detector import _dims

_last_action = 0

def human_delay():
    return MIN_DELAY + random.random() * (MAX_DELAY - MIN_DELAY)

def move_and_interact(point):
    global _last_action
    now = time.time()
    if now - _last_action < COOLDOWN:
        print(f"[DEBUG] mover: on cooldown ({now-_last_action:.2f}s elapsed)")
        return False

    x, y = point
    abs_x = GAME_REGION["left"] + x
    abs_y = GAME_REGION["top"]  + y
    print(f"[DEBUG] mover: moving to absolute ({abs_x},{abs_y}) and interacting")

    pyautogui.moveTo(
        abs_x + random.randint(-5, 5),
        abs_y + random.randint(-5, 5),
        duration=random.uniform(0.3, 0.7)
    )
    time.sleep(human_delay())
    pyautogui.click()
    time.sleep(human_delay())
    pyautogui.press(HARVEST_KEY)

    _last_action = now
    return True
