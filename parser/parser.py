import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

class MedicalDocumentParser:
    def __init__(self):
        pass

    def parse(self, ocr_data):
        # Объединяем весь найденный текст
        full_text = " ".join([item['text'] for item in ocr_data])
        
        # Улучшенный поиск ФИО (ищем 2-3 слова подряд с большой буквы)
        fio_match = re.search(r'([А-ЯЁ][а-яё\-]+\s+[А-ЯЁ][а-яё\-]+(?:\s+[А-ЯЁ][а-яё\-]+)?)', full_text)
        
        # Поиск ИД и Номера (любые группы цифр от 5 до 8 штук)
        digits = re.findall(r'(\d{5,8})', full_text)
        id_emp = digits[0] if len(digits) > 0 else ""
        nomer = digits[1] if len(digits) > 1 else id_emp

        # Поиск дат
        dates = re.findall(r'(\d{2}[.\/]\d{2}[.\/]\d{2,4})', full_text)
        exam_date = dates[0] if len(dates) > 0 else "Не найдено"
        
        next_visit = "Не рассчитано"
        if exam_date != "Не найдено":
            try:
                clean_d = exam_date.replace('/', '.')
                fmt = '%d.%m.%y' if len(clean_d) < 10 else '%d.%m.%Y'
                dt = datetime.strptime(clean_d, fmt)
                # Прибавляем 6 месяцев как в образце
                next_dt = dt + relativedelta(months=6)
                next_visit = next_dt.strftime('%d.%m.%Y')
            except: pass

        return {
            "id": id_emp,
            "fio": fio_match.group(1) if fio_match else "Не найдено",
            "exam_date": exam_date,
            "next_date": next_visit,
            "nomer": nomer
        }
