from dataclasses import asdict
from dataclasses import dataclass

@dataclass(frozen=True)
class AssetRegisterTokenPayload:
    aud: str
    iss: str
    uid: str
    name: str
    familyName: str
    email: str
    orgId: str
    orgVAT: str
    orgName: str
    orgRole: str
    orgPec: str
    orgAddress: str

    @classmethod
    def from_dict(cls, payload: dict[str, str]) -> "AssetRegisterTokenPayload":
        normalized = dict(payload)
        # The APIM signer reads email/orgVAT. Accept the legacy configuration
        # names without sending misspelled claims or mutating the secret object.
        for legacy, canonical in (('orgEmail', 'email'), ('orgVat', 'orgVAT')):
            if legacy in normalized:
                if canonical in normalized and normalized[canonical] != normalized[legacy]:
                    raise ValueError(f'Conflicting token fields: {legacy} and {canonical}')
                normalized[canonical] = normalized.pop(legacy)
        return cls(**normalized)

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
