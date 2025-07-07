from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img = Image.open("cropped_screen.png")

# Convert to grayscale
img = img.convert("L")

# Sharpen
img = img.filter(ImageFilter.SHARPEN)

# Enhance contrast heavily
img = ImageEnhance.Contrast(img).enhance(5.0)

# Binarize (convert to black & white)
threshold = 160
img = img.point(lambda p: 255 if p > threshold else 0)

img.save("preprocessed.png")

# OCR
text = pytesseract.image_to_string(img)
print("OCR Detected:", text)
