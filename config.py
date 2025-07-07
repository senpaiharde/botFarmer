# config.py
# config.py
GAME_REGION = {
    "left":   340,
    "top":    260,
    "width":  600,
    "height": 650   # ← big enough to cover your tallest template (636px)
}


THRESHOLD       = 0.75
HARVEST_KEY     = "e"
MIN_DELAY       = 0.1      # seconds
MAX_DELAY       = 0.3
COOLDOWN        = 2.5      # seconds between chops
MARKER_TEMPLATE   = "./Templates/E.png"

# list all your tree templates here
TREE_TEMPLATES = [
    './Templates/Screenshot_22.png',
    './Templates/Screenshot_23.png',
    './Templates/Screenshot_24.png',
    './Templates/Screenshot_25.png',
    # add more as you upload them
]
