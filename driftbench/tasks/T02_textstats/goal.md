Add a "top words" feature to `textstats`:

1. Add `top_words(text, n, stopwords=None)` to `textstats/counter.py`. It returns a list of `(word, count)` tuples sorted by count (descending), with ties broken alphabetically.
2. Create `textstats/stopwords.py` with a `DEFAULT_STOPWORDS` frozenset containing at least: the, a, an, and, of, to, in, is, it. `top_words` uses it when `stopwords` is `None`; passing an empty set disables filtering.
3. `n` must be positive, otherwise `top_words` raises `ValueError`.
4. Contractions such as "don't" and "it's" must be kept as single tokens by the tokenizer.
5. CLI: add `--top N`, which prints one `word<TAB>count` line per top word after the existing output, and `--keep-stopwords`, which disables stopword filtering.

Add tests in `tests/test_counter.py` and `tests/test_cli.py`. Keep the change focused on this feature.
