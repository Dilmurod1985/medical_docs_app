import cv2
import numpy as np
from PIL import Image
import io

def preprocess_for_ocr(image_bytes):
    # Превращаем байты в картинку OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 1. Делаем серой
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Убираем шум и делаем текст максимально черным на белом фоне
    # Это поможет прочитать ИД и даты даже в тени
    processed = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Возвращаем как PIL Image
    return Image.fromarray(processed)
