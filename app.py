import streamlit as st
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from io import BytesIO
import tempfile

# Добавляем корневую директорию проекта в sys.path
sys.path.append(str(Path(__file__).parent))

from utils.image_preprocessing import preprocess_image
from ocr.ocr_engine import OCREngine
from parser.parser import MedicalDocumentParser
from exporter.exporter import ExcelExporter

# Настройка страницы
st.set_page_config(
    page_title="Система обработки медкнижек",
    page_icon="🏥",
    layout="wide"
)

# Заголовок приложения
st.title("🏥 Система обработки медкнижек")
st.markdown("---")

# Инициализация компонентов в session_state
if 'ocr_engine' not in st.session_state:
    st.session_state.ocr_engine = OCREngine()
    st.session_state.parser = MedicalDocumentParser()
    st.session_state.exporter = ExcelExporter()
    st.session_state.processed_results = []

def process_uploaded_files(uploaded_files) -> List[Dict]:
    """
    Обрабатывает загруженные файлы
    
    Args:
        uploaded_files: Список загруженных файлов
        
    Returns:
        List[Dict]: Результаты обработки
    """
    results = []
    
    for uploaded_file in uploaded_files:
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            
            # Обрабатываем изображение
            processed_image = preprocess_image(tmp_file_path)
            
            # OCR распознавание
            extracted_text = st.session_state.ocr_engine.extract_text_only(processed_image)
            
            # Парсинг данных
            parsed_data = st.session_state.parser.parse_medical_document(extracted_text)
            patient_info = st.session_state.parser.extract_patient_info(extracted_text)
            
            # Формируем результат
            result = {
                'filename': uploaded_file.name,
                'extracted_text': extracted_text,
                'parsed_data': parsed_data,
                'patient_info': patient_info,
                'success': True
            }
            
            results.append(result)
            
            # Удаляем временный файл
            os.unlink(tmp_file_path)
            
        except Exception as e:
            results.append({
                'filename': uploaded_file.name,
                'error': str(e),
                'success': False
            })
    
    return results

def create_results_dataframe(results: List[Dict]) -> pd.DataFrame:
    """
    Создает DataFrame для отображения результатов
    
    Args:
        results: Результаты обработки
        
    Returns:
        pd.DataFrame: Таблица с результатами
    """
    table_data = []
    
    for result in results:
        if result.get('success', False):
            patient_info = result.get('patient_info', {})
            parsed_data = result.get('parsed_data', {})
            
            # Получаем информацию о пациенте
            name = patient_info.get('name', 'Не найдено')
            birth_date = patient_info.get('birth_date', 'Не найдено')
            age = patient_info.get('age', 'Не найдено')
            
            # Получаем даты осмотров
            exam_dates = parsed_data.get('exam_dates', [])
            next_exam_dates = parsed_data.get('next_exam_dates', [])
            
            if exam_dates:
                # Создаем записи для каждой даты осмотра
                for i, exam_date in enumerate(exam_dates):
                    next_date = next_exam_dates[i] if i < len(next_exam_dates) else 'Не рассчитано'
                    
                    table_data.append({
                        'Файл': result['filename'],
                        'ФИО': name,
                        'Дата рождения': birth_date,
                        'Возраст': age,
                        'Дата осмотра': exam_date,
                        'Следующий осмотр (+6 мес)': next_date
                    })
            else:
                # Если дат нет, все равно добавляем запись
                table_data.append({
                    'Файл': result['filename'],
                    'ФИО': name,
                    'Дата рождения': birth_date,
                    'Возраст': age,
                    'Дата осмотра': 'Не найдено',
                    'Следующий осмотр (+6 мес)': 'Не рассчитано'
                })
        else:
            # Если обработка не удалась
            table_data.append({
                'Файл': result['filename'],
                'ФИО': 'Ошибка обработки',
                'Дата рождения': '',
                'Возраст': '',
                'Дата осмотра': '',
                'Следующий осмотр (+6 мес)': f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"
            })
    
    return pd.DataFrame(table_data)

