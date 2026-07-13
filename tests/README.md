# Web and portfolio tests

- `rendered-html.test.mjs` verifies that the React server output contains the complete research case and required artifacts.
- `standalone-html.test.mjs` verifies the root portfolio, inline JavaScript and every local asset/download link.

Run both through `npm test`. The Python analytics suite is located in `analytics/tests/` and runs with:

```bash
python -m unittest discover -s analytics/tests -v
```
