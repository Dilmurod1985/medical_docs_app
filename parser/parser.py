import re
from datetime import datetime, timedelta

def parse_medical_book_text(full_text):
    text = full_text.lower()
    res = {
        "id": "Не найдено", 
        "fio": "Не найдено", 
        "status": "годен",
        "date": "Не найдено", 
        "next": "Не рассчитано"
    }

    # Ищем ИД (6 цифр)
    id_match = re.search(r'(\d{6})', text)
    if id_match: 
        res["id"] = id_match.group(1)

    # Ищем ФИО (Слова с большой буквы)
    fio_match = re.search(r'([А-ЯЁ][а-яё\-]+\s+[А-ЯЁ][а-яё\-]+(?:\s+[А-ЯЁ][а-яё\-]+)?)', full_text)
    if fio_match:
        res["fio"] = fio_match.group(1)

    # Ищем дату и считаем +6 месяцев
    dates = re.findall(r'(\d{2}[.\/]\d{2}[.\/]\d{2,4})', text)
    if dates:
        d_str = dates[0].replace('/', '.')
        res["date"] = d_str
        try:
            fmt = "%d.%m.%Y" if len(d_str) > 8 else "%d.%m.%y"
            dt = datetime.strptime(d_str, fmt)
            res["next"] = (dt + timedelta(days=182)).strftime("%d.%m.%Y")
        except: 
            pass
    
    return res
