# Nassau Candy shipping analysis

This project audits shipment-date quality and provides defensible sales, product, geography, ship-mode usage, and factory-to-destination volume summaries. It does not claim delivery-efficiency rankings because the supplied shipment dates are inconsistent with the order dates.

## Run

Use Python with the packages in `requirements.txt`:

```powershell
python analysis.py
python visualizations.py
streamlit run dashboard.py
```

The Streamlit dashboard reads `outputs/cleaned_shipments.csv`. Run the analysis script after replacing the source CSV so that the derived data and audit outputs are refreshed. Static charts are written under `outputs/`.

## Main deliverables

- `dashboard.py` — interactive dashboard with date, region, state, ship-mode, and lead-time threshold controls.
- `research_paper.md` — methods, findings, limitations, and operational recommendations.
- `executive_summary.md` — concise decision brief.
- `analysis.py` — reproducible cleaning, date audit, and CSV summary generation.
- `visualizations.py` — static sales and route-volume charts.
- `outputs/date_audit_summary.csv` — date validation evidence.

## Date-quality caveat

The source has order dates from 2024-01-02 to 2025-12-31 and ship dates from 2026-06-30 to 2030-06-28. All 10,194 calculated lead times exceed 30 days. Preserve the source dates and request corrected or explained shipment dates before interpreting lead times, delays, or route efficiency. Route volume counts are order lines; distinct order counts are reported separately.
