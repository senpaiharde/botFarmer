import time, random, logging, keyboard
import pyautogui

from src.capture  import capture_screen
from src.detector import find_trees, find_markers
from config       import (
    GAME_REGION, HARVEST_KEY,
    MIN_DELAY, MAX_DELAY, COOLDOWN
)

logging.basicConfig(filename="logs/bot.log", level=logging.INFO)

_last_harvest = 0

def main_loop():
    global _last_harvest

    state = "seek_tree"   # or "wait_for_marker"
    target = None         # will hold the (x,y) of the tree we’re moving toward

    while True:
        if keyboard.is_pressed('q'):
            break

        gray = capture_screen()

        if state == "seek_tree":
            trees = find_trees(gray)
            if not trees:
                logging.debug("No trees visible")
            else:
                # pick a tree at random
                tx, ty = random.choice(trees)
                # convert to absolute coords
                abs_x = GAME_REGION["left"] + tx
                abs_y = GAME_REGION["top"]  + ty
                logging.info(f"Moving to tree at {(abs_x,abs_y)}")
                pyautogui.moveTo(
                    abs_x + random.randint(-5,5),
                    abs_y + random.randint(-5,5),
                    duration=random.uniform(0.7,1.2)
                )
                pyautogui.click()     # start walking toward tree
                target = (tx, ty)
                state = "wait_for_marker"

        elif state == "wait_for_marker":
            markers = find_markers(gray)
            # filter markers near the target tree (within ~100px)
            close = [
              (mx,my) for mx,my in markers
              if abs(mx - target[0]) < 100 and abs(my - target[1]) < 100
            ]
            if close:
                now = time.time()
                if now - _last_harvest >= COOLDOWN:
                    # press E on the first close marker
                    mx, my = close[0]
                    abs_x = GAME_REGION["left"] + mx
                    abs_y = GAME_REGION["top"]  + my
                    logging.info(f"Pressing E at {(abs_x,abs_y)}")
                    pyautogui.moveTo(abs_x, abs_y, duration=0.3)
                    pyautogui.click()              # ensure focus
                    pyautogui.press(HARVEST_KEY)   # chop
                    _last_harvest = now
                    state = "seek_tree"
            else:
                logging.debug("No E-marker yet; still traveling")

        # small random delay before next frame
        time.sleep(MIN_DELAY + random.random()*(MAX_DELAY-MIN_DELAY))

    logging.info("Bot stopped")
