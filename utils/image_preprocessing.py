import cv2
import numpy as np
from PIL import Image

def preprocess_for_ocr(image_bytes):
    # Декодируем байты в картинку
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Делаем картинку контрастнее
    img = cv2.convertScaleAbs(img, alpha=1.5, beta=10)
    
    # Переводим в черно-белый формат для EasyOCR
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    return Image.fromarray(thresh)
