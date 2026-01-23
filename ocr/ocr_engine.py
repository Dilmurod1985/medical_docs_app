import easyocr
import numpy as np
from typing import List, Dict, Tuple

class OCREngine:
    def __init__(self, languages=['ru', 'en']):
        """
        Инициализация OCR движка EasyOCR.
        Используем русский и английский для корректной работы.
        """
        self.reader = easyocr.Reader(languages, gpu=False)
        self.languages = languages

    def extract_text(self, image: np.ndarray) -> List[Dict]:
        """
        Извлекает текст из изображения.
        """
        try:
            # Распознаем текст
            results = self.reader.readtext(image)
            
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
        Возвращает только строку распознанного текста.
        """
        results = self.extract_text(image)
        return ' '.join([item['text'] for item in results])

    def extract_high_confidence_text(self, image: np.ndarray, min_confidence: float = 0.5) -> List[Dict]:
        """
        Извлекает текст с фильтрацией по уверенности (от 50% и выше).
        """
        all_results = self.extract_text(image)
        filtered_results = [
            result for result in all_results 
            if result['confidence'] >= min_confidence
        ]
        return filtered_results
