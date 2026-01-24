import re
from datetime import datetime, timedelta

def parse_medical_book_text(text):
    # Очищаем текст для поиска
    text_clean = " ".join(text.split())
    
    result = {
        "id": "Не найдено", 
        "fio": "Впишите вручную", 
        "status": "годен",
        "date_osm": "Не найдено", 
        "next_osm": "Не рассчитано",
        "seriya": "Не найдено", 
        "num_doc": "Не найдено",
        "vidano": "Тиббий кўрик МЧЖ",
        "date_vidano": "Не найдено",
        "date_start": "Не найдено",
        "date_end": "Не рассчитано"
    }

    # 1. Серия и Номер (Твоя логика)
    # Ищем SERIYASI -> MT или TK
    series_match = re.search(r'(?:seriyasi|серия|seriya)\s*([A-Z]{2})', text_clean, re.I)
    if series_match:
        result["seriya"] = series_match.group(1).upper()
    
    # Ищем RAQAMI -> 057304
    number_match = re.search(r'(?:raqami|номер|number)\s*(\d{5,7})', text_clean, re.I)
    if number_match:
        result["num_doc"] = number_match.group(1)
        result["id"] = number_match.group(1) # Используем как ИД для твоей таблицы

    # 2. Даты (Выдача / Осмотр)
    # Ищем даты типа 19.10.2024
    dates = re.findall(r'(\d{2}[./]\d{2}[./]\d{2,4})', text_clean)
    if dates:
        d = dates[0].replace('/', '.')
        result["date_osm"] = result["date_vidano"] = result["date_start"] = d
        try:
            dt = datetime.strptime(d, "%d.%m.%Y" if len(d) > 8 else "%d.%m.%y")
            next_d = (dt + timedelta(days=182)).strftime("%d.%m.%Y")
            result["next_osm"] = result["date_end"] = next_d
        except: pass

    return result
