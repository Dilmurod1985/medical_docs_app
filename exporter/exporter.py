import pandas as pd
import io

class ExcelExporter:
    def __init__(self):
        pass

    def export_to_excel(self, df):
        """Создает Excel файл в памяти для скачивания"""
        output = io.BytesIO()
        # Используем движок xlsxwriter
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Медосмотры')
        return output.getvalue()
