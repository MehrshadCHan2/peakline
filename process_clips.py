"""Turn the downloaded Drive finals into site clips.
python process_clips.py [folder]   (default ~/Downloads/peakline-clips; zips are unpacked first)
Matches each clip's "drive" name in src/site.json, runs make_clip.py -> out/<slug>.mp4 + src/img/<slug>.jpg
"""
import json, pathlib, subprocess, sys, zipfile

root = pathlib.Path(__file__).resolve().parent
folder = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path.home() / "Downloads" / "peakline-clips")
for z in folder.glob("*.zip"):
    zipfile.ZipFile(z).extractall(folder / z.stem)
vids = [p for p in folder.rglob("*") if p.suffix.lower() in (".mp4", ".mov")]
norm = lambda s: "".join(ch for ch in s.lower() if ch.isalnum())
cfg = json.loads((root / "src" / "site.json").read_text(encoding="utf-8"))
missing = []
for c in cfg["clips"]:
    want = norm(c["drive"].rsplit(".mp4", 1)[0])
    hit = [v for v in vids if norm(v.stem) == want] or [v for v in vids if norm(v.stem).startswith(want)]
    if not hit:
        missing.append(c["drive"]); continue
    slug = c["file"].rsplit(".", 1)[0]
    subprocess.run([sys.executable, str(root / "make_clip.py"), str(hit[0]), slug], check=True)
print("missing:", missing or "none")
