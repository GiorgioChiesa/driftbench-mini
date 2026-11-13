# ledger

A small double-entry-ish bank ledger: accounts with overdraft limits, an append-only journal of
dated transactions, simple-interest helpers and CSV/JSON export.

```python
from datetime import date
from ledger import Ledger

book = Ledger()
book.open_account("ALICE", "Alice")
book.deposit("ALICE", "100.00", date(2024, 1, 5), memo="salary")
book.balance("ALICE")   # Decimal('100.00')
```

Run the tests with `python -m pytest`.
