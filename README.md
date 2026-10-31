# Peakline — peaklineedit.com (medical version, 2026-10-31)

One-file site for US dental/medical clinics. Design v1 approved by Mehrshad 2026-10-31
(spec: vault `Strategy/Peakline/Site design v1/`). The founder version lives in git history (commit 269a1ea).

- `src/page.html` template · `src/styles.css` design stylesheet · `src/site.json` clips, contact, stats
- `src/fonts/` Instrument Sans (OFL, Latin variable 400–600) · `src/img/` posters (inlined)
- `python build.py` → `index.html` (noindex). `LAUNCH=1 python build.py` → indexable.
  The build warns about every empty slot; never publish with warnings.
- Videos: `media/` in this repo (720×1280 H.264, 5–9 MB, made by make_clip.py from out/). Old release `media-v1` stays.
- Deploy: GitHub Pages, branch `main`, root, file `index.html` + `CNAME`.
