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

if 'data_rows' not in st.session_state:
    st.session_state.data_rows = []

with st.sidebar:
    st.header("📂 Загрузка")
    files = st.file_uploader("Загрузите фото", accept_multiple_files=True)
    if st.button("🔄 Сброс"):
        st.session_state.data_rows = []
        st.rerun()

# Обработка
if files and len(files) != len(st.session_state.data_rows):
    results = []
    for f in files:
        with st.spinner(f'Читаем {f.name}...'):
            img = preprocess_for_ocr(f.getvalue())
            text = reader.readtext(np.array(img), detail=0)
            parsed = parse_medical_book_text(" ".join(text))
            parsed["Файл"] = f.name
            results.append(parsed)
    st.session_state.data_rows = results

# Интерфейс
if st.session_state.data_rows:
    col_t, col_i = st.columns([1.3, 0.7])
    
    with col_i:
        sel = st.selectbox("Показать фото:", [r['Файл'] for r in st.session_state.data_rows])
        img_file = next(f for f in files if f.name == sel)
        st.image(img_file, use_container_width=True)

    with col_t:
        df = pd.DataFrame(st.session_state.data_rows)
        # Названия как в твоем Excel
        df_edit = df.rename(columns={
            "id": "ИД сотрудника", "fio": "ФИО", "seriya": "Серия", 
            "num_doc": "Номер документа", "date_osm": "Дата осмотра"
        })
        
        # Редактируем
        final_df = st.data_editor(df_edit, use_container_width=True, hide_index=True)
        
        # Кнопка Excel
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            final_df.drop(columns=['Файл']).to_excel(writer, index=False)
        st.download_button("📥 Скачать Excel", buf.getvalue(), file_name="report.xlsx")
