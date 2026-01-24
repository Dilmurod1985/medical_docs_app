import re
from datetime import datetime, timedelta

def normalize_date(raw_date: str, add_half_year: bool = False) -> str:
    """Исправляет ошибки OCR в датах и прибавляет полгода."""
    if not raw_date:
        return "Не найдено"

    # 1. Исправляем типичные ошибки (буквы вместо цифр)
    cleaned = (raw_date.lower()
               .replace("i", "1").replace("l", "1").replace("|", "1")
               .replace("o", "0").replace("s", "5").replace("б", "6")
               .replace("в", "8").replace("а", "4"))
    
    # 2. Оставляем только цифры и разделители
    cleaned = re.sub(r'[^0-9\.\-\/]', '', cleaned)
    
    # 3. Пытаемся распознать формат
    for fmt in ("%d.%m.%Y", "%d.%m.%y", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            # Если год двузначный (напр. 24), корректируем его до 2024
            if dt.year < 100:
                dt = dt.replace(year=dt.year + 2000)
            
            if add_half_year:
                # Твоё условие: осмотр каждые полгода (182 дня)
                dt += timedelta(days=182)
                
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue
            
    return "Не найдено"

def parse_med_doc(text: str) -> dict:
    """Основной парсер для медкнижек."""
    # Очистка текста для поиска
    text_lower = text.lower().replace("\n", " ")
    
    result = {
        "ИД сотрудника": "Не найдено",
        "ФИО": "Впишите вручную",
        "Статус": "годен", # Дефолт, как ты просил
        "Дата медосмотра": "Не найдено",
        "След. медосмотр": "Не рассчитан",
        "Серия": "Не найдено",
        "Номер": "Не найдено"
    }

    # 1. ПОИСК СЕРИИ (MT, AB и т.д.)
    # Ищем два латинских символа, которые стоят рядом с ключевыми словами
    series_match = re.search(r'(?:seriya|seriyasi|серия|mt|ab)\s*([a-z]{2})', text_lower)
    if series_match:
        result["Серия"] = series_match.group(1).upper()
    else:
        # Резервный поиск: просто ищем MT или AB в тексте
        standalone_series = re.search(r'\b(mt|ab)\b', text_lower)
        if standalone_series:
            result["Серия"] = standalone_series.group(1).upper()

    # 2. ПОИСК НОМЕРА (5-7 цифр)
    # Ищем цифры после "№" или слова "номер"
    number_match = re.search(r'(?:raqami|№|номер|number|id)\s*(\d{5,7})', text_lower)
    if number_match:
        result["Номер"] = result["ИД сотрудника"] = number_match.group(1)
    else:
        # Резервный поиск: любые 6 цифр подряд
        fallback_num = re.search(r'\b(\d{6})\b', text_lower)
        if fallback_num:
            result["Номер"] = result["ИД сотрудника"] = fallback_num.group(1)

    # 3. ПОИСК ДАТЫ
    # Ищем паттерны типа 19.10.2024 или 19-10-24
    date_pattern = r'(\d{1,2}[\.\-\/]\d{1,2}[\.\-\/]\d{2,4})'
    dates = re.findall(date_pattern, text_lower)
    
    if dates:
        # Берем первую найденную дату (обычно это дата выдачи/осмотра)
        result["Дата медосмотра"] = normalize_date(dates[0])
        result["След. медосмотр"] = normalize_date(dates[0], add_half_year=True)

    # 4. СТАТУС (доп. проверка)
    if "yaroqli" in text_lower or "годен" in text_lower or "goden" in text_lower:
        result["Статус"] = "годен"

    return result
