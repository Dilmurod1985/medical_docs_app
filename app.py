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

# Инициализация состояния
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = []

with st.sidebar:
    st.header("📂 Загрузка")
    uploaded_files = st.file_uploader("Загрузите медкнижки", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    
    if st.button("🔄 Очистить всё"):
        st.session_state.clear() # Полная очистка, чтобы убрать кэш селектора
        st.rerun()

# Основная логика обработки
if uploaded_files:
    # Если количество файлов изменилось — запускаем парсинг заново
    if len(uploaded_files) != len(st.session_state.processed_data):
        results = []
        for f in uploaded_files:
            with st.spinner(f'Обработка {f.name}...'):
                # 1. Твоя новая крутая предобработка (CLAHE + Crop)
                img_processed = preprocess_for_ocr(f.getvalue())
                
                # 2. OCR
                raw_text_list = reader.readtext(np.array(img_processed), detail=0)
                full_raw_text = " ".join(raw_text_list)
                
                # 3. Парсинг твоими новыми Regex (MT, 069510 и т.д.)
                data = parse_medical_book_text(full_raw_text)
                
                # Сохраняем и сырой текст для отладки, и имя файла
                data["raw_debug_text"] = full_raw_text
                data["Файл"] = f.name
                results.append(data)
        st.session_state.processed_data = results

# ИНТЕРФЕЙС
if st.session_state.processed_data:
    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.subheader("📝 Итоговые данные")
        df = pd.DataFrame(st.session_state.processed_data)
        
        # Убираем технические колонки из отображения, но оставляем для логики
        display_cols = ["ИД сотрудника", "ФИО", "Статус", "Дата медосмотра", "След. медосмотр", "Серия", "Номер"]
        edited_df = st.data_editor(df[display_cols], use_container_width=True, hide_index=True)
        
        # Кнопка скачивания Excel
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            edited_df.to_excel(writer, index=False)
        st.download_button("📥 Скачать Excel", buf.getvalue(), file_name="med_report.xlsx")

    with col2:
        st.subheader("👀 Проверка фото")
        file_names = [f['Файл'] for f in st.session_state.processed_data]
        selected_file = st.selectbox("Какой файл смотрим?", file_names, key="photo_selector")

        # ТВОЙ ФИКС: Безопасный поиск файла (не падает в StopIteration)
        curr_f = next((f for f in uploaded_files if f.name == selected_file), None)

        if curr_f:
            st.image(curr_f, caption=f"Просмотр: {selected_file}", use_container_width=True)
            
            # ВЫВОД ОТЛАДКИ: смотрим, что увидел OCR именно для этого фото
            current_row = next(r for r in st.session_state.processed_data if r['Файл'] == selected_file)
            st.info("🔍 Что увидел ИИ в нижней части фото:")
            st.text_area("Сырой текст OCR", current_row["raw_debug_text"], height=150)
        else:
            st.warning("Фото не найдено. Попробуйте перевыбрать.")
