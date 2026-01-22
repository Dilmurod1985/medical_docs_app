import pandas as pd
from typing import List, Dict, Any
import os
from datetime import datetime

class ExcelExporter:
    def __init__(self):
        """
        Инициализация экспортера в Excel
        """
    
    def export_to_excel(self, data: List[Dict], output_path: str, sheet_name: str = 'Medical_Data') -> bool:
        """
        Экспортирует список словарей в Excel файл
        
        Args:
            data (List[Dict]): Список словарей с данными
            output_path (str): Путь для сохранения Excel файла
            sheet_name (str): Название листа в Excel файле
            
        Returns:
            bool: True если экспорт успешен, False в случае ошибки
        """
        try:
            if not data:
                print("Предупреждение: Нет данных для экспорта")
                return False
            
            # Создаем DataFrame из списка словарей
            df = pd.DataFrame(data)
            
            # Создаем директорию если она не существует
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Экспортируем в Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Получаем рабочую книгу и лист для форматирования
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                
                # Автоматическая настройка ширины колонок
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # Ограничиваем максимальную ширину
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"Данные успешно экспортированы в {output_path}")
            return True
            
        except Exception as e:
            print(f"Ошибка при экспорте в Excel: {e}")
            return False
    
    def export_medical_documents(self, medical_data: List[Dict], output_path: str) -> bool:
        """
        Экспортирует данные медицинских документов в специальном формате
        
        Args:
            medical_data (List[Dict]): Список данных медицинских документов
            output_path (str): Путь для сохранения Excel файла
            
        Returns:
            bool: True если экспорт успешен, False в случае ошибки
        """
        try:
            # Подготавливаем данные для экспорта
            export_data = []
            
            for i, doc_data in enumerate(medical_data, 1):
                # Базовая информация о документе
                base_info = {
                    'document_id': i,
                    'filename': doc_data.get('filename', f'document_{i}'),
                    'processing_date': datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                }
                
                # Информация о пациенте
                patient_info = doc_data.get('patient_info', {})
                patient_data = {
                    'patient_name': patient_info.get('name', ''),
                    'birth_date': patient_info.get('birth_date', ''),
                    'age': patient_info.get('age', '')
                }
                
                # Даты осмотров
                parsed_data = doc_data.get('parsed_data', {})
                exam_dates = parsed_data.get('exam_dates', [])
                next_exam_dates = parsed_data.get('next_exam_dates', [])
                
                # Создаем записи для каждой даты осмотра
                if exam_dates:
                    for j, exam_date in enumerate(exam_dates):
                        row_data = {
                            **base_info,
                            **patient_data,
                            'exam_date': exam_date,
                            'next_exam_date': next_exam_dates[j] if j < len(next_exam_dates) else '',
                            'exam_number': j + 1
                        }
                        export_data.append(row_data)
                else:
                    # Если дат нет, все равно создаем запись
                    row_data = {
                        **base_info,
                        **patient_data,
                        'exam_date': '',
                        'next_exam_date': '',
                        'exam_number': 0
                    }
                    export_data.append(row_data)
            
            # Экспортируем подготовленные данные
            return self.export_to_excel(export_data, output_path, 'Medical_Examinations')
            
        except Exception as e:
            print(f"Ошибка при подготовке медицинских данных: {e}")
            return False
    
    def create_summary_report(self, medical_data: List[Dict], output_path: str) -> bool:
        """
        Создает сводный отчет по всем документам
        
        Args:
            medical_data (List[Dict]): Список данных медицинских документов
            output_path (str): Путь для сохранения отчета
            
        Returns:
            bool: True если создание успешно, False в случае ошибки
        """
        try:
            summary_data = []
            
            total_documents = len(medical_data)
            total_exams = 0
            documents_with_dates = 0
            
            for doc_data in medical_data:
                parsed_data = doc_data.get('parsed_data', {})
                exam_dates = parsed_data.get('exam_dates', [])
                
                doc_summary = {
                    'filename': doc_data.get('filename', ''),
                    'total_exams': len(exam_dates),
                    'has_dates': len(exam_dates) > 0,
                    'first_exam': exam_dates[0] if exam_dates else '',
                    'last_exam': exam_dates[-1] if exam_dates else ''
                }
                
                summary_data.append(doc_summary)
                total_exams += len(exam_dates)
                if len(exam_dates) > 0:
                    documents_with_dates += 1
            
            # Добавляем итоговую строку
            summary_data.append({
                'filename': 'ИТОГО',
                'total_exams': total_exams,
                'has_documents': total_documents,
                'documents_with_dates': documents_with_dates,
                'first_exam': '',
                'last_exam': ''
            })
            
            return self.export_to_excel(summary_data, output_path, 'Summary_Report')
            
        except Exception as e:
            print(f"Ошибка при создании сводного отчета: {e}")
            return False