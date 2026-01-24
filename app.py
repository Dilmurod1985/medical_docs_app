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

if 'final_data' not in st.session_state:
    st.session_state.final_data = []

with st.sidebar:
    st.header("📂 Загрузка")
    uploaded_files = st.file_uploader("Загрузите медкнижки", accept_multiple_files=True)
    if st.button("🗑 Очистить всё"):
        st.session_state.final_data = []
        st.rerun()

if uploaded_files and len(st.session_state.final_data) != len(uploaded_files):
    results = []
    for f in uploaded_files:
        with st.spinner(f'Обработка {f.name}...'):
            img_processed = preprocess_for_ocr(f.getvalue())
            raw_text = reader.readtext(np.array(img_processed), detail=0)
            data = parse_medical_book_text(" ".join(raw_text))
            data["Файл"] = f.name
            results.append(data)
    st.session_state.final_data = results

if st.session_state.final_data:
    col_table, col_view = st.columns([1.2, 0.8])
    
    with col_view:
        st.subheader("👀 Твой выбор фото")
        selected = st.selectbox("Какой файл смотрим?", [r['Файл'] for r in st.session_state.final_data])
        # Показываем ОРИГИНАЛ (не кроп), чтобы видеть ФИО
        original = next(f for f in uploaded_files if f.name == selected)
        st.image(original, use_container_width=True)

    with col_table:
        st.subheader("📝 Итоговая таблица")
        df = pd.DataFrame(st.session_state.final_data)
        # Переименуем для красоты
        df_edit = df.rename(columns={
            "id": "ИД", "fio": "ФИО", "seriya": "Серия", "num_doc": "Номер", "date_osm": "Дата осмотра"
        })
        edited_df = st.data_editor(df_edit, use_container_width=True, hide_index=True)
        
        # Скачать Excel
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            edited_df.drop(columns=['Файл']).to_excel(writer, index=False)
        st.download_button("📥 Скачать Excel", buf.getvalue(), file_name="report.xlsx")
