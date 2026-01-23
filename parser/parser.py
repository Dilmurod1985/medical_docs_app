import re
from datetime import datetime, timedelta

def parse_medical_book_text(full_text):
    """
    Умный парсер текста из медкнижки.
    Возвращает словарь с заполненными полями.
    """
    result = {
        "ИД сотрудника": "Не найдено",
        "ФИО": "Не найдено",
        "Статус медосмотра": "Не определён",
        "Дата медосмотра": "Не найдено",
        "След. Дата медосмотра": "Не рассчитано",
        "Серия": "Не найдено",
        "Номер": "Не найдено",
        "Выдано": "Не найдено",
        "Дата выдачи": "Не найдено",
        "Дата начала действия": "Не найдено",
        "Дата истечения": "Не найдено"
    }

    # Нормализация текста
    text = full_text.lower().replace("ё", "е").replace("\n", " ")

    # 1. ФИО (рус/узб): имя + фамилия + отчество/инициалы
    fio_pattern = r'(?:[а-яa-z]+\s+){1,4}[а-яa-z]+(?:\s+[а-яa-z]+\.?)?'
    fio_match = re.search(fio_pattern, text)
    if fio_match:
        result["ФИО"] = fio_match.group(0).strip().title()

    # 2. ИД сотрудника (часто 7–14 цифр или с буквами)
    id_patterns = [
        r'(?:ид|id|номер|№|№№)\s*[:№]?\s*([a-zа-я0-9-]{5,15})',
        r'\b(\d{7,14})\b'
    ]
    for pattern in id_patterns:
        match = re.search(pattern, text)
        if match:
            result["ИД сотрудника"] = match.group(1).strip()
            break

    # 3. Дата медосмотра (рядом с ключевыми словами)
    date_patterns = [
        r'(?:осмотр|кўрик|пройден|дата|от|протокол|заключение|медосмотр)\s*(?:от\s*)?(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
        r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})\s*(?:г\.|г)?'
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            try:
                # Пробуем разные форматы
                for fmt in ["%d.%m.%Y", "%d/%m/%Y", "%d.%m.%y", "%d/%m/%y"]:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        if date_obj.year < 2000:
                            date_obj = date_obj.replace(year=date_obj.year + 2000)
                        result["Дата медосмотра"] = date_obj.strftime("%d.%m.%Y")
                        next_date = date_obj + timedelta(days=183)  # ≈6 месяцев
                        result["След. Дата медосмотра"] = next_date.strftime("%d.%m.%Y")
                        break
                    except ValueError:
                        continue
            except:
                pass
            if result["Дата медосмотра"] != "Не найдено":
                break

    # 4. Статус (годен/не годен)
    if any(word in text for word in ["годен", "годен до", "годен", "здоров"]):
        result["Статус медосмотра"] = "Годен"
    elif any(word in text for word in ["не годен", "негоден", "не здоров"]):
        result["Статус медосмотра"] = "Не годен"

    # 5. Серия и номер (часто рядом)
    series_match = re.search(r'(?:серия|сер)\s*([а-яa-z0-9]{2,6})', text)
    if series_match:
        result["Серия"] = series_match.group(1).upper()

    number_match = re.search(r'(?:номер|№)\s*(\d{6,12})', text)
    if number_match:
        result["Номер"] = number_match.group(1)

    # 6. Выдано / кем
    issued_match = re.search(r'(?:выдано|кем|медпункт|поликлиника)\s*([а-яa-z0-9\s\-.,]+)', text)
    if issued_match:
        result["Выдано"] = issued_match.group(1).strip().title()

    return result
