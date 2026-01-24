import streamlit as st
import pandas as pd
import numpy as np
import easyocr
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text
from exporter.exporter import ExcelExporter

st.title("🏥 Система медосмотров")

# Загрузка моделей
@st.cache_resource
def load_reader():
    return easyocr.Reader(['ru', 'uz'])

reader = load_reader()
ex = ExcelExporter()

files = st.file_uploader("Загрузите фото", accept_multiple_files=True)

if files:
    results = []
    for f in files:
        try:
            # Предобработка
            proc_img = preprocess_for_ocr(f.getvalue())
            # Распознавание
            text_list = reader.readtext(np.array(proc_img), detail=0)
            full_text = " ".join(text_list)
            # Парсинг
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
        st.download_button("📥 Скачать Excel", data=xlsx, file_name="otchet.xlsx")
