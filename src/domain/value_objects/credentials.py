from abc import ABC, abstractmethod

from csf_scraper import Rfc


class Credentials(ABC):
    """Credenciales que identifican a un contribuyente mediante su RFC."""

    @property
    @abstractmethod
    def rfc(self) -> Rfc:
        """RFC del titular de las credenciales."""
