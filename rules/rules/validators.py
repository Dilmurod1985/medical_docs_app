from datetime import datetime, timedelta

def normalize_date(raw_date: str, add_half_year: bool = False) -> str:
    # Исправление типичных OCR-ошибок (буквы на цифры)
    cleaned = (raw_date.replace("i", "1")
                       .replace("I", "1")
                       .replace("O", "0")
                       .replace("o", "0")
                       .replace("A", "4")
                       .replace("s", "5")
                       .replace("S", "5")
                       .replace("B", "8"))
    
    # Оставляем только цифры и разделители
    cleaned = "".join([c if c.isdigit() or c in "./-" else "." for c in cleaned])

    for fmt in ("%d.%m.%Y", "%d.%m.%y", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(cleaned, fmt)
            if add_half_year:
                # Твоё правило: каждые полгода осмотр
                dt += timedelta(days=182)
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue
    return "Не найдено"
