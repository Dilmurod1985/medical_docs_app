import re
from datetime import datetime, timedelta

def parse_medical_book_text(text):
    # Очищаем текст от лишних пробелов для лучшего поиска
    text_clean = " ".join(text.split())
    
    result = {
        "id": "Не найдено", "fio": "Не найдено", "status": "годен",
        "date_osm": "Не найдено", "next_osm": "Не рассчитано",
        "seriya": "Не найдено", "num_doc": "Не найдено",
        "vidano": "Тиббий кўрик МЧЖ", "date_vidano": "Не найдено"
    }

    # 1. Серия (Seriyasi / Серия)
    series_match = re.search(r'(?:seriyasi|серия|seriya)\s*([A-Z0-9]{2,4})', text_clean, re.I)
    if series_match:
        result["seriya"] = series_match.group(1).replace(" ", "")

    # 2. Номер (Raqami / Номер)
    number_match = re.search(r'(?:raqami|номер|number)\s*(\d{5,8})', text_clean, re.I)
    if number_match:
        result["num_doc"] = number_match.group(1)

    # 3. Даты (Выдача / Осмотр)
    # Ищем даты в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ
    dates = re.findall(r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})', text_clean)
    if dates:
        clean_dates = [d.replace('/', '.') for d in dates]
        result["date_osm"] = clean_dates[0]
        result["date_vidano"] = clean_dates[0]
        try:
            dt = datetime.strptime(clean_dates[0], "%d.%m.%Y" if len(clean_dates[0]) > 8 else "%d.%m.%y")
            result["next_osm"] = (dt + timedelta(days=182)).strftime("%d.%m.%Y")
        except: pass

    # 4. ФИО (Попытка найти слова с Большой буквы)
    names = [w for w in text_clean.split() if len(w) > 4 and w[0].isupper() and w.lower() not in ["seriyasi", "raqami", "tibbiyot", "kitobchasi"]]
    if len(names) >= 2:
        result["fio"] = " ".join(names[:3])

    return result
