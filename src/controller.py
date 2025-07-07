# src/controller.py

import time, random, logging, keyboard
from src.capture  import capture_screen
from src.detector import find_trees
from src.mover    import move_and_interact
from config       import MIN_DELAY, MAX_DELAY

logging.basicConfig(filename="logs/bot.log", level=logging.INFO)

def main_loop():
    logging.info("Bot started")
    while True:
        if keyboard.is_pressed('q'):
            logging.info("Quit key—stopping.")
            break

        try:
            gray   = capture_screen()
            trees  = find_trees(gray)

            if trees:
                pt      = random.choice(trees)
                success = move_and_interact(pt)
                action  = "Interacted" if success else "Cooling down"
                logging.info(f"{action} at {pt}")
            else:
                logging.info("No trees found")

        except Exception:
            logging.exception("Error in loop")

        # randomized pause
        time.sleep(MIN_DELAY + random.random()*(MAX_DELAY - MIN_DELAY))

    logging.info("Bot stopped")
