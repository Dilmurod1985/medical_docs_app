import re
from datetime import datetime, timedelta

def parse_medical_book_text(full_text):
    """
    Функция для извлечения данных из текста медкнижки.
    """
    # Переводим в нижний регистр для удобства поиска
    text = full_text.lower()
    
    # Заготовка для результата
    res = {
        "id": "Не найдено", 
        "fio": "Не найдено", 
        "status": "годен",
        "date": "Не найдено", 
        "next": "Не рассчитано"
    }

    # 1. Поиск ИД сотрудника (ищем 6 цифр подряд, например 057304)
    id_match = re.search(r'(\d{6})', text)
    if id_match: 
        res["id"] = id_match.group(1)

    # 2. Поиск ФИО (Ищем слова с большой буквы в оригинальном тексте)
    fio_match = re.search(r'([А-ЯЁ][а-яё\-]+\s+[А-ЯЁ][а-яё\-]+(?:\s+[А-ЯЁ][а-яё\-]+)?)', full_text)
    if fio_match:
        res["fio"] = fio_match.group(1)

    # 3. Поиск дат (форматы 23.01.2026 или 23/01/26)
    dates = re.findall(r'(\d{2}[.\/]\d{2}[.\/]\d{2,4})', text)
    if dates:
        date_str = dates[0].replace('/', '.')
        res["date"] = date_str
        try:
            # Определяем формат года (2 или 4 цифры)
            fmt = "%d.%m.%Y" if len(date_str) > 8 else "%d.%m.%y"
            dt = datetime.strptime(date_str, fmt)
            
            # Прибавляем 182 дня (примерно 6 месяцев)
            next_dt = dt + timedelta(days=182)
            res["next"] = next_dt.strftime("%d.%m.%Y")
        except: 
            pass
    
    return res
