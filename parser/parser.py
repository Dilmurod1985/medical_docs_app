import re
from datetime import datetime, timedelta

def parse_medical_book_text(full_text):
    text = " ".join(full_text.split())
    text_low = text.lower()
    
    # Изначально все поля пустые
    res = {
        "id": "", "fio": "", "status": "годен", "date": "", "next": "",
        "seriya": "TK", "num_doc": "", "vidano": "Тиббий кўрик МЧЖ",
        "date_vidano": "", "date_start": "", "date_end": ""
    }

    # 1. ИД сотрудника (6 цифр)
    id_match = re.search(r'(\d{6})', text)
    if id_match: res["id"] = id_match.group(1)

    # 2. ФИО (ищем заглавные буквы)
    names = [w for w in text.split() if w[0].isupper() and len(w) > 3 
             and w.lower() not in ["тиббий", "кўрик", "мчж", "санитария", "тиббиёт"]]
    if len(names) >= 2: res["fio"] = " ".join(names[:3])

    # 3. Номер документа (часто совпадает с ИД или идет отдельно)
    num_match = re.findall(r'(\d{5,6})', text)
    if len(num_match) > 1: res["num_doc"] = num_match[1]

    # 4. Поиск всех дат в тексте
    dates = re.findall(r'(\d{2}[.\s\-/]\d{2}[.\s\-/]\d{2,4})', text)
    if dates:
        clean_dates = [re.sub(r'[\s\-/]', '.', d) for d in dates]
        res["date"] = clean_dates[0] # Первая дата - осмотр
        res["date_vidano"] = clean_dates[0]
        res["date_start"] = clean_dates[0]
        
        try:
            fmt = "%d.%m.%Y" if len(clean_dates[0]) > 8 else "%d.%m.%y"
            dt = datetime.strptime(clean_dates[0], fmt)
            res["next"] = (dt + timedelta(days=182)).strftime("%d.%m.%Y")
            res["date_end"] = res["next"]
        except: pass
            
    return res
