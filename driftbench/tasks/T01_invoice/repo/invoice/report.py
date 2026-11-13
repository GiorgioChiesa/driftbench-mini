"""Plain-text rendering of invoices."""
from .models import Invoice
from .money import fmt
from .pricing import subtotal


def render_text(invoice: Invoice, width: int = 40) -> str:
    lines = [f"INVOICE {invoice.number}".center(width, "="), f"Customer: {invoice.customer}", ""]
    for item in invoice.items:
        left = f"{item.quantity} x {item.description}"
        right = fmt(item.total())
        lines.append(left + right.rjust(width - len(left)))
    lines.append("-" * width)
    label = "Subtotal"
    lines.append(label + fmt(subtotal(invoice)).rjust(width - len(label)))
    return "\n".join(lines)
