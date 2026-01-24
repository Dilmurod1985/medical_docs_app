import streamlit as st
import pandas as pd
from PIL import Image
import io

# Импорты модулей
from utils.image_preprocessing import preprocess_image
from ocr.ocr_engine import get_ocr_reader, extract_text_from_image
from parser.parser import parse_medical_text
from exporter.excel_exporter import ExcelExporter

st.set_page_config(
    page_title="Система обработки медкнижек",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Система обработки медицинских книжек")

st.markdown("""
Загружайте фото страниц медкнижки (jpg, jpeg, png).  
Система извлечёт текст, распарсит данные и подготовит таблицу + Excel.
""")

uploaded_files = st.file_uploader(
    "Загрузите страницы медкнижки",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

results = []

if uploaded_files:
    progress_bar = st.progress(0)
    status_text = st.empty()

    results = []

    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Обработка {idx+1}/{len(uploaded_files)}: {uploaded_file.name}")

        try:
            bytes_data = uploaded_file.getvalue()
            processed_img = preprocess_image(bytes_data)
            reader = get_ocr_reader()
            raw_text = extract_text_from_image(reader, processed_img)

            # Отладка — сразу видно, что OCR вернул
            st.write(f"Текст из файла {uploaded_file.name}:")
            st.text_area("Извлечённый текст", raw_text, height=150, key=f"ocr_text_{idx}")

            parsed_data = parse_medical_text(raw_text)
            parsed_data["Файл"] = uploaded_file.name
            results.append(parsed_data)

        except Exception as e:
            st.error(f"Ошибка при обработке {uploaded_file.name}: {str(e)}")
            continue

        progress_bar.progress((idx + 1) / len(uploaded_files))

    status_text.text("Обработка завершена!")

    if results:
        df = pd.DataFrame(results)
        st.subheader("Результаты обработки")
        st.dataframe(df)

        exporter = ExcelExporter()
        excel_data = exporter.export_to_excel(df)

        st.download_button(
            label="Скачать Excel отчёт",
            data=excel_data,
            file_name="медкнижки_отчёт.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Не удалось обработать ни один файл — проверьте фото")
else:
    st.info("Загрузите хотя бы одно фото для начала работы")
