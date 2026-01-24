import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import io
from PIL import Image
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text

st.set_page_config(page_title="MedScan Pro", layout="wide")
st.title("🏥 Умный конвертер медкнижек")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ru', 'en'], gpu=False)

reader = load_ocr()

# Создаем боковую панель для загрузки, чтобы освободить место
with st.sidebar:
    st.header("📂 Загрузка")
    files = st.file_uploader("Загрузите фото документов", accept_multiple_files=True)

if files:
    all_data = []
    # Словарь для хранения загруженных картинок, чтобы быстро переключаться
    images_dict = {f.name: f for f in files}
    
    # Обработка всех файлов
    for f in files:
        # Мы не пересчитываем OCR каждый раз при клике, Streamlit кэширует результаты
        with st.spinner(f'Распознаем {f.name}...'):
            try:
                img_proc = preprocess_for_ocr(f.getvalue())
                raw_text = reader.readtext(np.array(img_proc), detail=0)
                data = parse_medical_book_text(" ".join(raw_text))
                
                all_data.append({
                    "Файл": f.name,
                    "ИД сотрудника": data["id"],
                    "ФИО (впишите вручную)": data["fio"],
                    "Дата медосмотра": data["date"],
                    "След. медосмотр": data["next"],
                    "Серия": data["seriya"],
                    "Номер док.": data["num_doc"]
                })
            except Exception as e:
                st.error(f"Ошибка в {f.name}: {e}")

    # Основной интерфейс: два столбца
    col_table, col_img = st.columns([1, 1])

    with col_img:
        st.subheader("🖼 Просмотр оригинала")
        # Кнопка переключения между фото
        selected_filename = st.selectbox("Выберите файл для проверки почерка:", [f.name for f in files])
        if selected_filename:
            st.image(images_dict[selected_filename], use_container_width=True)

    with col_table:
        st.subheader("📝 Редактор данных")
        df = pd.DataFrame(all_data)
        # Редактируемая таблица
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
        
        # Кнопка Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            edited_df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Скачать готовый Excel",
            data=buffer.getvalue(),
            file_name="med_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
