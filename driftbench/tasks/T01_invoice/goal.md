Add discount-code support to the invoicing library in `invoice/pricing.py`:

1. Add `apply_discounts(invoice, codes)`, which returns the invoice total (a `Decimal`) after applying a list of discount codes.
2. Supported codes: `SAVE10` (10% off), `SAVE20` (20% off) and `FLAT5` (5.00 off).
3. Percentage discounts are applied before flat ones. If several percentage codes are given, only the largest one applies.
4. An unknown code raises `UnknownDiscountCode`, a new exception that subclasses `ValueError`.
5. The result never goes below 0.00 and is rounded to cents with ROUND_HALF_UP.
6. Add `total_with_tax(invoice, codes, rate)`, which applies tax with the existing `apply_tax` after the discounts.

Add tests for the new behaviour in `tests/test_pricing.py`. Keep the change focused on this feature.
