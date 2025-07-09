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
        harvest_path: str,
        region: dict,
        min_matches=12,
        approach_radius=80,
        harvest_thresh=0.7,
        loop_delay=0.2,
        approach_timeout=1.0
    ):
        # ORB & Matcher setup
        self.orb              = cv2.ORB_create(800)
        self.matcher          = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.min_matches      = min_matches
        self.approach_radius  = approach_radius
        self.harvest_thresh   = harvest_thresh
        self.loop_delay       = loop_delay
        self.approach_timeout = approach_timeout

        # Load templates & descriptors
        def load_tpl(path):
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise FileNotFoundError(f"Template not found: {path}")
            kp, des = self.orb.detectAndCompute(img, None)
            return img, kp, des

        self.tree_templates = [load_tpl(p) for p in tree_paths]
        self.e_img, self.e_kp, self.e_des = load_tpl(e_path)

        self.harvest_tpl = cv2.imread(harvest_path, cv2.IMREAD_GRAYSCALE)
        if self.harvest_tpl is None:
            raise FileNotFoundError(f"Harvest template not found: {harvest_path}")

        # Screen region to capture
        self.region = region
        # Single mss instance
        self.sct = mss.mss()

        # Precompute screen-center for approach
        self.center_x = region['left'] + region['width'] // 2
        self.center_y = region['top']  + region['height'] // 2

    def detect_features(self, gray, tpl_kp, tpl_des):
        kp2, des2 = self.orb.detectAndCompute(gray, None)
        if des2 is None:
            return [], None, None
        matches = list(self.matcher.match(tpl_des, des2))
        matches.sort(key=lambda m: m.distance)
        keep = max(self.min_matches, len(matches) // 4)
        return matches[:keep], kp2, des2

    def find_homography(self, tpl_img, tpl_kp, gray, skp, matches):
        src = np.float32([tpl_kp[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
        dst = np.float32([skp[m.trainIdx].pt     for m in matches]).reshape(-1,1,2)
        M, _ = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
        if M is None:
            return None
        h, w = tpl_img.shape
        corners = np.array([[0,0],[w,0],[w,h],[0,h]], dtype=np.float32).reshape(-1,1,2)
        pts = cv2.perspectiveTransform(corners, M).reshape(-1,2).astype(int)
        return pts

    def approach(self, tx, ty):
        start = time.time()
        while True:
            dx = tx - self.center_x
            dy = ty - self.center_y
            dist = (dx*dx + dy*dy)**0.5
            if dist <= self.approach_radius or (time.time() - start) > self.approach_timeout:
                break

            # Strafe
            if dx < -self.approach_radius:
                pyautogui.keyDown('a')
            else:
                pyautogui.keyUp('a')

            if dx > self.approach_radius:
                pyautogui.keyDown('d')
            else:
                pyautogui.keyUp('d')

            # Forward/back
            if dy < -self.approach_radius:
                pyautogui.keyDown('w')
            else:
                pyautogui.keyUp('w')

            if dy > self.approach_radius:
                pyautogui.keyDown('s')
            else:
                pyautogui.keyUp('s')

            time.sleep(0.02)

        # Release all movement keys
        for key in ('w','a','s','d'):
            pyautogui.keyUp(key)

    def template_match(self, gray, tpl, thresh):
        ih, iw = gray.shape
        th, tw = tpl.shape
        if th > ih or tw > iw:
            return False
        res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
        _, maxv, _, _ = cv2.minMaxLoc(res)
        return maxv >= thresh

    def step(self):
        # 1) Capture once
        shot = np.array(self.sct.grab(self.region))[:,:,:3]
        gray = cv2.cvtColor(shot, cv2.COLOR_BGR2GRAY)
        debug = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        # 2) Detect tree
        tree_box = None
        for img, kp, des in self.tree_templates:
            matches, skp, sdes = self.detect_features(gray, kp, des)
            if len(matches) < self.min_matches:
                continue
            pts = self.find_homography(img, kp, gray, skp, matches)
            if pts is not None:
                tree_box = pts + np.array([self.region['left'], self.region['top']])
                cv2.polylines(debug, [tree_box], True, (0,255,0), 2)
                break

        if tree_box is None:
            print("🌲 No tree detected")
            cv2.imwrite("debug_box.png", debug)
            return

        tx = int(tree_box[:,0].mean())
        ty = int(tree_box[:,1].mean())
        print("🌲 Tree found — approaching…")

        # 3) Approach
        self.approach(tx, ty)

        # 4) Harvest
        time.sleep(0.1)
        pyautogui.press('e')
        print("🟢 Pressed E — harvesting")

        # 5) Wait for harvest indicator to appear
        deadline = time.time() + 1.0
        while time.time() < deadline:
            shot2 = np.array(self.sct.grab(self.region))[:,:,:3]
            g2 = cv2.cvtColor(shot2, cv2.COLOR_BGR2GRAY)
            if self.template_match(g2, self.harvest_tpl, self.harvest_thresh):
                break
            time.sleep(0.05)

        # Then wait until it disappears
        while True:
            shot3 = np.array(self.sct.grab(self.region))[:,:,:3]
            g3 = cv2.cvtColor(shot3, cv2.COLOR_BGR2GRAY)
            if not self.template_match(g3, self.harvest_tpl, self.harvest_thresh):
                break
            time.sleep(0.05)

        print("✅ Harvest complete")
        cv2.imwrite("debug_box.png", debug)

    def run(self):
        print("▶️ Press 'Q' to start, '`' to stop.")
        # Wait for start
        while not keyboard.is_pressed('q'):
            time.sleep(0.05)
        print("▶️ Bot running — press '`' to stop.")
        while True:
            if keyboard.is_pressed('`'):
                print("🛑 Bot stopped by user.")
                break
            try:
                self.step()
            except Exception as e:
                print("❌ Error:", e)
            time.sleep(self.loop_delay)

if __name__ == "__main__":
    # Paths to your templates
    tree_paths   = [
        "./Templates/Screenshot_22.png",
        "./Templates/Screenshot_23.png",
        "./Templates/Screenshot_24.png",
        "./Templates/Screenshot_25.png",
    ]
    e_path       = "./Templates/E.png"
    harvest_path = "./Templates/finish.png"

    # Exact region of your game viewport
    region = {
        "left":   200,
        "top":    150,
        "width":  1200,
        "height":  700,
    }

    bot = BotController(
        tree_paths=tree_paths,
        e_path=e_path,
        harvest_path=harvest_path,
        region=region,
        min_matches=12,
        approach_radius=80,
        harvest_thresh=0.7,
        loop_delay=0.2,
        approach_timeout=1.0
    )
    bot.run()
