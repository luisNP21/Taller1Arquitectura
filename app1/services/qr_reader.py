# app1/services/qr_reader.py
from __future__ import annotations

import io
import json
import re
from dataclasses import dataclass
from typing import Iterable, List, Dict, Any

import fitz  # PyMuPDF
import cv2
import numpy as np


@dataclass(frozen=True)
class QRPayload:
    """Estructura tipada para los datos que esperamos en el QR."""
    id: int | None
    referencia: str | None
    modelo: str | None
    talla: str | int | None
    sexo: str | None
    color: str | None

    @classmethod
    def from_json(cls, raw: str) -> "QRPayload | None":
        try:
            # Limpieza de caracteres extraños y parseo
            clean = re.sub(r'[^\x20-\x7E]+', '', raw.strip())
            data = json.loads(clean)
            return cls(
                id=data.get("id"),
                referencia=data.get("referencia"),
                modelo=data.get("modelo"),
                talla=data.get("talla"),
                sexo=data.get("sexo"),
                color=data.get("color"),
            )
        except Exception:
            return None


class ImageAdapter:
    """
    ADAPTER: convierte distintas fuentes (PDF/imágenes) a arrays BGR (np.ndarray)
    compatibles con OpenCV.
    """

    @staticmethod
    def pdf_bytes_to_images_bgr(pdf_bytes: bytes, dpi: int = 200) -> List[np.ndarray]:
        images: List[np.ndarray] = []
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            pix = page.get_pixmap(dpi=dpi)  # RGB o RGBA
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            images.append(img)
        return images

    @staticmethod
    def image_bytes_to_bgr(img_bytes: bytes) -> np.ndarray | None:
        buf = np.asarray(bytearray(img_bytes), dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)  # BGR
        return img


class QRReaderFacade:
    """
    FACADE: ofrece un método único para extraer payloads de un archivo subido,
    escondiendo la complejidad (PDF vs imagen, multi vs single QR).
    """

    def __init__(self) -> None:
        self.detector = cv2.QRCodeDetector()

    def extract_payloads(self, uploaded_file) -> List[QRPayload]:
        """
        Acepta InMemoryUploadedFile/TemporaryUploadedFile de Django.
        Devuelve una lista de QRPayload válidos encontrados en el archivo.
        """
        name = (uploaded_file.name or "").lower()
        data = uploaded_file.read()

        # 1) Adaptamos a listas de imágenes BGR
        if name.endswith(".pdf"):
            images = ImageAdapter.pdf_bytes_to_images_bgr(data)
        else:
            single = ImageAdapter.image_bytes_to_bgr(data)
            images = [single] if single is not None else []

        # 2) Decodificamos cada imagen (multi → single fallback)
        payloads: List[QRPayload] = []
        for img in images:
            if img is None:
                continue

            # Multi
            retval, decoded_info, points, _ = self.detector.detectAndDecodeMulti(img)
            texts: List[str] = []
            if retval and decoded_info:
                texts.extend([t for t in decoded_info if t])

            # Fallback single
            if not texts:
                t_single, pts, _ = self.detector.detectAndDecode(img)
                if t_single:
                    texts.append(t_single)

            # 3) Parseamos a QRPayload y filtramos válidos
            for t in texts:
                p = QRPayload.from_json(t)
                if p and (p.referencia and p.modelo and p.talla and p.sexo and p.color):
                    payloads.append(p)

        return payloads
