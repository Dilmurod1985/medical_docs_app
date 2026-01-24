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

# Инициализация списка
if 'final_rows' not in st.session_state:
    st.session_state.final_rows = []

with st.sidebar:
    st.header("📂 Загрузка")
    uploaded = st.file_uploader("Загрузите фото", accept_multiple_files=True)
    if st.button("🗑 Очистить всё"):
        st.session_state.final_rows = []
        st.rerun()

# --- ОБРАБОТКА С КРОПОМ ---
if uploaded and len(uploaded) != len(st.session_state.final_rows):
    processed_data = []
    for f in uploaded:
        with st.spinner(f'Читаем нижнюю часть {f.name}...'):
            img_pill = preprocess_for_ocr(f.getvalue())
            w, h = img_pill.size
            
            # ТВОЙ КРОП: Нижние 40% (где серия и номер)
            cropped = img_pill.crop((0, h * 0.6, w, h)) 
            
            # OCR только на кропнутой части
            raw_text = reader.readtext(np.array(cropped), detail=0)
            data = parse_medical_book_text(" ".join(raw_text))
            data["Файл"] = f.name
            processed_data.append(data)
    st.session_state.final_rows = processed_data

# --- ИНТЕРФЕЙС ---
if st.session_state.final_rows:
    col_t, col_i = st.columns([1.2, 0.8])
    
    with col_i:
        sel = st.selectbox("Для проверки ФИО:", [r['Файл'] for r in st.session_state.final_rows])
        curr_f = next(f for f in uploaded if f.name == sel)
        st.image(curr_f, use_container_width=True) # Показываем целое фото для проверки ФИО

    with col_t:
        st.subheader("📝 Данные (Серия, Номер и Даты считаны автоматически)")
        df = pd.DataFrame(st.session_state.final_rows)
        
        # Названия колонок как в твоем образце
        df_display = df.rename(columns={
            "id": "ИД сотрудника", "fio": "ФИО (впишите вручную)", 
            "seriya": "Серия документа", "num_doc": "Номер документа",
            "date_osm": "Дата осмотра", "next_osm": "След. осмотр"
        })
        
        edited_df = st.data_editor(df_display, use_container_width=True, hide_index=True)
        
        # Сохранение в Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            edited_df.drop(columns=['Файл']).to_excel(writer, index=False)
        st.download_button("📥 Скачать Excel (11 колонок)", buffer.getvalue(), file_name="med_report.xlsx")
