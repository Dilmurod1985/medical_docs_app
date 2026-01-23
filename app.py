import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from ocr.ocr_engine import OCREngine
from parser.parser import MedicalDocumentParser
from exporter.exporter import ExcelExporter

st.set_page_config(page_title="Medical Scan", layout="wide")
st.title("🏥 Система обработки медосмотров")

# Инициализация
ocr = OCREngine()
parser = MedicalDocumentParser()
exporter = ExcelExporter()

files = st.file_uploader("Загрузите фотографии", accept_multiple_files=True)

if files:
    results = []
    for f in files:
        with st.spinner(f'Обработка {f.name}...'):
            img = np.array(Image.open(f).convert('RGB'))
            text_data = ocr.extract_text(img)
            data = parser.parse(text_data)
            
            # Сопоставляем данные с твоей таблицей
            results.append({
                "ИД сотрудника": data.get("id"),
                "ФИО": data.get("fio"),
                "Статус медосмотра годен/не годен": "годен",
                "Дата медосмотра": data.get("exam_date"),
                "След. Дата медосмотра": data.get("next_date"),
                "Серия документа": "ТК",
                "Номер документа": data.get("doc_num"),
                "Выдано": "Тиббий кўрик МЧЖ",
                "Дата выдачи": data.get("exam_date"),
                "Дата начала действия": data.get("exam_date"),
                "Дата истечения": data.get("next_date")
            })

    df = pd.DataFrame(results)
    st.table(df)

    if not df.empty:
        excel_data = exporter.export_to_excel(df)
        st.download_button("📥 Скачать Excel отчет", data=excel_data, file_name="report.xlsx")
