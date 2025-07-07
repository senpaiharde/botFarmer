import pyautogui
import pytesseract
import time
import random

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def scan_screen():
    screenshot = pyautogui.screenshot()

    # Get screen size
    screen_width, screen_height = pyautogui.size()

    # Define cropping area (center bottom area of screen)
    crop_width = 600
    crop_height = 750

    left = (screen_width // 2) - (crop_width // 2)
    top = screen_height - crop_height - 200  # 100px above bottom
    right = left + crop_width
    bottom = top + crop_height

    cropped = screenshot.crop((left, top, right, bottom))
    cropped.save("cropped_screen.png")  # for debugging

    text = pytesseract.image_to_string(cropped)
    print("OCR Output:", text)
    return text.lower()


def press_e():
    pyautogui.press('e')
    print("Pressed E")

while True:
    screen_text = scan_screen()
    
    if "collect" in screen_text or "e" in screen_text:
        press_e()
    else:
        print("Nothing detected.")

    time.sleep(2 + random.random() * 1.5) # randomize delay
