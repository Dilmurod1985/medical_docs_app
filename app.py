import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import io
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text

st.set_page_config(page_title="MedScan Pro", layout="wide")
st.title("🏥 Полный отчет по медкнижкам")

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ru', 'en'], gpu=False)

reader = load_ocr()

files = st.file_uploader("Загрузите фото", accept_multiple_files=True)

if files:
    all_data = []
    file_map = {f.name: f for f in files}
    
    for f in files:
        with st.spinner(f'Обработка {f.name}...'):
            try:
                img_proc = preprocess_for_ocr(f.getvalue())
                raw_text = reader.readtext(np.array(img_proc), detail=0)
                data = parse_medical_book_text(" ".join(raw_text))
                
                # Формируем строку точно по твоим пунктам
                all_data.append({
                    "ИД сотрудника": data["id"],
                    "ФИО": data["fio"],
                    "Статус медосмотра годен/не годен": data["status"],
                    "Дата медосмотра": data["date_osm"],
                    "След. Дата медосмотра": data["next_osm"],
                    "Серия документа": data["seriya"],
                    "Номер документа": data["num_doc"],
                    "Выдано": data["vidano"],
                    "Дата выдачи": data["date_vidano"],
                    "Дата начала действия": data["date_start"],
                    "Дата истечения": data["date_end"],
                    "Имя файла": f.name
                })
            except Exception as e:
                st.error(f"Ошибка в {f.name}: {e}")

    if all_data:
        col_t, col_i = st.columns([1.2, 0.8])
        
        with col_i:
            sel = st.selectbox("Оригинал для проверки ФИО:", [f.name for f in files])
            st.image(file_map[sel], use_container_width=True)

        with col_t:
            st.subheader("📝 Редактирование всех пунктов")
            df = pd.DataFrame(all_data)
            # Теперь здесь все 11 колонок!
            edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Удаляем колонку "Имя файла" перед сохранением в Excel
                edited_df.drop(columns=['Имя файла']).to_excel(writer, index=False)
            
            st.download_button("📥 Скачать полный Excel (11 колонок)", buffer.getvalue(), 
                               file_name="med_report_full.xlsx", 
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