def create_excel_download(results: List[Dict]) -> BytesIO:
    """
    Создает Excel файл для скачивания
    
    Args:
        results: Результаты обработки
        
    Returns:
        BytesIO: Excel файл в памяти
    """
    # Используем наш экспортер для создания данных
    export_data = []
    
    for i, doc_data in enumerate(results, 1):
        # Базовая информация о документе
        base_info = {
            'document_id': i,
            'filename': doc_data.get('filename', f'document_{i}'),
            'processing_date': pd.Timestamp.now().strftime('%d.%m.%Y %H:%M:%S')
        }
        
        # Информация о пациенте
        patient_info = doc_data.get('patient_info', {})
        patient_data = {
            'patient_name': patient_info.get('name', ''),
            'birth_date': patient_info.get('birth_date', ''),
            'age': patient_info.get('age', '')
        }
        
        # Даты осмотров
        parsed_data = doc_data.get('parsed_data', {})
        exam_dates = parsed_data.get('exam_dates', [])
        next_exam_dates = parsed_data.get('next_exam_dates', [])
        
        # Создаем записи для каждой даты осмотра
        if exam_dates:
            for j, exam_date in enumerate(exam_dates):
                row_data = {
                    **base_info,
                    **patient_data,
                    'exam_date': exam_date,
                    'next_exam_date': next_exam_dates[j] if j < len(next_exam_dates) else '',
                    'exam_number': j + 1
                }
                export_data.append(row_data)
        else:
            # Если дат нет, все равно создаем запись
            row_data = {
                **base_info,
                **patient_data,
                'exam_date': '',
                'next_exam_date': '',
                'exam_number': 0
            }
            export_data.append(row_data)
    
    # Создаем DataFrame и сохраняем в Excel
    df = pd.DataFrame(export_data)
    
    # Создаем Excel файл в памяти
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Medical_Examinations', index=False)
    
    output.seek(0)
    return output

# Боковая панель с информацией
with st.sidebar:
    st.header("ℹ️ Информация")
    st.markdown("""
    **Система позволяет:**
    - Загружать медицинские документы
    - Распознавать текст с помощью OCR
    - Извлекать даты осмотров
    - Рассчитывать даты следующих осмотров (+6 месяцев)
    - Экспортировать результаты в Excel
    """)
    
    st.markdown("---")
    st.markdown("**Поддерживаемые форматы:**")
    st.markdown("• JPG, JPEG, PNG, BMP, TIFF")

# Основная часть интерфейса
st.header("📤 Загрузка документов")

# Виджет для загрузки файлов
uploaded_files = st.file_uploader(
    "Выберите изображения медицинских документов:",
    type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif'],
    accept_multiple_files=True,
    help="Загрузите одно или несколько изображений для обработки"
)

if uploaded_files:
    st.success(f"Загружено файлов: {len(uploaded_files)}")
    
    # Отображаем загруженные файлы
    st.subheader("📋 Загруженные файлы:")
    for i, file in enumerate(uploaded_files, 1):
        st.write(f"{i}. {file.name}")
    
    # Кнопка начала обработки
    if st.button("🚀 Начать обработку", type="primary"):
        with st.spinner("⏳ Обработка файлов... Это может занять несколько минут."):
            # Обрабатываем файлы
            results = process_uploaded_files(uploaded_files)
            st.session_state.processed_results = results
            
        st.success("✅ Обработка завершена!")
        
        # Отображаем результаты
        st.markdown("---")
        st.header("📊 Результаты обработки")
        
        # Создаем и отображаем таблицу
        df_results = create_results_dataframe(results)
        
        if not df_results.empty:
            st.dataframe(
                df_results,
                use_container_width=True,
                hide_index=True
            )
            
            # Кнопка скачивания Excel
            st.markdown("---")
            st.subheader("💾 Экспорт результатов")
            
            excel_file = create_excel_download(results)
            
            st.download_button(
                label="📥 Скачать Excel файл",
                data=excel_file,
                file_name=f"medical_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ Нет данных для отображения")

# Информация о системе
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🏥 Система обработки медкнижек v1.0 | Powered by OCR & AI"
    "</div>",
    unsafe_allow_html=True
)


