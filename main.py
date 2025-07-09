import time
import keyboard
from controller import (
    find_tree_and_move, find_marker_and_harvest,
    pan_camera, cleanup
)
from config import QUIT_KEY, LOOP_SLEEP

if __name__ == '__main__':
    state = 'search_tree'
    print(f"Bot started. Press '{QUIT_KEY.upper()}' to exit.")
    try:
        while True:
            if keyboard.is_pressed(QUIT_KEY):
                print('Quit key pressed.')
                break

            if state == 'search_tree':
                if find_tree_and_move():
                    state = 'harvest_marker'
            elif state == 'harvest_marker':
                if find_marker_and_harvest():
                    pan_camera()
                    state = 'search_tree'

            time.sleep(LOOP_SLEEP)

    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
        print('Exited.')