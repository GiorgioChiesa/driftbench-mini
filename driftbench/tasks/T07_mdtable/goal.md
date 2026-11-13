Add alignment, number formatting, escaping and a maximum cell width to the Markdown renderer in `mdtable/table.py`:

1. `render_table(headers, rows, align=None)`: `align` is a string with one letter per column, `l`, `r` or `c`. The separator cell of a column is `:` followed by dashes (`l`), dashes followed by `:` (`r`) or `:` + dashes + `:` (`c`), always exactly as wide as the column (e.g. `:--`, `--:`, `:-:` for a 3-wide column). Without `align` the separator stays all dashes. An `align` string of the wrong length or with any other letter raises `ValueError`.
2. Header and body cells are padded to the column width according to the column's alignment: `l` left-aligned, `r` right-aligned, `c` centred with the odd extra space on the right. Without `align` every column is left-aligned. Widths are measured in display columns with the existing `textutil.display_width` (minimum 3, as today).
3. New keyword `decimals=None`: when given, every `int`, `float` or `Decimal` cell (but not `bool`) is rendered with exactly `decimals` digits after the point, rounded half-up (`2.675` → `2.68`, `2` → `2.00`). Without `decimals` numbers render as `str(value)`. `None` cells are always empty.
4. Headers and cells are escaped for Markdown: `|` becomes `\|` and each line break (`\n` or `\r\n`) becomes `<br>`. Column widths are computed on the escaped text.
5. New keyword `max_width=None`: when given, any header or cell wider than `max_width` display columns is shortened to exactly `max_width` columns, ending with `…`; text that fits (including text exactly `max_width` wide) is left alone. Truncation happens before escaping.
6. `Table(headers, align=None, decimals=None, max_width=None)` stores these options and `Table.render()` passes them to `render_table`.

Add tests for the new behaviour in `tests/test_table.py`. Keep the change focused on this feature.
