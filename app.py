import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import io
from PIL import Image

# Импортируем твои модули
from utils.image_preprocessing import preprocess_for_ocr
from parser.parser import parse_medical_book_text

st.set_page_config(page_title="Medical Scanner", layout="wide")
st.title("🏥 Система медосмотров")

# Загрузка OCR
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ru', 'uz'])

reader = load_ocr()

files = st.file_uploader("Загрузите фото", accept_multiple_files=True)

if files:
    all_data = []
    for f in files:
        with st.spinner(f'Читаем {f.name}...'):
            try:
                img_proc = preprocess_for_ocr(f.getvalue())
                raw_text = reader.readtext(np.array(img_proc), detail=0)
                full_text = " ".join(raw_text)
                data = parse_medical_book_text(full_text)
                
                all_data.append({
                    "ИД сотрудника": data["id"],
                    "ФИО": data["fio"],
                    "Статус": data["status"],
                    "Дата осмотра": data["date"],
                    "Следующий осмотр": data["next"]
                })
            except Exception as e:
                st.error(f"Ошибка в {f.name}: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        st.table(df)
        
        # Простой экспорт в Excel без внешних файлов exporter
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        st.download_button(
            label="📥 Скачать Excel",
            data=buffer.getvalue(),
            file_name="report.xlsx",
            mime="application/vnd.ms-excel"
        )
