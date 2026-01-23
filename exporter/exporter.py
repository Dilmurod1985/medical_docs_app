import pandas as pd
from typing import List, Dict, Any
import os
from datetime import datetime

class ExcelExporter:
    def __init__(self):
        """
        Инициализация экспортера в Excel
        """
        pass
    
    def export_to_excel(self, data: List[Dict], output_path: str, sheet_name: str = 'Medical_Data') -> bool:
        try:
            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False, sheet_name=sheet_name)
            return True
        except Exception:
            return False
    
    def export_medical_documents(self, medical_data: List[Dict], output_path: str) -> bool:
        return self.export_to_excel(medical_data, output_path)
    
    def create_summary_report(self, medical_data: List[Dict], output_path: str) -> bool:
        return self.export_to_excel(medical_data, output_path, sheet_name='Summary')
