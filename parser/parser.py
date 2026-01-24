import re
from datetime import datetime, timedelta

# --- 1. ПРАВИЛА (вместо aliases.py) ---
FIELD_ALIASES = {
    "number": ["№", "raqami", "номер", "id", "raqa", "raqam"],
    "date": ["sana", "дата", "дата осмотра", "осмотр", "berilgan", "ko'rik"],
    "series": ["seriyasi", "серия", "seriya", "mt", "tk", "ab"]
}

# --- 2. ВАЛИДАТОР (вместо validators.py) ---
def normalize_date(raw_date: str, add_half_year: bool = False) -> str:
    # Исправление типичных OCR-ошибок (буквы на цифры)
    cleaned = (raw_date.replace("i", "1").replace("I", "1")
                       .replace("O", "0").replace("o", "0")
                       .replace("A", "4").replace("s", "5")
                       .replace("S", "5").replace("B", "8"))
    
    # Оставляем только цифры и разделители
    cleaned = "".join([c if c.isdigit() or c in "./-" else "." for c in cleaned])

    for fmt in ("%d.%m.%Y", "%d.%m.%y", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            if add_half_year:
                dt += timedelta(days=182) # Твои полгода
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue
    return "Не найдено"

# --- 3. ГЛАВНЫЙ ПАРСЕР ---
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

    # Поиск даты
    date_pattern = r"\b\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4}\b"
    dates = re.findall(date_pattern, text_lower)
    if dates:
        result["Дата медосмотра"] = normalize_date(dates[0])
        result["След. медосмотр"] = normalize_date(dates[0], add_half_year=True)

    # Поиск Серии
    for alias in FIELD_ALIASES["series"]:
        match = re.search(rf"{alias}\s*([a-z]{{2}})", text_lower, re.I)
        if match:
            result["Серия"] = match.group(1).upper()
            break

    # Поиск Номера
    for alias in FIELD_ALIASES["number"]:
        match = re.search(rf"{alias}\s*(\d{{5,7}})", text_lower, re.I)
        if match:
            result["Номер"] = result["ИД сотрудника"] = match.group(1)
            break

    return result
