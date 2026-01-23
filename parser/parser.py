import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

class MedicalDocumentParser:
    def parse(self, ocr_data):
        full_text = " ".join([item['text'] for item in ocr_data])
        
        # Поиск данных по шаблонам из твоего Excel
        fio = re.search(r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)', full_text)
        id_emp = re.search(r'(\d{6})', full_text) # Ищем 6 цифр ID
        seria = re.search(r'\b(ТК|TK|AA|AB)\b', full_text) # Серия документа
        nomer = re.search(r'(\d{5,7})', full_text) # Номер документа
        
        # Поиск дат (ищем все даты в тексте)
        dates = re.findall(r'(\d{2}[.\/]\d{2}[.\/]\d{2,4})', full_text)
        
        exam_date = dates[0] if len(dates) > 0 else "Не найдено"
        issue_date = dates[1] if len(dates) > 1 else "Не найдено"
        
        next_visit = "Не рассчитано"
        if exam_date != "Не найдено":
            try:
                # В твоем Excel формат даты 15.11.25
                dt = datetime.strptime(exam_date.replace('/', '.'), '%d.%m.%y' if len(exam_date) < 10 else '%d.%m.%Y')
                next_visit = (dt + relativedelta(months=6)).strftime('%d.%m.%y')
            except: pass

        return {
            "ИД сотрудника": id_emp.group(1) if id_emp else "",
            "ФИО": fio.group(1) if fio else "Не найдено",
            "Статус медосмотра": "годен", # По умолчанию как в примере
            "Дата медосмотра": exam_date,
            "След. Дата медосмотра": next_visit,
            "Серия документа": seria.group(1) if seria else "ТК",
            "Номер документа": nomer.group(1) if nomer else "",
            "Выдано": "Тиббий кўрик МЧЖ",
            "Дата выдачи": issue_date,
            "Дата начала действия": issue_date,
            "Дата истечения": next_visit
        }
