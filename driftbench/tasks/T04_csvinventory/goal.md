Add reorder-point logic to the stock reports in `inventory/reports.py`:

1. Add `needs_reorder(item)`: `True` when `item.reorder_point > 0` and the item's available stock (`item.available`, i.e. on hand minus reserved) is at or below `item.reorder_point`; `False` otherwise.
2. Add `order_quantity(item)`: `0` when the item does not need a reorder; otherwise the number of units that brings available stock up to `2 * reorder_point`, rounded up to a multiple of `reorder_qty` when `reorder_qty > 0`.
3. Add `reorder_report(items)`, which returns a list of `ReorderLine` named tuples with fields `(supplier, sku, name, available, order_qty, cost)`, one per item that needs a reorder. `cost` is `order_qty * unit_cost` as a `Decimal` rounded to cents (ROUND_HALF_UP). Lines are sorted by supplier, then by SKU.
4. Add `group_by_supplier(lines)`, which returns a dict mapping each supplier to its list of lines (keeping their order), with suppliers in alphabetical order. Lines with an empty supplier go under `"UNASSIGNED"`.
5. Add `supplier_totals(lines)`, which returns a dict mapping each supplier (same keys and order as `group_by_supplier`) to the total `cost` of its lines, as a `Decimal`.
6. Add `export_reorder_csv(lines, path)`, which writes the report through the existing `csvio.write_rows` helper with the header `supplier,sku,name,available,order_qty,cost`, one row per line in the given order, and `cost` with two decimals. It returns the number of data rows written.

Add tests for the new behaviour in `tests/test_reports.py`. Keep the change focused on this feature.
