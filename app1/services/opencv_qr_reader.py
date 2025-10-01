import cv2
import numpy as np
import json
from .qr_reader import QRReader

class OpenCVQRReader(QRReader):
    def decode(self, image_or_bytes):
        """
        Recibe una imagen como numpy array (BGR) o bytes y devuelve un diccionario con los datos del QR.
        """
        # Convertir a imagen numpy si viene en bytes
        if isinstance(image_or_bytes, bytes):
            nparr = np.frombuffer(image_or_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("No se pudo decodificar la imagen desde bytes.")
        elif isinstance(image_or_bytes, np.ndarray):
            img = image_or_bytes
        else:
            raise TypeError(f"Tipo no soportado en decode(): {type(image_or_bytes)}")

        detector = cv2.QRCodeDetector()
        data, points, _ = detector.detectAndDecode(img)

        if not data:
            return None

        return data
