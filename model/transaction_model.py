import datetime

from dataclasses import dataclass


def _format_report_datetime(value: datetime.datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=datetime.timezone.utc)
    value = value.astimezone(datetime.timezone.utc)
    return value.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]


@dataclass(frozen=True)
class ReportRequest:
    start_period: datetime.datetime
    end_period: datetime.datetime
    report_type: str

    def to_dict(self) -> dict:
        return {
            'startPeriod': _format_report_datetime(self.start_period),
            'endPeriod': _format_report_datetime(self.end_period),
            'reportType': self.report_type,
        }


@dataclass(frozen=True)
class ChecksErrorDTO:
    cf_error: bool | None = False
    product_eligibility_error: bool | None = False
    disposal_raee_error: bool | None = False
    price_error: bool | None = False
    bonus_error: bool | None = False
    seller_reference_error: bool | None = False
    accounting_document_error: bool | None = False
    generic_error: bool | None = False

    @classmethod
    def from_dict(cls, payload: dict) -> 'ChecksErrorDTO':
        return cls(
            cf_error=payload.get('cfError'),
            product_eligibility_error=payload.get('productEligibilityError'),
            disposal_raee_error=payload.get('disposalRaeeError'),
            price_error=payload.get('priceError'),
            bonus_error=payload.get('bonusError'),
            seller_reference_error=payload.get('sellerReferenceError'),
            accounting_document_error=payload.get('accountingDocumentError'),
            generic_error=payload.get('genericError'),
        )

    def to_dict(self) -> dict:
        payload = {}
        if self.cf_error is not None:
            payload['cfError'] = self.cf_error
        if self.product_eligibility_error is not None:
            payload['productEligibilityError'] = self.product_eligibility_error
        if self.disposal_raee_error is not None:
            payload['disposalRaeeError'] = self.disposal_raee_error
        if self.price_error is not None:
            payload['priceError'] = self.price_error
        if self.bonus_error is not None:
            payload['bonusError'] = self.bonus_error
        if self.seller_reference_error is not None:
            payload['sellerReferenceError'] = self.seller_reference_error
        if self.accounting_document_error is not None:
            payload['accountingDocumentError'] = self.accounting_document_error
        if self.generic_error is not None:
            payload['genericError'] = self.generic_error
        return payload


@dataclass(frozen=True)
class ReasonDTO:
    date: str
    reason: str

    @classmethod
    def from_dict(cls, payload: dict) -> 'ReasonDTO':
        return cls(
            date=payload['date'],
            reason=payload['reason'],
        )

    def to_dict(self) -> dict:
        return {
            'date': self.date,
            'reason': self.reason,
        }


@dataclass(frozen=True)
class TransactionActionRequest:
    transaction_ids: list[str]
    reason: str | None = None
    checks_error: ChecksErrorDTO | None = None

    @classmethod
    def from_dict(cls, payload: dict) -> 'TransactionActionRequest':
        checks_error = payload.get('checksError')
        return cls(
            transaction_ids=payload['transactionIds'],
            reason=payload.get('reason'),
            checks_error=ChecksErrorDTO.from_dict(checks_error) if checks_error else None,
        )

    def to_dict(self) -> dict:
        payload = {'transactionIds': self.transaction_ids}
        if self.reason is not None:
            payload['reason'] = self.reason
        if self.checks_error is not None:
            payload['checksError'] = self.checks_error.to_dict()
        return payload
