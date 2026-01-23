import streamlit as st
from PIL import Image
import io
import pandas as pd

# Импортируем свои модули
from utils.image_preprocessing import preprocess_image
from ocr.ocr_engine import get_ocr_reader, extract_text_from_image
from parser.medical_parser import parse_medical_text
from exporter.excel_exporter import create_excel_file

st.set_page_config(
    page_title="Система обработки медкнижек",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Система обработки медицинских книжек")

st.markdown("""
Загружайте фото страниц медкнижки. Система извлечёт данные и подготовит таблицу для скачивания в Excel.
""")

# Загрузка файлов
uploaded_files = st.file_uploader(
    "Загрузите страницы медкнижки (jpg, png)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

results = []

if uploaded_files:
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Обработка файла {idx+1}/{len(uploaded_files)}: {uploaded_file.name}")

        try:
            # Читаем байты
            bytes_data = uploaded_file.getvalue()

            # Предобработка
            processed_img = preprocess_image(bytes_data)

            # OCR
            reader = get_ocr_reader()
            raw_text = extract_text_from_image(reader, processed_img)

            # Парсинг
            parsed_data = parse_medical_text(raw_text)

            # Добавляем имя файла для удобства
            parsed_data["Файл"] = uploaded_file.name

            results.append(parsed_data)

        except Exception as e:
            st.error(f"Ошибка обработки {uploaded_file.name}: {str(e)}")
            continue

        progress_bar.progress((idx + 1) / len(uploaded_files))

    status_text.text("Обработка завершена!")

    if results:
        # Показываем таблицу
        df = pd.DataFrame(results)
        st.subheader("Результаты")
        st.dataframe(df)

        # Скачивание Excel
        excel_data = create_excel_file(df)
        st.download_button(
            label="Скачать Excel отчет",
            data=excel_data,
            file_name="medical_books_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
