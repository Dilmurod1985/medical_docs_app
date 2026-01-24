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

# Инициализация памяти приложения
if 'data_list' not in st.session_state:
    st.session_state.data_list = []

with st.sidebar:
    st.header("📂 Загрузка")
    uploaded_files = st.file_uploader("Загрузите страницы медкнижек", accept_multiple_files=True)
    if st.button("🔄 Очистить всё"):
        st.session_state.data_list = []
        st.rerun()

# Если файлы загружены и память пуста — обрабатываем
if uploaded_files and not st.session_state.data_list:
    temp_list = []
    for f in uploaded_files:
        with st.spinner(f'Анализ {f.name}...'):
            img_proc = preprocess_for_ocr(f.getvalue())
            raw_text = reader.readtext(np.array(img_proc), detail=0)
            data = parse_medical_book_text(" ".join(raw_text))
            temp_list.append({
                "ИД сотрудника": data["id"],
                "ФИО": data["fio"],
                "Статус": data["status"],
                "Дата осмотра": data["date_osm"],
                "След. осмотр": data["next_osm"],
                "Серия": data["seriya"],
                "Номер док.": data["num_doc"],
                "Выдано": data["vidano"],
                "Дата выдачи": data["date_vidano"],
                "Файл": f.name
            })
    st.session_state.data_list = temp_list

# Основной интерфейс
if st.session_state.data_list:
    col_table, col_img = st.columns([1.2, 0.8])

    with col_img:
        st.subheader("🖼 Оригинал")
        file_names = [d['Файл'] for d in st.session_state.data_list]
        selected = st.selectbox("Выберите фото для проверки ФИО:", file_names)
        # Находим файл в загруженных
        curr_file = next(f for f in uploaded_files if f.name == selected)
        st.image(curr_file, use_container_width=True)

    with col_table:
        st.subheader("📝 Редактор (измените ФИО здесь)")
        # Отображаем таблицу из памяти
        df = pd.DataFrame(st.session_state.data_list)
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True, key="main_editor")
        
        # Кнопка скачивания
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            edited_df.drop(columns=['Файл']).to_excel(writer, index=False)
        
        st.download_button("📥 Скачать Excel (все сотрудники)", buffer.getvalue(), 
                           file_name="result.xlsx", 
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
