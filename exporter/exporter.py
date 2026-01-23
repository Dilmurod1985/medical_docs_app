import pandas as pd
import io

class ExcelExporter:
    def __init__(self):
        pass

    def export_to_excel(self, df: pd.DataFrame):
        """
        Преобразует DataFrame в байтовый поток Excel файла.
        """
        output = io.BytesIO()
        # Используем движок xlsxwriter для создания файла
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Медосмотры')
            
            # Настройка ширины колонок для красоты
            workbook = writer.book
            worksheet = writer.sheets['Медосмотры']
            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                worksheet.set_column(i, i, column_len)
        
        return output.getvalue()
