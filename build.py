"""Build the one-file Peakline site: src/ -> index.html (repo root, served by GitHub Pages).

python build.py            -> noindex (preview / soft launch)
LAUNCH=1 python build.py   -> indexable
Prints a warning for every placeholder left; never launch with warnings.
"""
import base64, html, json, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
cfg = json.loads(pathlib.Path(os.environ.get("SITE") or SRC / "site.json").read_text(encoding="utf-8"))
warn = []

PLAY = '<span class="pk-play" aria-hidden="true"><svg width="18" height="20" viewBox="0 0 18 20"><path d="M2 1.8v16.4a1 1 0 0 0 1.5.86l13.6-8.2a1 1 0 0 0 0-1.72L3.5.94A1 1 0 0 0 2 1.8Z" fill="#1B5FD9"></path></svg></span>'
CAP = '<span class="pk-cap" aria-hidden="true"><span></span><span></span></span>'
CHECK = '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="10" fill="#EAF2FE"></circle><path d="m6 10.2 2.6 2.6L14 7.4" stroke="#1B5FD9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
CROSS = '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="10" fill="#E8EDF3"></circle><path d="m7 7 6 6M13 7l-6 6" stroke="#5E6B7F" stroke-width="1.8" stroke-linecap="round"></path></svg>'
PLUS = '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M10 4v12M4 10h12" stroke="#0E1A2B" stroke-width="1.8" stroke-linecap="round"></path></svg>'
e = lambda s: html.escape(s or "", quote=True)


def img(name):
    if not name:
        return ""
    p = SRC / "img" / name
    if not p.exists():
        warn.append(f"missing poster {name}")
        return ""
    mime = "image/webp" if p.suffix == ".webp" else "image/jpeg"
    return f'<img src="data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}" alt="" loading="lazy" decoding="async">'


def url(file):
    return (cfg["release_base"] + file) if file else ""


def poster(tag, poster_name, extra=""):
    pic = img(poster_name)
    cls = "pk-poster" + extra + (" has-img" if pic else "")
    return f'<span class="{cls}">{pic}<span class="pk-tag">{e(tag)}</span>{PLAY}{CAP}</span>'


def card(c, tag, meta=True, extra=""):
    src = url(c.get("file"))
    if not src:
        warn.append(f"no video for '{c.get('title', tag)}'")
    attrs = f' data-src="{e(src)}"' if src else " disabled"
    label = c.get("title") or tag
    body = poster(tag, c.get("poster"), extra)
    if meta:
        clinic = c.get("clinic") or "[Clinic name]"
        if not c.get("clinic"):
            warn.append(f"no clinic name for '{label}'")
        body += f'<span class="pk-card-meta"><b>{e(label)}</b><span>{e(clinic)} · made with a partner agency</span></span>'
    return f'<button type="button" class="pk-card" data-cat="{e(c.get("cat",""))}" aria-label="Play: {e(label)}"{attrs}>{body}</button>'


cats = dict(cfg["categories"])
tag_of = lambda c: "Patient story" if c["cat"] == "stories" else cats.get(c["cat"], "")

chips = ['<button type="button" class="pk-chip is-on" aria-pressed="true" data-f="all">All</button>']
used = {c["cat"] for c in cfg["clips"]}
chips += [f'<button type="button" class="pk-chip" aria-pressed="false" data-f="{k}">{e(v)}</button>' for k, v in cfg["categories"] if k in used]

cards = "\n".join(card(c, tag_of(c)) for c in cfg["clips"] if not c.get("more"))
extra = [c for c in cfg["clips"] if c.get("more")]
more_html = (f'<details class="pk-morework"><summary>See more work ({len(extra)} more)</summary><div class="pk-grid">'
             + "\n".join(card(c, tag_of(c)) for c in extra) + '</div></details>') if extra else ""
