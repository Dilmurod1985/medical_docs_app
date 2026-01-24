import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import io
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text

st.set_page_config(page_title="Мед Книжка Excel", layout="wide")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ru', 'en'], gpu=False)

reader = load_ocr()

files = st.file_uploader("Загрузите фото", accept_multiple_files=True)

if files:
    all_data = []
    for f in files:
        with st.spinner(f'Обработка {f.name}...'):
            try:
                img_proc = preprocess_for_ocr(f.getvalue())
                raw_text = reader.readtext(np.array(img_proc), detail=0)
                data = parse_medical_book_text(" ".join(raw_text))
                
                # Колонки точно как на твоем скриншоте!
                all_data.append({
                    "ИД сотрудника": data["id"],
                    "ФИО": data["fio"],
                    "Статус медосмотра годен/не годен": data["status"],
                    "Дата медосмотра": data["date"],
                    "След. Дата медосмотра": data["next"],
                    "Серия документа": data["seriya"],
                    "Номер документа": data["num_doc"],
                    "Выдано": data["vidano"],
                    "Дата выдачи": data["date_vidano"],
                    "Дата начала действия": data["date_start"],
                    "Дата истечения": data["date_end"]
                })
            except Exception as e:
                st.error(f"Ошибка: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        st.subheader("📋 Проверьте данные перед выгрузкой")
        # Редактируемая таблица
        edited_df = st.data_editor(df, num_rows="dynamic")
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            edited_df.to_excel(writer, index=False, sheet_name='Sheet1')
            
        st.download_button(
            label="📥 Скачать Excel отчет",
            data=buffer.getvalue(),
            file_name="med_knizhka.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
