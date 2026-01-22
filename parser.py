import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class MedicalDocumentParser:
    def __init__(self):
        """
        Инициализация парсера медицинских документов
        """
        # Регулярное выражение для поиска дат в формате DD.MM.YYYY
        self.date_pattern = re.compile(r'\b(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}\b')
        
        # Дополнительные паттерны для поиска контекста дат
        self.exam_context_patterns = [
            r'(?:осмотр|обследование|проверка|визит).*?(\d{2}\.\d{2}\.\d{4})',
            r'(\d{2}\.\d{2}\.\d{4}).*?(?:осмотр|обследование|проверка|визит)',
        ]
    
    def find_dates(self, text: str) -> List[str]:
        """
        Находит все даты в тексте в формате DD.MM.YYYY
        
        Args:
            text (str): Текст для поиска дат
            
        Returns:
            List[str]: Список найденных дат
        """
        dates = self.date_pattern.findall(text)
        # Преобразуем кортежи в строки (findall с группами возвращает кортежи)
        if dates and isinstance(dates[0], tuple):
            dates = ['.'.join(date_tuple) for date_tuple in dates]
        return dates
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Парсит строку с датой в объект datetime
        
        Args:
            date_str (str): Строка с датой в формате DD.MM.YYYY
            
        Returns:
            Optional[datetime]: Объект datetime или None в случае ошибки
        """
        try:
            return datetime.strptime(date_str, '%d.%m.%Y')
        except ValueError:
            return None
    
    def calculate_next_exam_date(self, exam_date: datetime) -> str:
        """
        Рассчитывает дату следующего осмотра (+6 месяцев)
        
        Args:
            exam_date (datetime): Дата текущего осмотра
            
        Returns:
            str: Дата следующего осмотра в формате DD.MM.YYYY
        """
        next_exam_date = exam_date + timedelta(days=180)  # Приблизительно 6 месяцев
        return next_exam_date.strftime('%d.%m.%Y')
    
    def parse_medical_document(self, text: str) -> Dict:
        """
        Парсит медицинский документ и извлекает даты осмотров
        
        Args:
            text (str): Текст документа
            
        Returns:
            Dict: Словарь с извлеченной информацией
        """
        # Находим все даты в тексте
        found_dates = self.find_dates(text)
        
        parsed_data = {
            'original_text': text,
            'found_dates': found_dates,
            'exam_dates': [],
            'next_exam_dates': []
        }
        
        # Обрабатываем каждую найденную дату
        for date_str in found_dates:
            parsed_date = self.parse_date(date_str)
            if parsed_date:
                next_exam_date = self.calculate_next_exam_date(parsed_date)
                
                parsed_data['exam_dates'].append(date_str)
                parsed_data['next_exam_dates'].append(next_exam_date)
        
        return parsed_data
    
    def extract_patient_info(self, text: str) -> Dict:
        """
        Извлекает базовую информацию о пациенте (имя, возраст и т.д.)
        
        Args:
            text (str): Текст документа
            
        Returns:
            Dict: Информация о пациенте
        """
        patient_info = {
            'name': None,
            'birth_date': None,
            'age': None
        }
        
        # Поиск ФИО (простой паттерн для заглавных слов)
        name_pattern = re.compile(r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?\b')
        names = name_pattern.findall(text)
        if names:
            patient_info['name'] = names[0]
        
        # Поиск даты рождения
        birth_dates = self.find_dates(text)
        if birth_dates:
            # Предполагаем, что первая дата может быть датой рождения
            # (это упрощение, в реальной системе нужна более сложная логика)
            birth_date = self.parse_date(birth_dates[0])
            if birth_date:
                patient_info['birth_date'] = birth_dates[0]
                # Расчет возраста (упрощенный)
                today = datetime.now()
                age = today.year - birth_date.year
                if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                    age -= 1
                patient_info['age'] = age
        
        return patient_info
    
    def get_summary_report(self, parsed_data: Dict) -> str:
        """
        Формирует сводный отчет по результатам парсинга
        
        Args:
            parsed_data (Dict): Результаты парсинга
            
        Returns:
            str: Текстовый отчет
        """
        report = "=== ОТЧЕТ ПАРСИНГА МЕДИЦИНСКОГО ДОКУМЕНТА ===\n\n"
        
        if parsed_data['found_dates']:
            report += f"Найдено дат: {len(parsed_data['found_dates'])}\n"
            for i, date in enumerate(parsed_data['exam_dates']):
                next_date = parsed_data['next_exam_dates'][i]
                report += f"  - Осмотр: {date} → Следующий осмотр: {next_date}\n"
        else:
            report += "Даты не найдены\n"
        
        return report