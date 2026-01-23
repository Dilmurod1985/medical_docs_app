import re
from datetime import datetime, timedelta

def parse_medical_text(full_text):
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

    text = full_text.lower().replace("ё", "е").replace("\n", " ")

    # ФИО
    fio_match = re.search(r'[а-яa-z]+\s+[а-яa-z]+\s*[а-яa-z]*\.?', text)
    if fio_match:
        result["ФИО"] = fio_match.group(0).title()

    # ИД
    id_match = re.search(r'(?:ид|id|номер|№)\s*[:№]?\s*([a-zа-я0-9-]{5,15})', text)
    if id_match:
        result["ИД сотрудника"] = id_match.group(1).upper()

    # Дата
    date_match = re.search(r'(?:осмотр|кўрик|пройден|дата|от)\s*(\d{1,2}[./]\d{1,2}[./]\d{2,4})', text)
    if date_match:
        date_str = date_match.group(1)
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y") if '.' in date_str else datetime.strptime(date_str, "%d/%m/%Y")
            result["Дата медосмотра"] = date_obj.strftime("%d.%m.%Y")
            next_date = date_obj + timedelta(days=183)
            result["След. Дата медосмотра"] = next_date.strftime("%d.%m.%Y")
        except:
            pass

    # Статус
    if "годен" in text:
        result["Статус медосмотра"] = "Годен"
    elif "не годен" in text or "негоден" in text:
        result["Статус медосмотра"] = "Не годен"

    return result
