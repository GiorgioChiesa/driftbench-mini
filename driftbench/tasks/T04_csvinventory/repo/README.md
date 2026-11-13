# inventory

Stock management for a small warehouse: items are imported from and exported to CSV,
stock movements go through a `Ledger`, and `inventory.reports` builds stock reports.

CSV columns: `sku,name,supplier,on_hand,reserved,unit_cost,reorder_point,reorder_qty`
(`supplier`, `reserved`, `reorder_point` and `reorder_qty` are optional).

Run the tests with `python -m pytest`.
