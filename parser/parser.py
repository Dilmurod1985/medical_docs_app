import re
from datetime import datetime, timedelta

def parse_medical_book_text(full_text):
    text = full_text.lower().replace("ё", "е").replace("\n", " ").strip()
        
    result = {
        "ИД сотрудника": "Не найдено", "ФИО": "Впишите вручную", "Статус": "Не определён",
        "Дата медосмотра": "Не найдено", "След. медосмотр": "Не рассчитано",
        "Серия": "Не найдено", "Номер": "Не найдено", "Дата выдачи": "Не найдено"
    }

    # Серия (MT, AB, TK и др.)
    series_match = re.search(r'(?:seriyasi|серия|seriya|mt|ab|tk)\s*([a-z]{1,3}\s*[0-9]{0,3})', text, re.I)
    if series_match:
        result["Серия"] = series_match.group(1).upper().replace(" ", "")

    # Номер (5–7 цифр)
    number_match = re.search(r'(?:raqami|номер|number|raqa|№)\s*(\d{5,7})', text, re.I)
    if number_match:
        result["Номер"] = result["ИД сотрудника"] = number_match.group(1)

    # Даты (Выдача и Осмотр)
    date_pattern = r'(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})'
    dates = re.findall(date_pattern, text)
    if dates:
        clean_date = dates[0].replace('/', '.').replace('-', '.')
        result["Дата медосмотра"] = result["Дата выдачи"] = clean_date
        try:
            d = datetime.strptime(clean_date, "%d.%m.%Y" if len(clean_date) > 8 else "%d.%m.%y")
            next_d = d + timedelta(days=183) # +6 месяцев
            result["След. медосмотр"] = next_d.strftime("%d.%m.%Y")
        except: pass

    # Статус
    if any(word in text for word in ["goden", "годен", "yil", "year", "yaroqli"]):
        result["Статус"] = "Годен"

    return result
