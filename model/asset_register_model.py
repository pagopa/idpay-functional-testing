from dataclasses import asdict
from dataclasses import dataclass

@dataclass(frozen=True)
class AssetRegisterTokenPayload:
    aud: str
    iss: str
    uid: str
    name: str
    familyName: str
    orgEmail: str
    orgId: str
    orgVat: str
    orgName: str
    orgRole: str
    orgPec: str
    orgAddress: str

    @classmethod
    def from_dict(cls, payload: dict[str, str]) -> "AssetRegisterTokenPayload":
        return cls(**payload)

    def to_dict(self) -> dict[str, str]:
        return asdict(self)