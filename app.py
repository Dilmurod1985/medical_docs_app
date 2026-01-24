import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import io
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text

st.set_page_config(page_title="Medical Scanner", layout="wide")

@st.cache_resource
def load_ocr():
    # Оставляем только стабильные языки, чтобы не было ошибок как на скриншоте
    return easyocr.Reader(['ru', 'en'], gpu=False)

reader = load_ocr()

# Инициализируем хранилище данных
if 'table_rows' not in st.session_state:
    st.session_state.table_rows = []

with st.sidebar:
    st.header("📂 Загрузка документов")
    uploaded_files = st.file_uploader("Выберите фото медкнижек", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    
    if st.button("🗑 Очистить таблицу"):
        st.session_state.table_rows = []
        st.rerun()

# ГЛАВНАЯ ЛОГИКА: Обработка каждого файла
if uploaded_files:
    # Проверяем, нужно ли запускать распознавание
    if len(uploaded_files) != len(st.session_state.table_rows):
        new_rows = []
        for f in uploaded_files:
            with st.spinner(f'Обработка файла {f.name}...'):
                # 1. Подготовка картинки
                img_proc = preprocess_for_ocr(f.getvalue())
                # 2. Распознавание текста
                raw_text = reader.readtext(np.array(img_proc), detail=0)
                # 3. Разбор текста через наш парсер
                data = parse_medical_book_text(" ".join(raw_text))
                
                # Добавляем данные в список
                new_rows.append({
                    "ИД сотрудника": data["id"],
                    "ФИО": data["fio"],
                    "Статус": data["status"],
                    "Дата осмотра": data["date_osm"],
                    "След. осмотр": data["next_osm"],
                    "Серия": data["seriya"],
                    "Номер док.": data["num_doc"],
                    "Выдано": data["vidano"],
                    "Файл": f.name
                })
        st.session_state.table_rows = new_rows

# ИНТЕРФЕЙС
if st.session_state.table_rows:
    col_edit, col_view = st.columns([1.2, 0.8])

    with col_view:
        st.subheader("🖼 Просмотр оригинала")
        # Список имен файлов для выбора
        f_names = [r['Файл'] for r in st.session_state.table_rows]
        selected_name = st.selectbox("Выберите файл:", f_names)
        
        # Находим и показываем выбранное фото
        orig_file = next(f for f in uploaded_files if f.name == selected_name)
        st.image(orig_file, use_container_width=True)

    with col_edit:
        st.subheader("📝 Редактор данных")
        # Создаем DataFrame из памяти приложения
        df = pd.DataFrame(st.session_state.table_rows)
        
        # РЕДАКТОР: здесь ты правишь ФИО и Номера
        # Используем key, чтобы правки не слетали
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True, key="data_editor_v3")
        
        # Обновляем память приложения после правок
        st.session_state.table_rows = edited_df.to_dict('records')

        # ЭКСПОРТ В EXCEL
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Убираем техническую колонку "Файл" перед сохранением
            edited_df.drop(columns=['Файл']).to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Скачать полный Excel отчет",
            data=buffer.getvalue(),
            file_name="med_report_fixed.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
