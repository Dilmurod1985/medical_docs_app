import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from ocr.ocr_engine import OCREngine
from parser.parser import MedicalDocumentParser
from exporter.exporter import ExcelExporter

st.set_page_config(page_title="Medical System", layout="wide")
st.title("🏥 Автоматизация медосмотров")

# Инструменты
ocr_tool = OCREngine()
parser_tool = MedicalDocumentParser()
exporter_tool = ExcelExporter()

files = st.file_uploader("Загрузите фото документов", accept_multiple_files=True)

if files:
    table_data = []
    for f in files:
        with st.spinner(f'Читаем {f.name}...'):
            img = np.array(Image.open(f).convert('RGB'))
            raw_text = ocr_tool.extract_text(img)
            d = parser_tool.parse(raw_text)
            
            # Сопоставляем с твоим Excel-образцом (11 колонок)
            table_data.append({
                "ИД сотрудника": d.get("id"),
                "ФИО": d.get("fio"),
                "Статус медосмотра годен/не годен": d.get("status"),
                "Дата медосмотра": d.get("date"),
                "След. Дата медосмотра": d.get("next"),
                "Серия документа": d.get("seria"),
                "Номер документа": d.get("nomer"),
                "Выдано": d.get("org"),
                "Дата выдачи": d.get("issue"),
                "Дата начала действия": d.get("issue"),
                "Дата истечения": d.get("next")
            })

    df = pd.DataFrame(table_data)
    st.table(df)

    if not df.empty:
        # Скачивание Excel
        excel_bytes = exporter_tool.export_to_excel(df)
        st.download_button(
            label="📥 Скачать Excel отчет",
            data=excel_bytes,
            file_name="report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
