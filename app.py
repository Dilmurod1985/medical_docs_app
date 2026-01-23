import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import sys
import os

# Пытаемся подключить твои модули
try:
    from ocr.ocr_engine import OCREngine
    from parser.parser import MedicalDocumentParser
    from exporter.exporter import ExcelExporter
except ImportError as e:
    st.error(f"Ошибка загрузки модулей: {e}. Проверьте наличие папок ocr, parser и exporter.")

st.set_page_config(page_title="Медосмотры", layout="wide")

st.title("🏥 Система медосмотров")
st.write(f"Сегодня: {pd.to_datetime('today').strftime('%d.%m.%Y')}")

# Проверка наличия инструментов
try:
    ocr_engine = OCREngine()
    parser = MedicalDocumentParser()
    exporter = ExcelExporter()
    
    # ВОТ ЭТА КНОПКА ДОЛЖНА ПОЯВИТЬСЯ:
    uploaded_files = st.file_uploader("Выберите фото медкнижек", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

    if uploaded_files:
        results = []
        for uploaded_file in uploaded_files:
            with st.spinner(f'Обрабатываем {uploaded_file.name}...'):
                image = Image.open(uploaded_file)
                img_array = np.array(image.convert('RGB'))
                
                ocr_data = ocr_engine.extract_text(img_array)
                parsed_data = parser.parse(ocr_data)
                results.append({
            "ИД сотрудника": parsed_data["ИД сотрудника"],
            "ФИО": parsed_data["ФИО"],
            "Статус медосмотра годен/не годен": parsed_data["Статус медосмотра"],
            "Дата медосмотра": parsed_data["Дата медосмотра"],
            "След. Дата медосмотра": parsed_data["След. Дата медосмотра"],
            "Серия документа": parsed_data["Серия документа"],
            "Номер документа": parsed_data["Номер документа"],
            "Выдано": parsed_data["Выдано"],
            "Дата выдачи": parsed_data["Дата выдачи"],
            "Дата начала действия": parsed_data["Дата начала действия"],
            "Дата истечения": parsed_data["Дата истечения"]
        })

        df = pd.DataFrame(results)
        st.table(df)

        if not df.empty:
            excel_data = exporter.export_to_excel(df)
            st.download_button(
                label="📥 Скачать Excel",
                data=excel_data,
                file_name="report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
except NameError:
    st.warning("Приложение настраивается. Подождите немного...")


