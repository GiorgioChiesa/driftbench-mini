"""JSON persistence for invoices."""
import json
from decimal import Decimal

from .models import Invoice, LineItem


def to_dict(invoice: Invoice) -> dict:
    return {
        "number": invoice.number,
        "customer": invoice.customer,
        "items": [
            {"sku": i.sku, "description": i.description, "quantity": i.quantity, "unit_price": str(i.unit_price)}
            for i in invoice.items
        ],
    }


def from_dict(data: dict) -> Invoice:
    inv = Invoice(data["number"], data["customer"])
    for raw in data["items"]:
        inv.add(LineItem(raw["sku"], raw["description"], int(raw["quantity"]), Decimal(raw["unit_price"])))
    return inv


def save(invoice: Invoice, path) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(to_dict(invoice), fh, indent=2)


def load(path) -> Invoice:
    with open(path, encoding="utf-8") as fh:
        return from_dict(json.load(fh))
