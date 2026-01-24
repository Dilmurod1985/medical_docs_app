import streamlit as st
import pandas as pd
import numpy as np
import easyocr
from PIL import Image
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text
from exporter.exporter import ExcelExporter

st.set_page_config(page_title="Система медосмотров", layout="wide")
st.title("🏥 Система медосмотров")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['ru', 'uz'])

reader = load_reader()
ex = ExcelExporter()

files = st.file_uploader("Загрузите страницы медкнижки", accept_multiple_files=True)

if files:
    results = []
    for f in files:
        with st.spinner(f'Обработка {f.name}...'):
            try:
                # 1. Предобработка
                proc_img = preprocess_for_ocr(f.getvalue())
                # 2. OCR
                text_list = reader.readtext(np.array(proc_img), detail=0)
                full_text = " ".join(text_list)
                # 3. Парсинг
                data = parse_medical_book_text(full_text)
                
                results.append({
                    "ИД сотрудника": data["id"],
                    "ФИО": data["fio"],
                    "Статус": data["status"],
                    "Дата осмотра": data["date"],
                    "Следующий осмотр": data["next"]
                })
            except Exception as e:
                st.error(f"Ошибка в файле {f.name}: {e}")

    if results:
        df = pd.DataFrame(results)
        st.table(df)
        xlsx = ex.export_to_excel(df)
        st.download_button("📥 Скачать Excel отчет", data=xlsx, file_name="report.xlsx")
