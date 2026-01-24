import cv2
import numpy as np
from PIL import Image

def preprocess_for_ocr(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Перевод в серое
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Улучшение контраста (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Бинаризация (черно-белое)
    _, processed = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return Image.fromarray(processed)
