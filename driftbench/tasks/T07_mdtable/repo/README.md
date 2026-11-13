# mdtable

Render tabular data as GitHub-flavoured Markdown (or plain HTML) tables. Includes a small CSV
reader with type coercion, number formatting helpers and width-aware text utilities that handle
East Asian wide characters.

```python
from mdtable import Table

print(Table(["Item", "Qty"]).add_row("pen", 3).add_row("notebook", 12).render())
```

Run the tests with `python -m pytest`.
