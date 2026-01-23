import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

class MedicalDocumentParser:
    def __init__(self):
        pass

    def parse(self, ocr_data):
        # Объединяем весь найденный текст в одну строку
        full_text = " ".join([item['text'] for item in ocr_data])
        
        # 1. Поиск ФИО (ищем слова с заглавной буквы, исключая служебные слова)
        fio_match = re.search(r'([А-ЯЁ][а-яё\-]+\s+[А-ЯЁ][а-яё\-]+(?:\s+[А-ЯЁ][а-яё\-]+)?)', full_text)
        
        # 2. Поиск ИД и Номера (группы по 5-6 цифр)
        numbers = re.findall(r'(\d{5,6})', full_text)
        id_emp = numbers[0] if len(numbers) > 0 else ""
        doc_num = numbers[1] if len(numbers) > 1 else id_emp

        # 3. Поиск всех дат (форматы 23.01.2026, 23/01/26 и т.д.)
        dates = re.findall(r'(\d{2}[.\/]\d{2}[.\/]\d{2,4})', full_text)
        
        exam_date = dates[0] if len(dates) > 0 else "Не найдено"
        next_visit = "Не рассчитано"

        if exam_date != "Не найдено":
            try:
                # Чистим дату и считаем +6 месяцев
                clean_date = exam_date.replace('/', '.')
                fmt = '%d.%m.%y' if len(clean_date) < 10 else '%d.%m.%Y'
                dt = datetime.strptime(clean_date, fmt)
                next_visit = (dt + relativedelta(months=6)).strftime('%d.%m.%Y')
            except:
                pass

        return {
            "id": id_emp,
            "fio": fio_match.group(1) if fio_match else "Не найдено",
            "exam_date": exam_date,
            "next_date": next_visit,
            "doc_num": doc_num
        }
