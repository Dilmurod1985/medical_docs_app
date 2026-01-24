import streamlit as st
import pandas as pd
import numpy as np
import easyocr
from PIL import Image
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text
from exporter.exporter import ExcelExporter

# Настройка страницы
st.set_page_config(page_title="Medical Scanner", layout="wide")
st.title("🏥 Автоматизация медосмотров")

# Загрузка модели OCR (кэшируем, чтобы не грузить каждый раз)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['ru', 'uz'])

reader = load_reader()
exporter = ExcelExporter()

# Загрузка файлов
files = st.file_uploader("Загрузите фото документов", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

if files:
    all_data = []
    for f in files:
        with st.spinner(f'Обработка {f.name}...'):
            try:
                # 1. Получаем байты и делаем предобработку
                img_bytes = f.getvalue()
                processed_img = preprocess_for_ocr(img_bytes)
                
                # 2. Распознавание текста (OCR)
                # Конвертируем PIL Image в numpy массив для EasyOCR
                img_array = np.array(processed_img)
                text_list = reader.readtext(img_array, detail=0)
                full_text = " ".join(text_list)
                
                # 3. Извлечение данных (Парсинг)
                data = parse_medical_book_text(full_text)
                
                # Сохраняем результат
                all_data.append({
                    "ИД сотрудника": data["id"],
                    "ФИО": data["fio"],
                    "Статус": data["status"],
                    "Дата осмотра": data["date"],
                    "Следующий осмотр": data["next"],
                    "Файл": f.name
                })
            except Exception as e:
                st.error(f"Ошибка при обработке {f.name}: {e}")

    # Если есть данные — выводим таблицу и кнопку Excel
    if all_data:
        df = pd.DataFrame(all_data)
        st.success("Все файлы успешно обработаны!")
        st.table(df)
        
        # Экспорт в Excel
        try:
            xlsx_output = exporter.export_to_excel(df)
            st.download_button(
                label="📥 Скачать отчет в Excel",
                data=xlsx_output,
                file_name="medical_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.warning(f"Ошибка при создании Excel: {e}")
