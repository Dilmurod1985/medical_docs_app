import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from ocr.ocr_engine import OCREngine
from parser.parser import MedicalDocumentParser
from exporter.exporter import ExcelExporter

st.set_page_config(page_title="Medical Scan", layout="wide")
st.title("🏥 Автоматизация медосмотров")

# Загружаем инструменты
ocr = OCREngine()
p = MedicalDocumentParser()
ex = ExcelExporter()

files = st.file_uploader("Загрузите фото документов", accept_multiple_files=True)

if files:
    all_rows = []
    for f in files:
        with st.spinner(f'Анализируем {f.name}...'):
            img = np.array(Image.open(f).convert('RGB'))
            text_data = ocr.extract_text(img)
            res = p.parse(text_data)
            
            # Собираем строку строго по твоему шаблону
            all_rows.append({
                "ИД сотрудника": res.get("id", ""),
                "ФИО": res.get("fio", "Не найдено"),
                "Статус медосмотра годен/не годен": "годен",
                "Дата медосмотра": res.get("exam_date", ""),
                "След. Дата медосмотра": res.get("next_date", ""),
                "Серия документа": "ТК",
                "Номер документа": res.get("nomer", ""),
                "Выдано": "Тиббий кўрик МЧЖ",
                "Дата выдачи": res.get("exam_date", ""),
                "Дата начала действия": res.get("exam_date", ""),
                "Дата истечения": res.get("next_date", "")
            })

    df = pd.DataFrame(all_rows)
    st.table(df)

    if not df.empty:
        xlsx = ex.export_to_excel(df)
        st.download_button("📥 Скачать Excel отчет", data=xlsx, file_name="report.xlsx")
