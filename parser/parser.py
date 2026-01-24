import re
from datetime import datetime, timedelta

def parse_medical_book_text(full_text):
    text = " ".join(full_text.split())
    
    # Создаем полный набор полей по твоему образцу
    res = {
        "id": "", "fio": "", "status": "годен", 
        "date_osm": "", "next_osm": "",
        "seriya": "TK", "num_doc": "", "vidano": "Тиббий кўрик МЧЖ",
        "date_vidano": "", "date_start": "", "date_end": ""
    }

    # 1. ИД (6 цифр)
    id_m = re.search(r'(\d{6})', text)
    if id_m: res["id"] = id_m.group(1)

    # 2. ФИО (слова с большой буквы)
    names = [w for w in text.split() if w[0].isupper() and len(w) > 3 
             and w.lower() not in ["тиббий", "кўрик", "мчж", "санитария"]]
    if len(names) >= 2: res["fio"] = " ".join(names[:3])

    # 3. Номера и серии
    # Если на фото есть серия MT или TK, записываем её
    ser_m = re.search(r'\b(MT|TK)\b', text.upper())
    if ser_m: res["seriya"] = ser_m.group(1)
    
    # 4. Даты (берем первую найденную как дату осмотра и выдачи)
    dates = re.findall(r'(\d{2}[.\s\-/]\d{2}[.\s\-/]\d{2,4})', text)
    if dates:
        d = re.sub(r'[\s\-/]', '.', dates[0])
        res["date_osm"] = d
        res["date_vidano"] = d
        res["date_start"] = d
        try:
            dt = datetime.strptime(d, "%d.%m.%Y" if len(d) > 8 else "%d.%m.%y")
            res["next_osm"] = (dt + timedelta(days=182)).strftime("%d.%m.%Y")
            res["date_end"] = res["next_osm"]
        except: pass
            
    return res
