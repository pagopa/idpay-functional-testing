"""Models for the Visura Impresa REST client payload."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ClassificazioneAteco:
    codice_attivita: str | None = None
    attivita: str | None = None
    codice_importanza: str | None = None


@dataclass
class InfoAttivita:
    classificazioni_ateco: list[ClassificazioneAteco] | None = None


@dataclass
class VisuraImpresa:
    """Payload used by the visura-impresa REST endpoint."""

    codice_fiscale: str
    info_attivita: InfoAttivita | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the JSON field names expected by the REST API."""
        return {
            "codiceFiscale": self.codice_fiscale,
            "infoAttivita": self._serialize_info_attivita(self.info_attivita),
        }

    @staticmethod
    def _serialize_info_attivita(info_attivita: InfoAttivita | None) -> dict[str, Any] | None:
        if info_attivita is None:
            return None

        classifications = info_attivita.classificazioni_ateco
        return {
            "classificazioniAteco": [
                {
                    "codiceAttivita": item.codice_attivita,
                    "attivita": item.attivita,
                    "codiceImportanza": item.codice_importanza,
                }
                for item in classifications
            ]
            if classifications is not None
            else None
        }