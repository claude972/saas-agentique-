"""Services métier devis.

Workflow (SRS) : Photo → PhotoAgent → Description → Quantification → QuoteAgent
→ Devis JSON → PDF → Archivage.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["QuoteLineDraft", "QuoteDraft", "compute_total"]


@dataclass
class QuoteLineDraft:
    designation: str
    unit: str = "u"
    quantity: float = 0.0
    unit_price: float = 0.0

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class QuoteDraft:
    reference: str
    lines: list[QuoteLineDraft] = field(default_factory=list)

    @property
    def total_ht(self) -> float:
        return compute_total(self.lines)


def compute_total(lines: list[QuoteLineDraft]) -> float:
    return round(sum(line.total for line in lines), 2)
