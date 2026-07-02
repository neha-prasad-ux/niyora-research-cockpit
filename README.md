# Niyora Research Cockpit

Local research bank for women's cycle / premenstrual mental health.
API harvest (Europe PMC) → local DuckDB → Streamlit cockpit → curate into the Table.

## Use
```
python3 harvest.py     # (re)build the bank from Europe PMC — 29 lanes
./run.sh               # launch the cockpit (or: python3 -m streamlit run app.py)
```

## Files
- `lanes.py`     — the 29 lane queries (core / modulator / impact / context) + tags + caps
- `harvest.py`   — Europe PMC → `research.db` (DuckDB), dedupe by DOI, auto-grade by study type
- `app.py`       — the cockpit: filter, read abstracts, Promote / Irrelevant, export
- `research.db`  — the local bank (DuckDB single file)

## Notes
- DuckDB is single-writer: stop the app before re-running `harvest.py`.
- Curation (status / notes) is preserved across re-harvests; only bibliographic fields refresh.
- `safety` (self-harm) lane is tagged, not hidden — filter Tag=safety to review deliberately.
