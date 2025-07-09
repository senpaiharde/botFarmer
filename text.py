import time, random
import cv2, numpy as np, mss
import pyautogui, keyboard

class BotController:
    def __init__(self,
                 tree_paths: list,         # filepaths for your 4 tree PNGs
                 e_path: str,              # filepath for E.png
                 crop_width=600,
                 crop_height=450,
                 bottom_offset=200,
                 tree_thresh=0.7,
                 e_thresh=0.7):
        # Load templates
        self.tree_templates = [cv2.imread(p, cv2.IMREAD_GRAYSCALE) for p in tree_paths]
        self.e_template     = cv2.imread(e_path, cv2.IMREAD_GRAYSCALE)
        self.tree_thresh    = tree_thresh
        self.e_thresh       = e_thresh

        # Compute dynamic crop region (center-bottom)
        sw, sh = pyautogui.size()
        left = (sw//2) - (crop_width//2)
        top  = sh - crop_height - bottom_offset
        self.region = {"top": top, "left": left, "width": crop_width, "height": crop_height}

        self.running = True

    def match_best(self, img_gray, templates, threshold):
        best_score, best_loc, best_tpl = 0, None, None
        for tpl in templates:
            res = cv2.matchTemplate(img_gray, tpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val > best_score:
                best_score, best_loc, best_tpl = max_val, max_loc, tpl
        return (best_score >= threshold), best_loc, best_score, best_tpl

    def move_mouse_smooth(self, tx, ty):
        cx, cy = pyautogui.position()
        steps = random.randint(10, 20)
        dx = (tx - cx) / steps
        dy = (ty - cy) / steps
        for i in range(steps):
            nx = cx + dx*(i+1) + random.uniform(-2,2)
            ny = cy + dy*(i+1) + random.uniform(-2,2)
            pyautogui.moveTo(nx, ny, duration=0.01)

    def step(self):
        # grab screen
        with mss.mss() as sct:
            shot = np.array(sct.grab(self.region))[:,:,:3]
        gray = cv2.cvtColor(shot, cv2.COLOR_BGR2GRAY)

        # 1) Tree detection
        found_tree, loc, score, tpl = self.match_best(gray, self.tree_templates, self.tree_thresh)
        print(f"🌲 Tree found={found_tree} score={score:.2f}")
        if not found_tree:
            self._export_debug(gray, [], None)
            return

        # On-screen tree center
        tx = self.region['left'] + loc[0] + tpl.shape[1]//2
        ty = self.region['top']  + loc[1] + tpl.shape[0]//2

        # 2) Move toward tree
        self.move_mouse_smooth(tx + random.randint(-10,10), ty + random.randint(-10,10))
        # press W to move forward; you can adjust timing for A/S/D as needed
        pyautogui.keyDown('w')
        time.sleep(0.5 + random.random()*0.3)
        pyautogui.keyUp('w')

        # 3) “E” detection
        time.sleep(0.2 + random.random()*0.1)
        with mss.mss() as sct:
            shot2 = np.array(sct.grab(self.region))[:,:,:3]
        gray2 = cv2.cvtColor(shot2, cv2.COLOR_BGR2GRAY)
        found_e, eloc, escore, etpl = self.match_best(gray2, [self.e_template], self.e_thresh)
        print(f"🔲 E found={found_e} score={escore:.2f}")

        if found_e:
            ex = self.region['left'] + eloc[0] + etpl.shape[1]//2
            ey = self.region['top']  + eloc[1] + etpl.shape[0]//2
            self.move_mouse_smooth(ex, ey)
            pyautogui.press('e')
            print("🟢 Pressed E")

        # 4) Export a single debug_box.png overlaying both detections
        self._export_debug(gray, [(loc, tpl)], (eloc, etpl) if found_e else None)

    def _export_debug(self, gray, tree_hits, e_hit):
        dbg = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        for loc, tpl in tree_hits:
            cv2.rectangle(dbg, loc,
                          (loc[0]+tpl.shape[1], loc[1]+tpl.shape[0]),
                          (0,255,0), 2)
        if e_hit:
            loc, tpl = e_hit
            cv2.rectangle(dbg, loc,
                          (loc[0]+tpl.shape[1], loc[1]+tpl.shape[0]),
                          (0,0,255), 2)
        cv2.imwrite("debug_box.png", dbg)

    def run(self, delay=0.2):
        print("▶️ Bot started. Press ‘q’ to stop.")
        while self.running:
            if keyboard.is_pressed('q'):
                print("🛑 Stopping bot.")
                break
            try:
                self.step()
            except Exception as e:
                print("❌ Error:", e)
            time.sleep(delay + random.random()*0.1)

if __name__ == "__main__":
    # Placeholder paths—update these with your uploaded PNG filenames
    tree_paths = ["./Templates/Screenshot_22.png", "./Templates/Screenshot_23.png", "./Templates/Screenshot_24.png", "./Templates/Screenshot_25.png"]
    e_path     = "./Templates/E.png"

    bot = BotController(tree_paths, e_path)
    bot.run()
