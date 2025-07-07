import cv2

# Load screenshot
img = cv2.imread("cropped_screen.png")
if img is None:
    raise ValueError("❌ Could not read the image file. Check the path and filename.")

# Crop the "E" key square from the image (X, Y, Width, Height)
# Coordinates based on your image (tuned visually)
x, y, w, h = 244, 276, 26, 26
template = img[y:y+h, x:x+w]

# Save it
cv2.imwrite("e_icon_template.png", template)
print("Template saved as e_icon_template.png")
