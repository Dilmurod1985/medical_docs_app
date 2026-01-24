import cv2
import numpy as np
from PIL import Image

def preprocess_for_ocr(image_bytes):
    # Декодируем байты в изображение
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        
    # 1. Увеличение контраста (CLAHE в LAB пространстве)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    enhanced = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
    # 2. Чёрно-белое + Otsu бинаризация
    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
    # 3. Удаление шумов
    denoised = cv2.medianBlur(binary, 3)
        
    # 4. Выравнивание (deskew)
    coords = np.column_stack(np.where(denoised > 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45: angle = -(90 + angle)
        else: angle = -angle
        (h, w) = denoised.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    else:
        deskewed = denoised

    # 5. Кроп на нижние 60%
    h, w = deskewed.shape
    cropped = deskewed[int(h*0.4):, :]
        
    # 6. Увеличение разрешения (fx=2.0)
    upscaled = cv2.resize(cropped, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        
    return Image.fromarray(upscaled)
