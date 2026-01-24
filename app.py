import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import io
from PIL import Image
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text

st.set_page_config(page_title="MedScan Pro", layout="wide")
st.title("🏥 Умный сканер медкнижек")

@st.cache_resource
def load_ocr():
    # 'en' заменяет 'uz' для стабильности кириллицы
    return easyocr.Reader(['ru', 'en'], gpu=False)

reader = load_ocr()

files = st.file_uploader("Загрузите фото документов", accept_multiple_files=True)

if files:
    all_data = []
    for f in files:
        with st.spinner(f'Анализируем {f.name}...'):
            try:
                img_proc = preprocess_for_ocr(f.getvalue())
                raw_results = reader.readtext(np.array(img_proc), detail=0)
                full_text = " ".join(raw_results)
                data = parse_medical_book_text(full_text)
                
                all_data.append({
                    "ИД сотрудника": data["id"],
                    "ФИО": data["fio"],
                    "Статус": data["status"],
                    "Дата осмотра": data["date"],
                    "Следующий осмотр": data["next"]
                })
            except Exception as e:
                st.error(f"Ошибка: {e}")

    if all_data:
        st.subheader("📝 Проверьте и отредактируйте данные")
        # st.data_editor позволяет менять текст в ячейках кликом мышки!
        edited_df = st.data_editor(pd.DataFrame(all_data), num_rows="dynamic")
        
        # Генерация Excel
        buffer = io.BytesIO()
        try:
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                edited_df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            st.download_button(
                label="📥 Скачать готовый Excel отчет",
                data=buffer.getvalue(),
                file_name="med_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Ошибка Excel: {e}")
