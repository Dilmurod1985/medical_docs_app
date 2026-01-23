import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

class MedicalDocumentParser:
    def __init__(self):
        pass

    def parse(self, ocr_data):
        # Объединяем текст для поиска
        full_text = " ".join([item['text'] for item in ocr_data])
        
        # Поиск ФИО, ID и дат
        fio_match = re.search(r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)', full_text)
        id_match = re.search(r'(\d{6})', full_text)
        nomer_match = re.search(r'(\d{5,8})', full_text)
        dates = re.findall(r'(\d{2}[.\/]\d{2}[.\/]\d{2,4})', full_text)

        exam_date = dates[0] if len(dates) > 0 else "Не найдено"
        next_date = "Не рассчитано"
        
        if exam_date != "Не найдено":
            try:
                # Очистка и расчет +6 месяцев
                dt = datetime.strptime(exam_date.replace('/', '.'), '%d.%m.%y' if len(exam_date) < 10 else '%d.%m.%Y')
                next_date = (dt + relativedelta(months=6)).strftime('%d.%m.%y')
            except: pass

        # Возвращаем данные для всех 11 колонок
        return {
            "id": id_match.group(1) if id_match else "",
            "fio": fio_match.group(1) if fio_match else "Не найдено",
            "status": "годен",
            "date": exam_date,
            "next": next_date,
            "seria": "ТК",
            "nomer": nomer_match.group(1) if nomer_match else "",
            "org": "Тиббий кўрик МЧЖ",
            "issue": exam_date
        }
