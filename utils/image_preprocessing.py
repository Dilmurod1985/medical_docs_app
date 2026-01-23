# utils/image_preprocessing.py
import cv2
import numpy as np
from PIL import Image

def preprocess_image(image_bytes):
    """Предобработка изображения для OCR"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Не удалось прочитать изображение")

    img = cv2.convertScaleAbs(img, alpha=1.4, beta=30)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.GaussianBlur(thresh, (3, 3), 0)

    return Image.fromarray(thresh)
