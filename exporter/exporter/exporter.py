import pandas as pd
import io

class ExcelExporter:
    def __init__(self):
        pass

    def export_to_excel(self, df):
        """
        Создает Excel файл в памяти и возвращает байты.
        """
        output = io.BytesIO()
        # Мы НЕ используем output_path, а пишем прямо в поток output
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Результаты')
        
        return output.getvalue()
