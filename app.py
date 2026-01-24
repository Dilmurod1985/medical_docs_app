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
    # Добавляем поддержку узбекского и русского
    return easyocr.Reader(['ru', 'en'], gpu=False)

reader = load_ocr()

# Инициализируем список данных в памяти
if 'final_data' not in st.session_state:
    st.session_state.final_data = []

with st.sidebar:
    st.header("📂 Загрузка")
    uploaded_files = st.file_uploader("Загрузите фото", accept_multiple_files=True)
    if st.button("🗑 Очистить список"):
        st.session_state.final_data = []
        st.rerun()

# Если файлы загружены, а список пуст — запускаем распознавание для КАЖДОГО файла
if uploaded_files and len(st.session_state.final_data) == 0:
    for f in uploaded_files:
        with st.spinner(f'Обработка {f.name}...'):
            img_proc = preprocess_for_ocr(f.getvalue())
            raw_text = reader.readtext(np.array(img_proc), detail=0)
            data = parse_medical_book_text(" ".join(raw_text))
            
            # Добавляем результат в общий список
            st.session_state.final_data.append({
                "ИД сотрудника": data["id"],
                "ФИО": data["fio"],
                "Статус": data["status"],
                "Дата осмотра": data["date_osm"],
                "След. осмотр": data["next_osm"],
                "Серия": data["seriya"],
                "Номер док.": data["num_doc"],
                "Выдано": data["vidano"],
                "Файл": f.name  # Чтобы знать, какое фото смотреть
            })

# Отображение интерфейса
if st.session_state.final_data:
    col_edit, col_view = st.columns([1.3, 0.7])

    with col_view:
        st.subheader("🖼 Просмотр")
        file_to_show = st.selectbox("Какое фото проверить?", [d['Файл'] for d in st.session_state.final_data])
        # Показываем именно выбранный файл
        img_file = next(f for f in uploaded_files if f.name == file_to_show)
        st.image(img_file, use_container_width=True)

    with col_edit:
        st.subheader("📝 Исправьте ФИО и номера здесь")
        df = pd.DataFrame(st.session_state.final_data)
        # Редактируем таблицу напрямую
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
        
        # Кнопка Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Убираем колонку "Файл" перед сохранением
            edited_df.drop(columns=['Файл']).to_excel(writer, index=False)
        
        st.download_button("📥 Скачать готовый Excel", buffer.getvalue(), 
                           file_name="med_report.xlsx", 
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
