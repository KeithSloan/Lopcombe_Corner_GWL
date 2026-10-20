# PDF report builders

The scripts that produced the PDFs in `docs/reports/` (reportlab + matplotlib), saved for reference.
They were run in Claude's workspace on 20 Oct 2026; paths have been rewritten to be relative to the repo root,
but they have not been re-tested from here and some still read intermediate files by fixed names.

| Script | Report |
|---|---|
| `build_pdfs.py` | Annual max levels, Oct–Dec and Oct–Mar rainfall reports (recreations) |
| `build_haduk_pdf.py` | `Lopcombe_HadUK_Rainfall_Cyclicity.pdf` |
| `build_start_pdf2.py` | `Lopcombe_Start_of_Winter_Level.pdf` |
| `build_flood_pdf.py` | `Lopcombe_Flood_Probability.pdf` |
| `build_method_pdf.py` | `HadUK-Grid_Rainfall_Method.pdf` |
| `build_summary_pdf.py` | `Lopcombe_Summary.pdf` |

Requires `reportlab` and `pillow` in addition to `requirements.txt`. Run from the repo root after the analysis scripts.
