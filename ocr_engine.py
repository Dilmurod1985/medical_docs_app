import easyocr
import numpy as np
from typing import List, Dict, Tuple

class OCREngine:
    def __init__(self, languages=['uz', 'ru']):
        """
        Инициализация OCR движка EasyOCR
        
        Args:
            languages (list): Список языков для распознавания
        """
        self.reader = easyocr.Reader(languages, gpu=False)
        self.languages = languages
    
    def extract_text(self, image: np.ndarray) -> List[Dict]:
        """
        Извлекает текст из изображения
        
        Args:
            image (numpy.ndarray): Обработанное изображение
            
        Returns:
            List[Dict]: Список словарей с результатами распознавания
        """
        try:
            # Распознаем текст с помощью EasyOCR
            results = self.reader.readtext(image)
            
            # Форматируем результаты
            extracted_data = []
            for (bbox, text, confidence) in results:
                extracted_data.append({
                    'text': text.strip(),
                    'confidence': float(confidence),
                    'bbox': bbox
                })
            
            return extracted_data
            
        except Exception as e:
            print(f"Ошибка при распознавании текста: {e}")
            return []
    
    def extract_text_only(self, image: np.ndarray) -> str:
        """
        Извлекает только текст без дополнительной информации
        
        Args:
            image (numpy.ndarray): Обработанное изображение
            
        Returns:
            str: Распознанный текст
        """
        results = self.extract_text(image)
        return ' '.join([item['text'] for item in results])
    
    def extract_high_confidence_text(self, image: np.ndarray, min_confidence: float = 0.5) -> List[Dict]:
        """
        Извлекает текст с минимальным порогом уверенности
        
        Args:
            image (numpy.ndarray): Обработанное изображение
            min_confidence (float): Минимальный порог уверенности
            
        Returns:
            List[Dict]: Отфильтрованные результаты распознавания
        """
        all_results = self.extract_text(image)
        
        # Фильтруем по уверенности
        filtered_results = [
            result for result in all_results 
            if result['confidence'] >= min_confidence
        ]
        
        return filtered_results