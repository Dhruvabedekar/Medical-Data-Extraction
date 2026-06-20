import cv2
import pytesseract
import re
import os

# ==============================
# 🔹 TESSERACT PATH (Windows)
# ==============================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ==============================
# 🔹 IMAGE PATH
# ==============================
image_path = "md.jpg"

if not os.path.exists(image_path):
    print("Image not found")
    exit()

# ==============================
# 🔹 LOAD IMAGE
# ==============================
img = cv2.imread(image_path)

if img is None:
    print("Failed to load image")
    exit()

# ==============================
# 🔹 PREPROCESSING (STRONG)
# ==============================

# Resize
img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

# Grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Denoise
gray = cv2.bilateralFilter(gray, 9, 75, 75)

# Adaptive Threshold
thresh = cv2.adaptiveThreshold(
    gray, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    11, 2
)

# ==============================
# 🔹 OCR CONFIG (IMPORTANT)
# ==============================
custom_config = r'--oem 3 --psm 4 -l eng'

text = pytesseract.image_to_string(thresh, config=custom_config)

print("\n================ RAW TEXT ================\n")
print(text)

# ==============================
# 🔹 CLEAN TEXT
# ==============================
clean_text = re.sub(r'[^A-Za-z0-9@:/\n .-]', '', text)
clean_text = re.sub(r'\s+', ' ', clean_text)

# ==============================
# 🔹 NORMALIZE OCR ERRORS
# ==============================
def normalize_text(text):
    corrections = {
        "Ratient": "Patient",
        "Batient": "Patient",
        "Patiert": "Patient",
        "Bhone": "Phone",
        "Phane": "Phone",
        "Emall": "Email",
        "Emai": "Email",
        "Jimohan": "mohan",
        "imohan": "mohan",
        "gmaileor": "gmail.com",
        "gimalr": "gmail",
        "De.": "Dr.",
        "MOKESH": "Mokesh",
        "MISHRA": "Mishra"
    }

    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)

    return text

clean_text = normalize_text(clean_text)

print("\n================ CLEAN TEXT ================\n")
print(clean_text)

# ==============================
# 🔹 EXTRACTION
# ==============================

# Name
name = re.search(r"Patient\s*Name\s*[:=]?\s*([A-Za-z]+)", clean_text, re.I)

# Age
age = re.search(r"Age.*?(\d{1,3})", clean_text, re.I)

# Date
date = re.search(r"\d{2}/\d{2}/\d{4}", clean_text)

# Phone (handle mixed chars)
phone = re.search(r"(\d[\dA-Za-z]{8,}\d)", clean_text)

# Email
email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", clean_text)

# Doctor
doctor = re.search(r"Dr\.?\s*([A-Za-z ]+)", clean_text)

# Address
address = re.search(r"Shop Number.*400703", clean_text)

# ==============================
# 🔹 CLEAN PHONE
# ==============================
def clean_phone(match):
    if not match:
        return None
    return re.sub(r'\D', '', match.group(1))

phone_clean = clean_phone(phone)

# ==============================
# 🔹 FINAL OUTPUT
# ==============================
print("\n================ FINAL OUTPUT ================\n")

print("Patient Name :", name.group(1) if name else "Not Found")
print("Age          :", age.group(1) if age else "Not Found")
print("Date         :", date.group(0) if date else "Not Found")
print("Phone        :", phone_clean if phone_clean else "Not Found")
print("Email        :", email.group(0) if email else "Not Found")
print("Doctor Name  :", doctor.group(1) if doctor else "Not Found")
print("Address      :", address.group(0) if address else "Not Found")