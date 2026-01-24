import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import io
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_med_doc

st.set_page_config(page_title="MedScan Pro", layout="wide")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ru', 'en'], gpu=False)

reader = load_ocr()

if 'final_data' not in st.session_state:
    st.session_state.final_data = []

with st.sidebar:
    st.header("📂 Загрузка")
    files = st.file_uploader("Загрузите фото", accept_multiple_files=True)
    if st.button("🔄 Сбросить всё"):
        st.session_state.clear()
        st.rerun()

if files and len(st.session_state.final_data) != len(files):
    results = []
    for f in files:
        with st.spinner(f'Обработка {f.name}...'):
            img = preprocess_for_ocr(f.getvalue())
            text_list = reader.readtext(np.array(img), detail=0)
            raw_text = " ".join(text_list)
            
            data = parse_med_doc(raw_text)
            data["Файл"] = f.name
            data["debug"] = raw_text # Для отладки
            results.append(data)
    st.session_state.final_data = results

if st.session_state.final_data:
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.subheader("📝 Таблица данных")
        df = pd.DataFrame(st.session_state.final_data)
        # Колонки для отображения
        cols = ["ИД сотрудника", "ФИО", "Статус", "Дата медосмотра", "След. медосмотр", "Серия", "Номер"]
        edited_df = st.data_editor(df[cols], use_container_width=True, hide_index=True)
        
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            edited_df.to_excel(writer, index=False)
        st.download_button("📥 Скачать Excel", buf.getvalue(), file_name="report.xlsx")

    with col2:
        st.subheader("👀 Проверка")
        names = [r['Файл'] for r in st.session_state.final_data]
        selected = st.selectbox("Выбери файл:", names, key="pic_select")
        
        # ТВОЙ БЕЗОПАСНЫЙ ФИКС
        curr_f = next((f for f in files if f.name == selected), None)
        if curr_f:
            st.image(curr_f, use_container_width=True)
            curr_row = next(r for r in st.session_state.final_data if r['Файл'] == selected)
            st.text_area("OCR увидел это:", curr_row["debug"], height=100)
