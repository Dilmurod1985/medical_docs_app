import easyocr

def get_ocr_reader():
    """Создаёт и возвращает читатель EasyOCR (лениво, один раз)"""
    if 'reader' not in st.session_state:
        st.session_state.reader = easyocr.Reader(['ru', 'uz', 'en'], gpu=False)
    return st.session_state.reader


def extract_text_from_image(reader, pil_image):
    """Извлекает текст из PIL изображения"""
    result = reader.readtext(np.array(pil_image), detail=0, paragraph=True)
    return " ".join(result)
