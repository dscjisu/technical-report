# dscjisu/technical-report

The **Technical Report** of GDG on Campus JIS University — a season-by-season record of the chapter's
events, attendance, footfall and community growth since 2022, typeset from structured data.

## Build

```bash
python3 build.py                        # emits dscjisu_report_21_26.tex
latexmk -pdf dscjisu_report_21_26.tex   # or: pdflatex dscjisu_report_21_26.tex ×2
```

## How it's organised

- **Data** — `records.json` is authoritative if present; otherwise the inline `SEASONS` / `EVENTS`
  in `build.py` are used. Adding an event or season is a data edit — the TOC, stats, charts and
  galleries all recompute.
- **Gallery images** — drop files into `assets/gallery/<NN>/` (zero-padded event number); they're
  optimised and laid out as a balanced grid automatically.
- **Attendance** — event totals are kept in `records.json`; named rosters are not included in the
  published report.
- **Brand assets** — `assets/brand/`.

## Related repositories

- [`dscjisu/guidelines`](https://github.com/dscjisu/guidelines) — the operating playbook.
- [`dscjisu/events`](https://github.com/dscjisu/events) — event coordination.
- [`dscjisu/branding`](https://github.com/dscjisu/branding) — brand assets.

---
GDG on Campus JIS University · Department of Computer Science &amp; Engineering

## Coverage note

The PDF records 36 chapter events across four seasons, including all 21 events
completed during the 2025–26 organiser tenure. The 21st event was the Gemma for
Bharat Swag Distribution & Workshop on 22 July.

HexaFalls 2 is not part of the DSCJISU event record.
