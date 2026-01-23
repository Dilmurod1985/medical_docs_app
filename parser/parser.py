import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class MedicalDocumentParser:
    def __init__(self):
        # Ищем форматы: ДД.ММ.ГГГГ, ДД/ММ/ГГГГ, ДД.ММ.ГГ
        self.date_pattern = re.compile(r'(\b\d{1,2}[.\/]\d{1,2}[.\/]\d{2,4}\b)')

    def parse(self, ocr_results):
        parsed_data = {
            'examination_date': None,
            'next_visit_date': None,
            'raw_text': ""
        }
        
        all_text = " ".join([item['text'] for item in ocr_results])
        parsed_data['raw_text'] = all_text
        
        found_dates = self.date_pattern.findall(all_text)
        
        valid_dates = []
        for date_str in found_dates:
            try:
                # Очищаем строку и пытаемся превратить в дату
                clean_date_str = date_str.replace('/', '.')
                if len(clean_date_str.split('.')[-1]) == 2:
                    dt = datetime.strptime(clean_date_str, '%d.%m.%y')
                else:
                    dt = datetime.strptime(clean_date_str, '%d.%m.%Y')
                
                # Игнорируем даты рождения (условно всё, что раньше 2010 года)
                if dt.year > 2010:
                    valid_dates.append(dt)
            except:
                continue
        
        if valid_dates:
            # Берем самую последнюю дату (самый свежий осмотр)
            latest_date = max(valid_dates)
            parsed_data['examination_date'] = latest_date.strftime('%d.%m.%Y')
            
            # Твое правило: осмотр каждые полгода (+6 месяцев)
            next_visit = latest_date + relativedelta(months=6)
            parsed_data['next_visit_date'] = next_visit.strftime('%d.%m.%Y')
            
        return parsed_data
