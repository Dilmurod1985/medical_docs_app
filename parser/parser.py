import re
from datetime import datetime, timedelta

def parse_medical_book_text(text):
    text = text.lower().replace("ё", "е").replace("\n", " ").strip()
    
    result = {
        "id": "Не найдено", "fio": "Впишите вручную", "status": "Не определён",
        "date_osm": "Не найдено", "next_osm": "Не рассчитано",
        "seriya": "Не найдено", "num_doc": "Не найдено", "date_vidano": "Не найдено"
    }

    # 1. ФИО (Твои шаблоны)
    fio_match = re.search(r'(?:ism|lavozimi|famil|familiya|otasi|full name)\s*[: ]*([а-яa-z\s]{5,})', text, re.I)
    if fio_match:
        result["fio"] = fio_match.group(1).title().strip()

    # 2. Серия (MT или TK)
    series_match = re.search(r'(?:seriyasi|серия|seriya|mt|tk)\s*([a-z]{1,2})', text, re.I)
    if series_match:
        result["seriya"] = series_match.group(1).upper()

    # 3. Номер (5-6 цифр после raqami)
    number_match = re.search(r'(?:raqami|номер|number)\s*(\d{5,6})', text, re.I)
    if number_match:
        result["num_doc"] = number_match.group(1)
        result["id"] = number_match.group(1)

    # 4. Даты и расчет +6 месяцев (по твоей инструкции)
    date_match = re.search(r'(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})', text)
    if date_match:
        d_str = date_match.group(1).replace('/', '.').replace('-', '.')
        result["date_osm"] = result["date_vidano"] = d_str
        try:
            # Парсим дату и прибавляем 182 дня (полгода)
            date_obj = datetime.strptime(d_str, "%d.%m.%Y" if len(d_str) > 8 else "%d.%m.%y")
            next_date = date_obj + timedelta(days=182)
            result["next_osm"] = next_date.strftime("%d.%m.%Y")
        except: pass

    # 5. Статус
    if any(word in text for word in ["goden", "годен", "yil", "year"]):
        result["status"] = "Годен"

    return result
