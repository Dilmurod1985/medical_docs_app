import re
from datetime import datetime, timedelta

def parse_medical_book_text(full_text):
    text = full_text.lower()
    res = {
        "id": "Не найдено", "fio": "Не найдено", "status": "годен",
        "date": "Не найдено", "next": "Не рассчитано", "num": ""
    }

    # Ищем ИД сотрудника (6 цифр, как на твоем фото 057304)
    id_match = re.search(r'(\d{6})', text)
    if id_match: res["id"] = id_match.group(1)

    # Ищем даты
    dates = re.findall(r'(\d{2}[.\/]\d{2}[.\/]\d{2,4})', text)
    if dates:
        res["date"] = dates[0].replace('/', '.')
        try:
            dt = datetime.strptime(res["date"], "%d.%m.%Y" if len(res["date"]) > 8 else "%d.%m.%y")
            res["next"] = (dt + timedelta(days=182)).strftime("%d.%m.%Y")
         medicine_dt = ""
    
    return res
