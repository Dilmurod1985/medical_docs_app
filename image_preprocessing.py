import cv2
import numpy as np
from PIL import Image

def preprocess_image(image_path):
    """
    Применяет адаптивный порог для очистки фото от теней
    
    Args:
        image_path (str): Путь к изображению
        
    Returns:
        numpy.ndarray: Обработанное изображение
    """
    # Загружаем изображение
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Не удалось загрузить изображение: {image_path}")
    
    # Конвертируем в градации серого
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Применяем адаптивный порог для удаления теней
    # Параметры: blockSize=11 (размер окрестности), C=2 (константа вычитания)
    adaptive_thresh = cv2.adaptiveThreshold(
        gray, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 
        2
    )
    
    # Дополнительная обработка для улучшения качества
    # Уменьшение шума
    denoised = cv2.medianBlur(adaptive_thresh, 3)
    
    # Морфологические операции для улучшения контуров символов
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
    
    return processed

def save_processed_image(processed_img, output_path):
    """
    Сохраняет обработанное изображение
    
    Args:
        processed_img (numpy.ndarray): Обработанное изображение
        output_path (str): Путь для сохранения
    """
    cv2.imwrite(output_path, processed_img)