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
        min_matches=10,           # minimum ORB matches to consider a detection
    ):
        # --- Load grayscale images and detect their keypoints/descriptors ---
        self.orb = cv2.ORB_create(1000)
        self.tree_templates = []
        for p in tree_paths:
            img = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise FileNotFoundError(f"Cannot load tree template: {p}")
            kp, des = self.orb.detectAndCompute(img, None)
            self.tree_templates.append((img, kp, des))

        self.e_img = cv2.imread(e_path, cv2.IMREAD_GRAYSCALE)
        if self.e_img is None:
            raise FileNotFoundError(f"Cannot load E template: {e_path}")
        self.e_kp, self.e_des = self.orb.detectAndCompute(self.e_img, None)

        # BFMatcher with Hamming distance (for ORB)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        self.min_matches = min_matches

        # Compute crop region (center-bottom)
        sw, sh = pyautogui.size()
        left = (sw // 2) - (crop_width // 2)
        top = sh - crop_height - bottom_offset
        self.region = {"top": top, "left": left, "width": crop_width, "height": crop_height}

    def detect_features(self, scene_gray, tpl_kp, tpl_des):
        """Return list of good matches between scene and template."""
        kp2, des2 = self.orb.detectAndCompute(scene_gray, None)
        if des2 is None or len(des2) < 10:
            return [], None, None
        matches = self.matcher.match(tpl_des, des2)
        # keep only the top 25% best matches by distance
        matches = sorted(matches, key=lambda x: x.distance)
        good = matches[: max(self.min_matches, len(matches)//4) ]
        return good, kp2, des2

    def find_homography_box(self, tpl_img, tpl_kp, scene_gray, scene_kp, matches):
        """Compute homography and return the four corners of the detected template in scene coords."""
        src_pts = np.float32([ tpl_kp[m.queryIdx].pt for m in matches ]).reshape(-1,1,2)
        dst_pts = np.float32([ scene_kp[m.trainIdx].pt for m in matches ]).reshape(-1,1,2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is None:
            return None
        h, w = tpl_img.shape
        # corners of the template
        corners = np.float32([[0,0],[w,0],[w,h],[0,h]]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(corners, M)
        return dst.reshape(-1,2).astype(int)

    def step(self):
        # 1) grab screen crop
        with mss.mss() as sct:
            shot = np.array(sct.grab(self.region))[:, :, :3]
        scene_gray = cv2.cvtColor(shot, cv2.COLOR_BGR2GRAY)
        debug = cv2.cvtColor(scene_gray, cv2.COLOR_GRAY2BGR)

        # 2) try each tree template
        tree_box = None
        for tpl_img, tpl_kp, tpl_des in self.tree_templates:
            matches, scene_kp, scene_des = self.detect_features(scene_gray, tpl_kp, tpl_des)
            if len(matches) >= self.min_matches:
                box = self.find_homography_box(tpl_img, tpl_kp, scene_gray, scene_kp, matches)
                if box is not None:
                    tree_box = box + np.array([self.region["left"], self.region["top"]])
                    # draw and break on first detection
                    cv2.polylines(debug, [tree_box], True, (0,255,0), 3)
                    break

        if tree_box is None:
            print("🌲 No tree detected")
            cv2.imwrite("debug_box.png", debug)
            return
        print("🌲 Tree detected")

        # compute tree center
        tx = int(tree_box[:,0].mean())
        ty = int(tree_box[:,1].mean())

        # 3) move & forward
        self.move_mouse_smooth(tx + random.randint(-10,10), ty + random.randint(-10,10))
        pyautogui.keyDown("w")
        time.sleep(0.5 + random.random()*0.2)
        pyautogui.keyUp("w")

        # 4) detect E prompt in the same crop
        matches_e, scene_kp2, scene_des2 = self.detect_features(scene_gray, self.e_kp, self.e_des)
        e_box = None
        if len(matches_e) >= self.min_matches:
            e_box = self.find_homography_box(self.e_img, self.e_kp, scene_gray, scene_kp2, matches_e)
            if e_box is not None:
                e_box = e_box + np.array([self.region["left"], self.region["top"]])
                cv2.polylines(debug, [e_box], True, (0,0,255), 2)
                # press E at the center
                ex = int(e_box[:,0].mean())
                ey = int(e_box[:,1].mean())
                self.move_mouse_smooth(ex, ey)
                pyautogui.press("e")
                print("🔲 E pressed")

        # dump debug
        cv2.imwrite("debug_box.png", debug)

    def move_mouse_smooth(self, tx, ty):
        cx, cy = pyautogui.position()
        steps = random.randint(10, 20)
        dx = (tx - cx) / steps
        dy = (ty - cy) / steps
        for i in range(steps):
            nx = cx + dx*(i+1) + random.uniform(-2,2)
            ny = cy + dy*(i+1) + random.uniform(-2,2)
            pyautogui.moveTo(nx, ny, duration=0.01)

    def run(self, delay=0.3):
        print("▶️ Bot started. Press ‘q’ to stop.")
        while True:
            if keyboard.is_pressed("q"):
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
    )
    bot.run()
