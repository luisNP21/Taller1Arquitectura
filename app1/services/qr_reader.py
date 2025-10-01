from abc import ABC, abstractmethod
from typing import Any

class QRReader(ABC):
    """Abstracción para lectores de códigos QR."""

    @abstractmethod
    def decode(self, image_or_bytes) -> Any:
        """
        Decodifica un QR a partir de una imagen o bytes.
        Retorna el contenido como string, o None si no hay QR válido.
        """
        raise NotImplementedError

