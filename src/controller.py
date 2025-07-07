# src/controller.py
import time, random, logging, keyboard
from capture import capture_screen
from detector import find_trees
from mover import move_and_chop
from config import MIN_DELAY, MAX_DELAY

logging.basicConfig(filename="logs/bot.log", level=logging.INFO)

def main_loop():
    logging.info("Bot started")
    while True:
        if keyboard.is_pressed('q'):
            logging.info("Quit key pressed, stopping")
            break

        try:
            gray = capture_screen()
            trees = find_trees(gray)
            if trees:
                x, y = random.choice(trees)
                success = move_and_chop((x, y))
                logging.info(f"{'Chopped' if success else 'Cooldown'} at {(x,y)}")
            else:
                logging.info("No trees found")
        except Exception as e:
            logging.exception("Unexpected error in loop")

        time.sleep(MIN_DELAY + random.random()*(MAX_DELAY-MIN_DELAY))

    logging.info("Bot stopped")
