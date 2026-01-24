import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import io
from PIL import Image
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text

st.set_page_config(page_title="MedScan Pro", layout="wide")
st.title("🏥 Умный конвертер медкнижек")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ru', 'en'], gpu=False)

reader = load_ocr()

col1, col2 = st.columns([1, 1]) # Делим экран на две части

with col1:
    files = st.file_uploader("Шаг 1: Загрузите фото документов", accept_multiple_files=True)

if files:
    all_data = []
    with col2:
        st.subheader("👀 Оригинал документа")
        # Показываем последнее загруженное фото для проверки почерка
        last_file = files[-1]
        st.image(last_file, caption="Посмотрите ФИО здесь и впишите в таблицу слева", use_container_width=True)

    for f in files:
        with st.spinner(f'Распознаем печатные данные...'):
            try:
                img_proc = preprocess_for_ocr(f.getvalue())
                raw_text = reader.readtext(np.array(img_proc), detail=0)
                data = parse_medical_book_text(" ".join(raw_text))
                
                all_data.append({
                    "ИД сотрудника": data["id"],
                    "ФИО (впишите вручную)": data["fio"],
                    "Дата медосмотра": data["date"],
                    "След. медосмотр": data["next"],
                    "Файл": f.name
                })
            except Exception as e:
                st.error(f"Ошибка: {e}")

    if all_data:
        with col1:
            st.subheader("Шаг 2: Проверьте и исправьте данные")
            # Редактируемая таблица
            edited_df = st.data_editor(pd.DataFrame(all_data), use_container_width=True)
            
            # Генерация Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                edited_df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Шаг 3: Скачать готовый Excel",
                data=buffer.getvalue(),
                file_name="med_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