dv = cfg.get("drive")
shown = len(cfg["clips"]) + (1 if cfg.get("feature") else 0)
drive_html = (f'<p class="pk-small">{dv["total"] - shown} more reels from the same archive, all in one folder.</p>'
              f'<a class="pk-btn pk-btn--line pk-btn--sm" href="{e(dv["url"])}" target="_blank" rel="noopener">Watch {dv["total"] - shown} more reels on Google Drive</a>') if dv else              '<p class="pk-small">600+ edits in the archive. These are a few.</p><a class="pk-btn pk-btn--line pk-btn--sm" href="mailto:mehrshad@peaklineedit.com?subject=Full%20reel">Ask for the full reel</a>'
if not cfg.get("filters", True):
    chips = []
hero =[c for c in cfg["clips"] if c.get("hero")][:3]
hero_html = "\n".join(card(c, tag_of(c), meta=False) for c in hero)

ba = cfg["raw_vs_edited"]
ba_on = ba.get("enabled", True)
pair = ""
for key, tag, cap in ((("raw", "Raw", "As filmed"), ("edited", "Edited", "Peakline edit")) if ba_on else ()):
    c = dict(ba[key], title=f"the {key} clip" if key == "raw" else "the edited short")
    length = ba[key].get("length")
    if not length:
        warn.append(f"no length for raw/edited {key}")
    pair += f'<figure>{card(c, tag, meta=False, extra=" pk-raw" if key == "raw" else "")}<figcaption>{cap} <span>{e(length)}</span></figcaption></figure>\n'

ft = cfg.get("feature")
feature = ""
if ft:
    fc = dict(ft, cat="feature", title=ft["title"])
    btn = card(fc, "On TV", meta=False, extra=" pk-poster--wide").replace('class="pk-card"', 'class="pk-card pk-feature-play"', 1)
    feature = (f'<div class="pk-feature">{btn}<div class="pk-feature-text"><span class="pk-label"><i></i>{e(ft["label"])}</span>'
               f'<h3 class="pk-h3">{e(ft["title"])}</h3><p class="pk-p">{e(ft["text"])}</p><p class="pk-small">{e(ft.get("length",""))} · made with a partner agency</p></div></div>')

stats = cfg["stats"][:3]
stats_html = "\n".join(f'<div class="pk-stat"><b>{e(n)}</b><span>{e(l)}</span></div>' for n, l in stats)
stats_style = "" if len(stats) == 3 else f' style="grid-template-columns:repeat({len(stats)},minmax(0,1fr))"'

turn = cfg.get("turnaround") or ""
turn_offer = f"Within {turn}" if turn else "In a few days"
turn_step = f"within {turn}" if turn else "in a few days"

li = cfg.get("linkedin") or ""
linkedin = (f'<a class="pk-way" href="{e(li)}" target="_blank" rel="noopener"><span class="pk-way-ic"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="2.5" y="2.5" width="15" height="15" rx="3" stroke="currentColor" stroke-width="1.6"></rect><path d="M6.5 9v5M6.5 6.3v.1M9.5 14V9m0 2.4c0-1.4 1-2.4 2.2-2.4s2 .9 2 2.3V14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"></path></svg></span><div><b>Peakline on LinkedIn</b><span>Message us there</span></div></a>' if li else "")
if not li:
    warn.append("no LinkedIn URL (card hidden)")
ph = cfg.get("phone") or ""
digits = "".join(ch for ch in ph if ch.isdigit() or ch == "+")
phone = (f'<a class="pk-way" href="tel:{e(digits)}"><span class="pk-way-ic"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M5.2 3h2.6l1.4 3.6-1.8 1.2a9 9 0 0 0 4.8 4.8l1.2-1.8L17 12.2v2.6A2 2 0 0 1 15 17 13 13 0 0 1 3 5a2 2 0 0 1 2.2-2Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"></path></svg></span><div><b>{e(ph)}</b><span>Call or text (US)</span></div></a>' if ph else "")
if not ph:
    warn.append("no US phone (card hidden)")

