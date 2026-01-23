import pandas as pd
import io

class ExcelExporter:
    def __init__(self):
        pass

    def export_to_excel(self, df):
        # Создаем виртуальный файл в памяти (BytesIO)
        output = io.BytesIO()
        
        # Записываем данные без использования путей к папкам
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Результаты')
        
        # Возвращаем готовый файл для кнопки скачивания
        return output.getvalue()
