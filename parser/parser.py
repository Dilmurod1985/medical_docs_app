import re
# ВОТ ЭТОТ БЛОК СТАВИМ В НАЧАЛО:
try:
    from rules.aliases import FIELD_ALIASES
    from rules.validators import normalize_date
except ImportError:
    # Если запуск идет из папки parser, используем относительный путь
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rules.aliases import FIELD_ALIASES
    from rules.validators import normalize_date

def parse_med_doc(text: str) -> dict:
    text_lower = text.lower().replace("\n", " ")
    result = {
        "ИД сотрудника": "Не найдено",
        "ФИО": "Впишите вручную",
        "Статус": "годен",
        "Дата медосмотра": "Не найдено",
        "След. медосмотр": "Не рассчитан",
        "Серия": "Не найдено",
        "Номер": "Не найдено"
    }

    # 1. Поиск даты (используем твой новый валидатор)
    date_pattern = r"\b\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4}\b"
    dates = re.findall(date_pattern, text_lower)
    if dates:
        result["Дата медосмотра"] = normalize_date(dates[0])
        result["След. медосмотр"] = normalize_date(dates[0], add_half_year=True)

    # 2. Поиск Серии через FIELD_ALIASES
    for alias in FIELD_ALIASES["series"]:
        match = re.search(rf"{alias}\s*([a-z]{{2}})", text_lower, re.I)
        if match:
            result["Серия"] = match.group(1).upper()
            break

    # 3. Поиск Номера через FIELD_ALIASES
    for alias in FIELD_ALIASES["number"]:
        match = re.search(rf"{alias}\s*(\d{{5,7}})", text_lower, re.I)
        if match:
            result["Номер"] = result["ИД сотрудника"] = match.group(1)
            break

    return result
