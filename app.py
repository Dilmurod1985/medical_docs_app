import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import io
from PIL import Image
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text

st.set_page_config(page_title="MedScan Pro", layout="wide")
st.title("🏥 Умный сканер: Проверка и редактирование")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ru', 'en'], gpu=False)

reader = load_ocr()

# Интерфейс загрузки
files = st.file_uploader("Загрузите сразу несколько страниц медкнижки", accept_multiple_files=True)

if files:
    all_data = []
    # Сохраняем файлы в словарь для быстрого переключения
    file_map = {f.name: f for f in files}
    
    # Обработка всех файлов (результаты кэшируются Streamlit)
    for f in files:
        with st.spinner(f'Читаем {f.name}...'):
            try:
                img_proc = preprocess_for_ocr(f.getvalue())
                raw_text = reader.readtext(np.array(img_proc), detail=0)
                # Передаем текст в наш парсер
                data = parse_medical_book_text(" ".join(raw_text))
                
                all_data.append({
                    "Файл": f.name,
                    "ИД сотрудника": data["id"],
                    "ФИО (проверьте по фото)": data["fio"],
                    "Дата осмотра": data["date"],
                    "След. осмотр": data["next"],
                    "Номер документа": data["num_doc"]
                })
            except Exception as e:
                st.error(f"Ошибка в {f.name}: {e}")

    # Создаем два столбца для удобной проверки
    col_table, col_img = st.columns([1.2, 0.8])

    with col_img:
        st.subheader("🖼 Оригинал для проверки")
        # Переключатель между загруженными фото
        selected_file = st.selectbox("Выберите файл для просмотра:", [f.name for f in files])
        if selected_file:
            st.image(file_map[selected_file], use_container_width=True, caption=f"Текущий файл: {selected_file}")

    with col_table:
        st.subheader("📝 Данные для Excel")
        # Редактируемая таблица
        df = pd.DataFrame(all_data)
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
        
        # Генерация Excel в формате твоего образца
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            edited_df.to_excel(writer, index=False, sheet_name='Медосмотры')
        
        st.download_button(
            label="📥 Скачать итоговый Excel",
            data=buffer.getvalue(),
            file_name="med_report_final.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
