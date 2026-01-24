import re
from datetime import datetime, timedelta

def parse_medical_book_text(full_text):
    text = " ".join(full_text.split())
    # Убираем лишние символы, оставляем цифры и буквы для поиска серии
    text_clean = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ.\s\-]', '', text)
    
    res = {
        "id": "", "fio": "", "status": "годен", "date_osm": "", "next_osm": "",
        "seriya": "TK", "num_doc": "", "vidano": "Тиббий кўрик МЧЖ",
        "date_vidano": "", "date_start": "", "date_end": ""
    }

    # 1. Ищем серию (MT или TK)
    ser_match = re.search(r'\b(MT|TK|МТ|ТК)\b', text_clean.upper())
    if ser_match:
        res["seriya"] = ser_match.group(1).replace('МТ', 'MT').replace('ТК', 'TK')

    # 2. Ищем ВСЕ группы цифр (от 5 до 8 знаков)
    all_numbers = re.findall(r'\b\d{5,8}\b', text_clean)
    
    if len(all_numbers) >= 2:
        # Обычно номер документа (7 цифр) идет раньше ИД (6 цифр)
        res["num_doc"] = all_numbers[0] 
        res["id"] = all_numbers[-1]
    elif len(all_numbers) == 1:
        res["id"] = all_numbers[0]

    # 3. Ищем даты
    dates = re.findall(r'(\d{2}[. ]\d{2}[. ]\d{2,4})', text_clean)
    if dates:
        d = dates[0].replace(' ', '.')
        res["date_osm"] = res["date_vidano"] = res["date_start"] = d
        try:
            dt = datetime.strptime(d, "%d.%m.%Y" if len(d) > 8 else "%d.%m.%y")
            next_d = (dt + timedelta(days=182)).strftime("%d.%m.%Y")
            res["next_osm"] = res["date_end"] = next_d
        except: pass

    # 4. Попытка вытащить ФИО (слова с большой буквы)
    words = text.split()
    names = [w for w in words if len(w) > 3 and w[0].isupper() and w.lower() not in ["тиббий", "мчж", "серия"]]
    if len(names) >= 2:
        res["fio"] = " ".join(names[:3])
            
    return res
