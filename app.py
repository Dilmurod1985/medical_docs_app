import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import io
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text

st.set_page_config(page_title="MedScan Pro", layout="wide")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ru', 'en'], gpu=False)

reader = load_ocr()

files = st.file_uploader("Загрузите фото документов", accept_multiple_files=True)

if files:
    all_results = []
    for f in files:
        with st.spinner(f'Обработка {f.name}...'):
            img_proc = preprocess_for_ocr(f.getvalue())
            
            # --- ТВОЯ ИДЕЯ С КРОПОМ ---
            w, h = img_proc.size
            # Обрезаем: берем только нижнюю часть (60% сверху отрезаем)
            cropped_img = img_proc.crop((0, h * 0.5, w, h)) 
            
            # Распознаем текст на обрезанном фото (точность будет выше)
            raw_text_list = reader.readtext(np.array(cropped_img), detail=0)
            full_text = " ".join(raw_text_list)
            
            # Парсим данные
            data = parse_medical_book_text(full_text)
            data["Файл"] = f.name
            all_results.append(data)

    # Отображение таблицы
    if all_results:
        df = pd.DataFrame(all_results)
        st.subheader("📋 Данные из нижней части документа (Серия, Номер, Даты)")
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
        
        # Кнопка Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            edited_df.drop(columns=['Файл']).to_excel(writer, index=False)
        st.download_button("📥 Скачать Excel", buffer.getvalue(), file_name="med_data.xlsx")
