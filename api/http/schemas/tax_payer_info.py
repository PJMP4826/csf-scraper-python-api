from csf_scraper import PersonaFisica, PersonaMoral

from api.http.schemas.base import SuccessEnvelope

TaxPayerInfo = PersonaMoral | PersonaFisica


class TaxPayerInfoResponse(SuccessEnvelope[TaxPayerInfo]):
    """Respuesta exitosa de la extracción de la CSF."""
