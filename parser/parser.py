import re
from datetime import datetime, timedelta

def parse_medical_book_text(full_text):
    # Очистка текста от мусора
    text = " ".join(full_text.split())
    res = {
        "id": "", "fio": "", "status": "годен", "date": "", "next": "",
        "seriya": "TK", "num_doc": ""
    }

    # 1. Поиск ИД (напечатан четко внизу страницы)
    id_match = re.search(r'(\d{6})', text)
    if id_match: res["id"] = id_match.group(1)

    # 2. Поиск ФИО (пробуем вытащить рукописный текст)
    # Ищем слова длиннее 3 символов с большой буквы, исключая служебные слова
    blacklist = ["familiyasi", "ismi", "otasining", "shaxsiy", "tibbiyot", "kitobchasi", "berildi"]
    words = text.split()
    found_names = []
    for w in words:
        clean_w = re.sub(r'[^а-яА-ЯёЁa-zA-Z]', '', w)
        if len(clean_w) > 3 and clean_w[0].isupper() and clean_w.lower() not in blacklist:
            found_names.append(clean_w)
    
    if found_names:
        res["fio"] = " ".join(found_names[:3])

    # 3. Поиск дат (для колонки осмотра)
    dates = re.findall(r'(\d{2}[.\s\-/]\d{2}[.\s\-/]\d{2,4})', text)
    if dates:
        clean_date = re.sub(r'[\s\-/]', '.', dates[0])
        res["date"] = clean_date
        try:
            dt = datetime.strptime(clean_date, "%d.%m.%Y" if len(clean_date) > 8 else "%d.%m.%y")
            res["next"] = (dt + timedelta(days=182)).strftime("%d.%m.%Y")
        except: pass
            
    return res
