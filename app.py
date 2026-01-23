import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import sys
import os

# Добавляем пути, чтобы Python видел твои папки
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from ocr.ocr_engine import OCREngine
from parser.parser import MedicalDocumentParser
try:
    from exporter.exporter import ExcelExporter
except ImportError:
    from exporter import ExcelExporter

st.set_page_config(page_title="Система обработки медкнижек", layout="wide")

st.title("🏥 Автоматизация медосмотров (Дильмурат)")
st.write(f"Сегодняшняя дата: {pd.to_datetime('today').strftime('%d.%m.%Y')}")

# Инициализация сервисов
ocr_engine = OCREngine()
parser = MedicalDocumentParser()
exporter = ExcelExporter()

uploaded_files = st.file_uploader("Загрузите фото медкнижек", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if uploaded_files:
    results = []
    for uploaded_file in uploaded_files:
        with st.spinner(f'Обработка {uploaded_file.name}...'):
            try:
                # Читаем изображение
                image = Image.open(uploaded_file)
                img_array = np.array(image.convert('RGB'))
                
                # OCR + Парсинг
                ocr_data = ocr_engine.extract_text(img_array)
                parsed_data = parser.parse(ocr_data)
                
                results.append({
                    "Файл": uploaded_file.name,
                    "Дата осмотра": parsed_data.get('examination_date', 'Не найдено'),
                    "Следующий осмотр": parsed_data.get('next_visit_date', 'Не рассчитано')
                })
            except Exception as e:
                results.append({"Файл": uploaded_file.name, "Ошибка": str(e)})

    # Вывод таблицы
    df = pd.DataFrame(results)
    st.table(df)

    # Кнопка Excel
    if not df.empty:
        excel_data = exporter.export_to_excel(df)
        st.download_button(
            label="📥 Скачать отчет в Excel",
            data=excel_data,
            file_name=f"med_osmotr_{pd.to_datetime('today').strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

