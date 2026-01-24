import re
from datetime import datetime, timedelta

def parse_medical_book_text(full_text):
    text = " ".join(full_text.split())
    res = {
        "id": "", "fio": "", "status": "годен", "date_osm": "", "next_osm": "",
        "seriya": "TK", "num_doc": "", "vidano": "Тиббий кўрик МЧЖ",
        "date_vidano": "", "date_start": "", "date_end": ""
    }

    # Ищем все группы цифр из 5-6 знаков
    numbers = re.findall(r'\b\d{5,6}\b', text)
    
    # Обычно ИД идет в конце страницы, а номер документа в середине
    if len(numbers) >= 2:
        res["num_doc"] = numbers[0] # Первый найденный номер
        res["id"] = numbers[-1]     # Последний (внизу страницы) — это ИД
    elif len(numbers) == 1:
        res["id"] = numbers[0]

    # Поиск дат
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
