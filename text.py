import time
import random
import cv2
import numpy as np
import mss
import pyautogui
import keyboard

class BotController:
    def __init__(
        self,
        tree_paths: list,
        e_path: str,
        crop_width=800,
        crop_height=800,
        bottom_offset=200,
        min_matches=12,
        approach_radius=100,   # pixels: how close before we stop moving
    ):
        self.min_matches     = min_matches
        self.approach_radius = approach_radius

        # ORB + BFMatcher setup
        self.orb     = cv2.ORB_create(1000)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # load templates & precompute kps/descriptors
        self.tree_templates = []
        for p in tree_paths:
            img = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
            kp, des = self.orb.detectAndCompute(img, None)
            self.tree_templates.append((img, kp, des))

        self.e_img = cv2.imread(e_path, cv2.IMREAD_GRAYSCALE)
        self.e_kp, self.e_des = self.orb.detectAndCompute(self.e_img, None)

        # screen crop region
        sw, sh = pyautogui.size()
        left = (sw//2) - (crop_width//2)
        top  = sh - crop_height - bottom_offset
        self.region = {"top": top, "left": left, "width": crop_width, "height": crop_height}

    def detect_features(self, scene_gray, tpl_kp, tpl_des):
        # detect keypoints/descriptors in the current scene
        scene_kp, scene_des = self.orb.detectAndCompute(scene_gray, None)
        if scene_des is None:
            return [], None, None

        # force to list so .sort() always works
        matches = list(self.matcher.match(tpl_des, scene_des))
        matches.sort(key=lambda m: m.distance)

        # keep only the top 25% or at least min_matches
        cutoff = max(self.min_matches, len(matches)//4)
        good = matches[:cutoff]

        return good, scene_kp, scene_des

    def find_homography_box(self, tpl_img, tpl_kp, scene_gray, scene_kp, matches):
        src = np.float32([tpl_kp[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
        dst = np.float32([scene_kp[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
        M, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
        if M is None: return None
        h, w = tpl_img.shape
        corners = np.float32([[0,0],[w,0],[w,h],[0,h]]).reshape(-1,1,2)
        pts = cv2.perspectiveTransform(corners, M).reshape(-1,2).astype(int)
        return pts

    def move_mouse_smooth(self, tx, ty):
        cx, cy = pyautogui.position()
        steps = random.randint(10,20)
        dx = (tx-cx)/steps; dy = (ty-cy)/steps
        for i in range(steps):
            x = cx + dx*(i+1) + random.uniform(-2,2)
            y = cy + dy*(i+1) + random.uniform(-2,2)
            pyautogui.moveTo(x,y, duration=0.01)

    def approach_tree(self, tx, ty, center_x, center_y):
        """
        Move using WASD so that the tree (tx,ty) comes within approach_radius of center.
        """
        dx = tx - center_x
        dy = ty - center_y

        # Decide strafe left/right
        if abs(dx) > self.approach_radius:
            key = 'a' if dx < 0 else 'd'
            pyautogui.keyDown(key)
            time.sleep(0.3 + random.random()*0.2)
            pyautogui.keyUp(key)

        # Decide forward/back
        if abs(dy) > self.approach_radius:
            key = 'w' if dy < 0 else 's'
            pyautogui.keyDown(key)
            time.sleep(0.3 + random.random()*0.2)
            pyautogui.keyUp(key)

    def step(self):
        # 1) Capture scene
        with mss.mss() as sct:
            shot = np.array(sct.grab(self.region))[:, :, :3]
        scene_gray = cv2.cvtColor(shot, cv2.COLOR_BGR2GRAY)
        debug = cv2.cvtColor(scene_gray, cv2.COLOR_GRAY2BGR)

        # 2) Find the tree
        tree_box = None
        for img, kp, des in self.tree_templates:
            matches, skp, sdes = self.detect_features(scene_gray, kp, des)
            if len(matches) >= self.min_matches:
                box = self.find_homography_box(img, kp, scene_gray, skp, matches)
                if box is not None:
                    tree_box = box + np.array([self.region['left'], self.region['top']])
                    cv2.polylines(debug, [tree_box], True, (0,255,0), 3)
                    break

        if tree_box is None:
            print("🌲 No tree detected")
            cv2.imwrite("debug_box.png", debug)
            return

        print("🌲 Tree detected")
        tx = int(tree_box[:,0].mean())
        ty = int(tree_box[:,1].mean())

        # 3) Approach with WASD until within radius
        # We'll loop small steps of approach until close enough:
        sw, sh = pyautogui.size()
        center_x = sw//2
        center_y = sh - (self.region['height']//2) - self.region['top']

        # Keep approaching until inside radius or timeout
        start = time.time()
        while True:
            dx = tx - center_x
            dy = ty - center_y
            dist = (dx*dx + dy*dy)**0.5
            if dist <= self.approach_radius or time.time() - start > 3:
                break
            # strafe if needed
            if abs(dx) > self.approach_radius:
                key = 'a' if dx < 0 else 'd'
                pyautogui.keyDown(key); time.sleep(0.2); pyautogui.keyUp(key)
            # forward/back
            if abs(dy) > self.approach_radius:
                key = 'w' if dy < 0 else 's'
                pyautogui.keyDown(key); time.sleep(0.2); pyautogui.keyUp(key)
            time.sleep(0.05)

        # 4) Harvest: always press E
        time.sleep(0.2 + random.random()*0.1)
        pyautogui.press('e')
        print("🟢 Pressed E to harvest")

        # 5) Wait for the animation to complete
        time.sleep(1.0 + random.random()*0.3)

        # 6) Dump debug and return
        cv2.imwrite("debug_box.png", debug)
        return


    def run(self, delay=0.3):
        print("▶️ Bot started. Press ‘q’ to stop.")
        while True:
            if keyboard.is_pressed('q'):
                print("🛑 Stopped by user.")
                break
            try:
                self.step()
            except Exception as e:
                print("❌ Error:", e)
            time.sleep(delay)

if __name__ == "__main__":
    tree_paths = [
        "./Templates/Screenshot_22.png",
        "./Templates/Screenshot_23.png",
        "./Templates/Screenshot_24.png",
        "./Templates/Screenshot_25.png",
    ]
    e_path = "./Templates/E.png"

    bot = BotController(
        tree_paths=tree_paths,
        e_path=e_path,
        crop_width=800,
        crop_height=800,
        bottom_offset=200,
        min_matches=12,
        approach_radius=120,
    )
    bot.run()
