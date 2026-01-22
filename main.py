import os
import sys
from pathlib import Path
from typing import List, Dict

# Добавляем корневую директорию проекта в sys.path
sys.path.append(str(Path(__file__).parent))

from utils.image_preprocessing import preprocess_image
from ocr.ocr_engine import OCREngine
from parser.parser import MedicalDocumentParser
from exporter.exporter import ExcelExporter

class MedicalDocsProcessor:
    def __init__(self):
        """
        Инициализация процессора медицинских документов
        """
        self.ocr_engine = OCREngine()
        self.parser = MedicalDocumentParser()
        self.exporter = ExcelExporter()
        
        # Создаем необходимые директории
        self.create_directories()
    
    def create_directories(self):
        """
        Создает необходимые директории для работы
        """
        directories = [
            'photos',
            'processed_images',
            'output'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"Директория {directory} готова")
    
    def get_image_files(self, photos_dir: str = 'photos') -> List[str]:
        """
        Получает список всех изображений из папки photos
        
        Args:
            photos_dir (str): Папка с фотографиями
            
        Returns:
            List[str]: Список путей к изображениям
        """
        supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        image_files = []
        
        if not os.path.exists(photos_dir):
            print(f"Предупреждение: Папка {photos_dir} не найдена")
            return image_files
        
        for filename in os.listdir(photos_dir):
            file_path = os.path.join(photos_dir, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename.lower())
                if ext in supported_extensions:
                    image_files.append(file_path)
        
        print(f"Найдено изображений: {len(image_files)}")
        return image_files
    
    def process_single_image(self, image_path: str) -> Dict:
        """
        Обрабатывает одно изображение
        
        Args:
            image_path (str): Путь к изображению
            
        Returns:
            Dict: Результаты обработки
        """
        try:
            print(f"Обработка изображения: {image_path}")
            
            # 1. Предобработка изображения
            processed_image = preprocess_image(image_path)
            
            # Сохраняем обработанное изображение для отладки
            filename = os.path.basename(image_path)
            processed_filename = f"processed_{filename}"
            processed_path = os.path.join('processed_images', processed_filename)
            
            from utils.image_preprocessing import save_processed_image
            save_processed_image(processed_image, processed_path)
            
            # 2. OCR распознавание
            extracted_text = self.ocr_engine.extract_text_only(processed_image)
            print(f"Извлеченный текст: {extracted_text[:100]}...")
            
            # 3. Парсинг данных
            parsed_data = self.parser.parse_medical_document(extracted_text)
            patient_info = self.parser.extract_patient_info(extracted_text)
            
            # 4. Формирование результата
            result = {
                'filename': filename,
                'original_path': image_path,
                'processed_path': processed_path,
                'extracted_text': extracted_text,
                'parsed_data': parsed_data,
                'patient_info': patient_info,
                'success': True
            }
            
            # Выводим сводный отчет
            summary_report = self.parser.get_summary_report(parsed_data)
            print(summary_report)
            
            return result
            
        except Exception as e:
            print(f"Ошибка при обработке {image_path}: {e}")
            return {
                'filename': os.path.basename(image_path),
                'original_path': image_path,
                'error': str(e),
                'success': False
            }
    
    def process_all_images(self) -> List[Dict]:
        """
        Обрабатывает все изображения из папки photos
        
        Returns:
            List[Dict]: Результаты обработки всех изображений
        """
        # Получаем список изображений
        image_files = self.get_image_files()
        
        if not image_files:
            print("В папке photos нет изображений для обработки")
            return []
        
        # Обрабатываем каждое изображение
        all_results = []
        
        for image_path in image_files:
            result = self.process_single_image(image_path)
            all_results.append(result)
            print("-" * 50)
        
        return all_results
    
    def export_results(self, results: List[Dict], output_filename: str = None) -> bool:
        """
        Экспортирует результаты в Excel файл
        
        Args:
            results (List[Dict]): Результаты обработки
            output_filename (str): Имя выходного файла
            
        Returns:
            bool: True если экспорт успешен
        """
        if not results:
            print("Нет результатов для экспорта")
            return False
        
        if output_filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"medical_results_{timestamp}.xlsx"
        
        output_path = os.path.join('output', output_filename)
        
        # Экспортируем медицинские данные
        success = self.exporter.export_medical_documents(results, output_path)
        
        if success:
            # Создаем также сводный отчет
            summary_filename = f"summary_{output_filename}"
            summary_path = os.path.join('output', summary_filename)
            self.exporter.create_summary_report(results, summary_path)
            
            print(f"Результаты сохранены в:")
            print(f"  - Основной файл: {output_path}")
            print(f"  - Сводный отчет: {summary_path}")
        
        return success
    
    def run_full_pipeline(self):
        """
        Запускает полный пайплайн обработки
        """
        print("=" * 60)
        print("ЗАПУСК OCR-СИСТЕМЫ МЕДИЦИНСКИХ ДОКУМЕНТОВ")
        print("=" * 60)
        
        try:
            # 1. Обрабатываем все изображения
            print("\n1. Обработка изображений...")
            results = self.process_all_images()
            
            if not results:
                print("Нет изображений для обработки")
                return
            
            # 2. Экспортируем результаты
            print("\n2. Экспорт результатов...")
            export_success = self.export_results(results)
            
            # 3. Выводим итоговую статистику
            print("\n3. Итоговая статистика:")
            successful = sum(1 for r in results if r.get('success', False))
            total = len(results)
            
            print(f"  - Всего обработано: {total}")
            print(f"  - Успешно: {successful}")
            print(f"  - С ошибками: {total - successful}")
            
            if export_success:
                print("  - Экспорт: Успешно")
            else:
                print("  - Экспорт: Ошибка")
            
            print("\n" + "=" * 60)
            print("РАБОТА ЗАВЕРШЕНА")
            print("=" * 60)
            
        except Exception as e:
            print(f"Критическая ошибка в пайплайне: {e}")

def main():
    """
    Главная функция
    """
    processor = MedicalDocsProcessor()
    processor.run_full_pipeline()

if __name__ == "__main__":
    main()