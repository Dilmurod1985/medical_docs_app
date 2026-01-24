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
    
    # Распределяем: ИД — это обычно самое последнее число внизу страницы
    if len(numbers) >= 2:
        res["id"] = numbers[-1]     # Нижнее число
        res["num_doc"] = numbers[0] # Верхнее/среднее число
    elif len(numbers) == 1:
        res["id"] = numbers[0]

    # Поиск дат (осмотра и выдачи)
    dates = re.findall(r'(\d{2}[.\s\-/]\d{2}[.\s\-/]\d{2,4})', text)
    if dates:
        d = re.sub(r'[\s\-/]', '.', dates[0])
        res["date_osm"] = res["date_vidano"] = res["date_start"] = d
        try:
            dt = datetime.strptime(d, "%d.%m.%Y" if len(d) > 8 else "%d.%m.%y")
            next_d = (dt + timedelta(days=182)).strftime("%d.%m.%Y")
            res["next_osm"] = res["date_end"] = next_d
        except: pass
            
    return res
