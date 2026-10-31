"""Prep one site clip: python make_clip.py <input video> <slug>
-> out/<slug>.mp4  (720x1280 H.264, faststart, aims for 5-9 MB) + src/img/<slug>.jpg (poster, inlined by build.py)
Then upload out/*.mp4 to the GitHub Release media-medical-v1 and put "<slug>.mp4" / "<slug>.jpg" in src/site.json.
"""
import pathlib, subprocess, sys

src, slug = sys.argv[1], sys.argv[2]
root = pathlib.Path(__file__).resolve().parent
(root / "out").mkdir(exist_ok=True)
mp4, jpg = root / "out" / f"{slug}.mp4", root / "src" / "img" / f"{slug}.jpg"
wh = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", src]).decode().strip().split(",")
wide = int(wh[0]) > int(wh[1])
W, H = (1280, 720) if wide else (720, 1280)
vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]).strip())
# ~7 MB target: video bitrate from duration, capped 1.0-3.0 Mbps
vb = max(1000, min(3000, int(7 * 8192 / dur) - 128))
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-vf", vf, "-r", "30", "-c:v", "libx264", "-preset", "slow",
                "-b:v", f"{vb}k", "-maxrate", f"{int(vb*1.5)}k", "-bufsize", f"{vb*2}k", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k", "-ac", "2", "-movflags", "+faststart", str(mp4)], check=True)
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(min(1.0, dur / 3)), "-i", src, "-frames:v", "1",
                "-vf", vf.replace(f"{W}:{H}", f"{W//2}:{H//2}"), "-q:v", "6", str(jpg)], check=True)
print(f"{mp4.name}: {mp4.stat().st_size/1e6:.1f} MB ({dur:.0f}s, {vb} kbps) · {jpg.name}: {jpg.stat().st_size/1e3:.0f} kB")
