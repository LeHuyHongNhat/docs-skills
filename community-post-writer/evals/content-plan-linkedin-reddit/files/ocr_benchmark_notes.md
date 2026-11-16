# OCR benchmark — Vietnamese invoices (my side project, Oct 2026)

Dataset: 400 scanned Vietnamese VAT invoices from 3 SMEs (shared with permission, cannot be published).
Images: 300 dpi scans, 60 phone photos among them. Labelled 9 fields per invoice by hand (seller tax code, invoice no., date, total, VAT amount, ...).
Metric: field-level exact match after normalising whitespace and thousand separators. Single run per engine, same machine (RTX 4070, 12 GB).

| Engine | Field exact match | Exact match on phone photos only (60) | Time / invoice |
|---|---|---|---|
| Tesseract 5 (vie) | 71.4% | 48.9% | 0.9 s |
| PaddleOCR (latin + vi dict) | 83.2% | 70.6% | 0.6 s |
| VietOCR + CRAFT detector | 88.7% | 79.1% | 1.4 s |

Observations:
- Most errors on all engines: diacritics in seller names (e.g. "Thương mại" → "Thuong mai") and confusing 0/O in invoice numbers.
- Tax-code field is easiest (digits only): > 95% for all three.
- VietOCR is slowest but best on photos.
- A vendor sales deck claims their commercial API gets "99% accuracy on Vietnamese invoices" — I did not test it, no access.
- My guess: fine-tuning VietOCR on 2k invoices would close most of the gap to commercial tools (not tested).

I built the benchmark harness myself (repo: github.com/example/vn-invoice-ocr-bench, MIT).
