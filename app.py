import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from ocr.ocr_engine import OCREngine
from parser.parser import MedicalDocumentParser
from exporter.exporter import ExcelExporter

st.set_page_config(page_title="Medical Docs", layout="wide")
st.title("🏥 Автоматизация медосмотров")

# Инициализация инструментов
ocr_tool = OCREngine()
parser_tool = MedicalDocumentParser()
exporter_tool = ExcelExporter()

uploaded_files = st.file_uploader("Загрузите фото документов", accept_multiple_files=True)

if uploaded_files:
    results = []
    for uploaded_file in uploaded_files:
        with st.spinner(f'Обработка {uploaded_file.name}...'):
            # Чтение фото
            image = Image.open(uploaded_file)
            img_array = np.array(image.convert('RGB'))
            
            # OCR + Парсинг
            raw_text = ocr_tool.extract_text(img_array)
            data = parser_tool.parse(raw_text)
            
            # Сопоставление колонок (используем .get чтобы не было KeyError)
            results.append({
                "ИД сотрудника": data.get("id"),
                "ФИО": data.get("fio"),
                "Статус медосмотра годен/не годен": data.get("status"),
                "Дата медосмотра": data.get("exam_date"),
                "След. Дата медосмотра": data.get("next_date"),
                "Серия документа": data.get("seria"),
                "Номер документа": data.get("nomer"),
                "Выдано": data.get("org"),
                "Дата выдачи": data.get("issue_date"),
                "Дата начала действия": data.get("issue_date"),
                "Дата истечения": data.get("next_date")
            })

    # Создаем таблицу
    df = pd.DataFrame(results)
    st.success("Обработка завершена!")
    st.table(df)

    # Кнопка скачивания
    if not df.empty:
        excel_file = exporter_tool.export_to_excel(df)
        st.download_button(
            label="📥 Скачать Excel отчет",
            data=excel_file,
            file_name="med_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
