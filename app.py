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

if 'final_rows' not in st.session_state:
    st.session_state.final_rows = []

with st.sidebar:
    st.header("📂 Загрузка")
    uploaded = st.file_uploader("Загрузите фото", accept_multiple_files=True)
    if st.button("🗑 Очистить всё"):
        st.session_state.final_rows = []
        st.rerun()

if uploaded and len(uploaded) != len(st.session_state.final_rows):
    processed_data = []
    for f in uploaded:
        with st.spinner(f'Обработка {f.name}...'):
            img_pill = preprocess_for_ocr(f.getvalue())
            raw_text_list = reader.readtext(np.array(img_pill), detail=0)
            raw_text_full = " ".join(raw_text_list)
            
            # ОКНО ОТЛАДКИ (как ты и просил)
            st.text_area(f"Текст OCR ({f.name})", raw_text_full, height=100)
            
            data = parse_medical_book_text(raw_text_full)
            data["Файл"] = f.name
            processed_data.append(data)
    st.session_state.final_rows = processed_data

# ИНТЕРФЕЙС ТАБЛИЦЫ И ПРОСМОТРА
if st.session_state.final_rows:
    col_t, col_i = st.columns([1.2, 0.8])
    with col_i:
        sel = st.selectbox("Выбор фото:", [r['Файл'] for r in st.session_state.final_rows])
        curr_f = next(f for f in uploaded if f.name == sel)
        st.image(curr_f, use_container_width=True)
    with col_t:
        df = pd.DataFrame(st.session_state.final_rows)
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
        
        # EXCEL
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            edited_df.drop(columns=['Файл']).to_excel(writer, index=False)
        st.download_button("📥 Скачать Excel", buf.getvalue(), file_name="med_report.xlsx")