JS = r"""
(function(){
  var chips=document.querySelectorAll('.pk-chip'),cards=document.querySelectorAll('.pk-grid .pk-card');
  chips.forEach(function(ch){ch.addEventListener('click',function(){
    var f=ch.getAttribute('data-f');
    chips.forEach(function(x){var on=x===ch;x.classList.toggle('is-on',on);x.setAttribute('aria-pressed',on?'true':'false');});
    cards.forEach(function(c){c.hidden=!(f==='all'||c.getAttribute('data-cat')===f);});
  });});
  document.addEventListener('click',function(ev){
    var b=ev.target.closest('.pk-card[data-src]');if(!b)return;
    var p=b.querySelector('.pk-poster');if(p.classList.contains('is-playing'))return;
    document.querySelectorAll('.pk-poster video').forEach(function(v){v.pause();});
    var v=document.createElement('video');
    v.src=b.getAttribute('data-src');v.controls=true;v.playsInline=true;v.setAttribute('playsinline','');v.preload='auto';
    var im=p.querySelector('img');if(im)v.poster=im.src;
    p.appendChild(v);p.classList.add('is-playing');
    v.play().catch(function(){});
  });
  document.addEventListener('play',function(ev){
    document.querySelectorAll('.pk-poster video').forEach(function(v){if(v!==ev.target)v.pause();});
  },true);
})();
"""

launch = os.environ.get("LAUNCH") == "1"
import re
rep = {
    "{{ROBOTS}}": "" if launch else '<meta name="robots" content="noindex">',
    "{{FONT}}": base64.b64encode((SRC / "fonts" / "InstrumentSans-latin.woff2").read_bytes()).decode(),
    "{{CSS}}": (SRC / "styles.css").read_text(encoding="utf-8"),
    "{{STATS}}": stats_html, "{{STATS_STYLE}}": stats_style,
    "{{HERO_REEL}}": hero_html, "{{CHIPS}}": "\n".join(chips), "{{CARDS}}": cards, "{{MORE}}": more_html, "{{DRIVE}}": drive_html, "{{ABOUT_IMG}}": img(cfg.get("about_photo", "about.jpg")).replace('alt=""', 'alt="Mehrshad Javid"'), "{{LINKEDIN_URL}}": e(cfg.get("linkedin", "")), "{{NCARDS}}": str(sum(1 for c in cfg["clips"] if not c.get("more"))),
    "{{BA_PAIR}}": pair, "{{FEATURE}}": feature, "{{CHECK}}": CHECK, "{{CROSS}}": CROSS, "{{PLUS}}": PLUS,
    "{{TURN_OFFER}}": turn_offer, "{{TURN_STEP}}": turn_step,
    "{{LINKEDIN}}": linkedin, "{{PHONE}}": phone, "{{JS}}": JS.strip(),
}
# template -> output. Clinic page always at /clinics/; the homepage uses home.html once it exists
# (until then / keeps showing the clinic page, so no link ever breaks).
out_root = pathlib.Path(os.environ.get("OUT") or ROOT)
pages = [("clinics.html", "clinics/index.html"),
         ("home.html" if (SRC / "home.html").exists() else "clinics.html", "index.html")]
# extra pages: src/<name>.html -> /<name>/ (e.g. system.html -> /system/, pack.html -> /pack/)
pages += [(p.name, f"{p.stem}/index.html") for p in sorted(SRC.glob("*.html"))
          if p.name not in ("clinics.html", "home.html", "page.html")]
for tpl, dest in pages:
    out = (SRC / tpl).read_text(encoding="utf-8")
    if not ba_on:
        out = re.sub(r"<!--BA-->.*?<!--/BA-->\s*", "", out, flags=re.S)
    for k, v in rep.items():
        out = out.replace(k, v)
    if "{{" in out:
        sys.exit(f"unreplaced placeholder in {tpl}")
    if tpl == "clinics.html" and dest == "index.html":  # temporary: / still serves clinic copy
        out = out.replace('href="https://peaklineedit.com/clinics/">', 'href="https://peaklineedit.com/">', 1)
    p = out_root / dest
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(out, encoding="utf-8")
    print(f"{dest} ({tpl}) {len(out.encode())/1024:.0f} kB · {'LAUNCH (indexable)' if launch else 'noindex'}")
for w in sorted(set(warn)):
    print("  ⚠", w)
