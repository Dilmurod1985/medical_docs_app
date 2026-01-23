import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

class MedicalDocumentParser:
    def __init__(self):
        pass

    def parse(self, ocr_data):
        # Объединяем весь текст в одну строку для поиска
        full_text = " ".join([item['text'] for item in ocr_data])
        
        # 1. Ищем ФИО (ищем слова с заглавной буквы, например "Иванов Иван")
        name_match = re.search(r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)', full_text)
        fio = name_match.group(1) if name_match else "Не найдено"

        # 2. Ищем дату осмотра (формат 23.01.2026 или 23/01/2026)
        date_pattern = r'(\d{2}[.\/]\d{2}[.\/]\d{4})'
        dates = re.findall(date_pattern, full_text)
        
        exam_date_str = dates[0] if dates else None
        next_visit_str = "Не рассчитано"

        if exam_date_str:
            try:
                # Превращаем текст в дату и прибавляем 6 месяцев
                dt = datetime.strptime(exam_date_str.replace('/', '.'), '%d.%m.%Y')
                next_visit_dt = dt + relativedelta(months=6)
                next_visit_str = next_visit_dt.strftime('%d.%m.%
