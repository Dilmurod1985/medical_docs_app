import cv2
import numpy as np
from PIL import Image
import io

def preprocess_for_ocr(image_bytes):
    """
    Предобработка изображения для лучшего распознавания OCR.
    Принимает байты из uploaded_file.getvalue()
    """
    # Конвертируем байты в numpy-массив
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Не удалось прочитать изображение")

    # 1. Увеличиваем контраст и яркость
    img = cv2.convertScaleAbs(img, alpha=1.4, beta=30)

    # 2. В серый + удаление шума
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)

    # 3. Адаптивный порог — лучший для печатей и почерка
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # 4. Лёгкое размытие для сглаживания
    thresh = cv2.GaussianBlur(thresh, (3, 3), 0)

    # Возвращаем PIL Image (EasyOCR любит PIL)
    return Image.fromarray(thresh)
