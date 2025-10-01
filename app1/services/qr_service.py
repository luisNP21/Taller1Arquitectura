import json
from .qr_reader import QRReader
from typing import Any, List
import numpy as np
from PIL import Image
import fitz  # PyMuPDF

class QRService:
    """Servicio de alto nivel que procesa archivos/páginas y usa un QRReader."""
    def __init__(self, reader: QRReader):
        self.reader = reader

    def process_image(self, image_or_bytes) -> Any:
        data = self.reader.decode(image_or_bytes)
        if not data:
            return None
        if isinstance(data, dict):
            return data  # por si en el futuro algún reader ya devuelve dict
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {"raw_data": data}

    def extract_payloads(self, archivo) -> List[dict]:
        """Extrae lista de payloads desde una imagen o PDF con QR"""


        payloads = []

        if isinstance(archivo, (bytes, bytearray)):
            try:
                img = Image.open(io.BytesIO(archivo)).convert("RGB")
                payload = self.process_image(np.array(img, dtype=np.uint8))
                if payload:
                    payloads.append(payload)
            except Exception as e:
                print(f"[extract_payloads] No se pudo abrir imagen desde bytes: {e}")
            return payloads

        # Caso: archivo Django UploadedFile o path
        if archivo.name.endswith(".pdf"):
            pdf = fitz.open(stream=archivo.read(), filetype="pdf")
            for page in pdf:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                payload = self.process_image(np.array(img, dtype=np.uint8))
                if payload:
                    payloads.append(payload)
        else:
            img = Image.open(archivo).convert("RGB")
            payload = self.process_image(np.array(img, dtype=np.uint8))
            if payload:
                payloads.append(payload)

        return payloads

