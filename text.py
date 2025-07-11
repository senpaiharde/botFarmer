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
        harvest_path: str,
        finish_tpl_path: str,
        region: dict,
        min_matches=12,
        x_thresh=50,
        forward_time=0.5,
        harvest_thresh=0.7,
        loop_delay=0.2
    ):
        # ORB & matcher
        self.orb         = cv2.ORB_create(800)
        self.matcher     = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.min_matches = min_matches
        self.x_thresh    = x_thresh
        self.forward_time= forward_time
        self.harvest_thresh = harvest_thresh
        self.loop_delay  = loop_delay

        # load tree templates (no E template needed)
        def load_tpl(path):
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise FileNotFoundError(path)
            kp, des = self.orb.detectAndCompute(img, None)
            return img, kp, des

        self.tree_templates = [load_tpl(p) for p in tree_paths]

        # finish-animation template
        self.finish_tpl = cv2.imread(finish_tpl_path, cv2.IMREAD_GRAYSCALE)
        if self.finish_tpl is None:
            raise FileNotFoundError(finish_tpl_path)

        # capture region & grabber
        self.region = region
        self.sct    = mss.mss()

        # precompute region center
        self.cx = region['left'] + region['width']//2
        self.cy = region['top']  + region['height']//2

    def detect_features(self, gray, tpl_kp, tpl_des):
        kp2, des2 = self.orb.detectAndCompute(gray, None)
        if des2 is None:
            return [], None, None
        matches = list(self.matcher.match(tpl_des, des2))
        matches.sort(key=lambda m: m.distance)
        keep = max(self.min_matches, len(matches)//4)
        return matches[:keep], kp2, des2

    def find_homography(self, tpl_img, tpl_kp, gray, skp, matches):
        src = np.float32([tpl_kp[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
        dst = np.float32([skp[m.trainIdx].pt     for m in matches]).reshape(-1,1,2)
        M, _ = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
        if M is None:
            return None
        h, w = tpl_img.shape
        corners = np.array([[0,0],[w,0],[w,h],[0,h]], dtype=np.float32).reshape(-1,1,2)
        return cv2.perspectiveTransform(corners, M).reshape(-1,2).astype(int)

    def template_match(self, gray, tpl, thresh):
        ih, iw = gray.shape
        th, tw = tpl.shape
        if th>ih or tw>iw:
            return False
        res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
        _, maxv, _, _ = cv2.minMaxLoc(res)
        return maxv>=thresh

    def step(self):
        # capture screen
        shot = np.array(self.sct.grab(self.region))[:,:,:3]
        gray = cv2.cvtColor(shot, cv2.COLOR_BGR2GRAY)

        # detect tree
        tree_box = None
        for img, kp, des in self.tree_templates:
            matches, skp, sdes = self.detect_features(gray, kp, des)
            if len(matches) < self.min_matches:
                continue
            pts = self.find_homography(img, kp, gray, skp, matches)
            if pts is not None:
                tree_box = pts + np.array([self.region['left'], self.region['top']])
                break

        if tree_box is None:
            print("🌲 No tree")
            return

        # compute tree center
        tx = int(tree_box[:,0].mean())
        ty = int(tree_box[:,1].mean())
        print(f"🌲 Tree at ({tx},{ty})")

        # 1) Align X axis
        dx = tx - self.cx
        if abs(dx) > self.x_thresh:
            key = 'a' if dx < 0 else 'd'
            pyautogui.keyDown(key)
            time.sleep(0.2)
            pyautogui.keyUp(key)

        # 2) Move forward
        pyautogui.keyDown('w')
        time.sleep(self.forward_time)
        pyautogui.keyUp('w')

        # 3) Harvest
        time.sleep(0.1)
        pyautogui.press('e')
        print("🟢 Pressed E")

        # 4) Wait for finish animation
        # appear
        deadline = time.time()+1.0
        while time.time()<deadline:
            shot2 = np.array(self.sct.grab(self.region))[:,:,:3]
            g2 = cv2.cvtColor(shot2, cv2.COLOR_BGR2GRAY)
            if self.template_match(g2, self.finish_tpl, self.harvest_thresh):
                break
            time.sleep(0.05)
        # disappear
        while True:
            shot3 = np.array(self.sct.grab(self.region))[:,:,:3]
            g3 = cv2.cvtColor(shot3, cv2.COLOR_BGR2GRAY)
            if not self.template_match(g3, self.finish_tpl, self.harvest_thresh):
                break
            time.sleep(0.05)

        # 5) slight random mouse drift
        cx, cy = pyautogui.position()
        nx = cx + random.randint(-50,50)
        ny = cy + random.randint(-50,50)
        pyautogui.moveTo(nx, ny, duration=0.5)

    def run(self):
        print("▶️ Press 'Q' to start, '`' to stop.")
        while not keyboard.is_pressed('q'):
            time.sleep(0.05)
        print("▶️ Running…")
        while True:
            if keyboard.is_pressed('`'):
                print("🛑 Stopped")
                break
            try:
                self.step()
            except Exception as e:
                print("❌", e)
            time.sleep(self.loop_delay)

if __name__ == "__main__":
    tree_paths   = [
        "./Templates/Screenshot_22.png",
        "./Templates/Screenshot_23.png",
        "./Templates/Screenshot_24.png",
        "./Templates/Screenshot_25.png",
    ]
    harvest_path     = "./Templates/finish.png"
    finish_tpl_path  = "./Templates/finish.png"  # same as harvest indicator
    region = {"left":200,"top":150,"width":1200,"height":700}

    bot = BotController(
        tree_paths=tree_paths,
        harvest_path=harvest_path,
        finish_tpl_path=finish_tpl_path,
        region=region,
        min_matches=12,
        x_thresh=50,
        forward_time=0.5,
        harvest_thresh=0.7,
        loop_delay=0.2
    )
    bot.run()
