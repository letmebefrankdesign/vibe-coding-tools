"""Builds content/review/mitchells-month.html: one page to approve the whole month.

Run: python3 scripts/build_review.py
Images are embedded as small JPEG data URIs (artifact pages can't load outside images).
"""
import base64
import datetime as dt
import glob
import html
import io
import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
manifest = json.load(open(os.path.join(ROOT, "media/rendered/manifest.json")))
PLAT = {"instagram": "Instagram", "facebook": "Facebook", "gbp": "Google Business"}


def thumb(path, w=520):
    im = Image.open(os.path.join(ROOT, path)).convert("RGB")
    im.thumbnail((w, w * 2))
    b = io.BytesIO()
    im.save(b, "JPEG", quality=72, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def t12(hhmm):
    h, m = map(int, hhmm.split(":"))
    return f"{(h - 1) % 12 + 1}:{m:02d} {'AM' if h < 12 else 'PM'}"


posts = []
for wf in sorted(glob.glob(os.path.join(ROOT, "content/weeks/*.json"))):
    posts += json.load(open(wf))["posts"]

cards = []
for p in posts:
    d = dt.date.fromisoformat(p["date"])
    head = " / ".join(p["headline"]) if isinstance(p["headline"], list) else p["headline"]
    tabs, panes = [], []
    for i, (k, v) in enumerate(p["variants"].items()):
        imgs = "".join(
            f'<img src="{thumb(f)}" alt="{html.escape(p["altText"][min(n, len(p["altText"]) - 1)])}" loading="lazy">'
            for n, f in enumerate(manifest[p["id"]][k]))
        extra = f'<div class="cta">Button: {v["cta"].replace("_", " ").title()}</div>' if k == "gbp" else ""
        tabs.append(f'<button class="tab{" on" if i == 0 else ""}" data-pane="{p["id"]}-{k}" type="button">{PLAT[k]} <span>{t12(v["time"])}</span></button>')
        panes.append(f'<div class="pane" id="{p["id"]}-{k}"{"" if i == 0 else " hidden"}><div class="imgs n{len(manifest[p["id"]][k])}">{imgs}</div>'
                     f'<pre class="cap">{html.escape(v["text"])}</pre>{extra}</div>')
    note = f'<p class="note">{html.escape(p["notes"])}</p>' if p.get("notes") else ""
    pm = int(p["variants"]["instagram"]["time"][:2]) >= 12
    cards.append(f'''
<article class="post" data-id="{p["id"]}">
  <header>
    <div class="date"><b>{d.strftime("%a")}</b><span>{d.strftime("%b %-d")}</span></div>
    <div class="meta"><h2>{html.escape(head)}</h2>
      <div class="chips"><span class="chip">{html.escape(p["pillar"])}</span>{'<span class="chip eve">Evening post</span>' if pm else ''}{'<span class="chip gbp">+ Google</span>' if "gbp" in p["variants"] else ''}</div></div>
    <label class="ok"><input type="checkbox" id="ok-{p["id"]}" data-id="{p["id"]}"> Approve</label>
  </header>
  {note}
  <div class="tabs">{"".join(tabs)}</div>
  {"".join(panes)}
</article>''')

n_plat = sum(len(p["variants"]) for p in posts)
page = f'''<title>Mitchell's Social Month</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=Source+Sans+3:wght@400;600&display=swap">
<style>
/* Layout: a single feed of day cards, like scrolling the calendar; sticky approval bar at the bottom. Mitchell's red and script-black on a cool white. */
:root{{
  --bg:#f5f5f3; --card:#ffffff; --ink:#1f1a1f; --muted:#646068; --line:#e3e1e4; --red:#d4271d; --red-soft:#fbe4e2; --ok:#1d7a47; --gold:#c98a12;
  --head:"Oswald", "Arial Narrow", system-ui, sans-serif; --body:"Source Sans 3", "Segoe UI", system-ui, sans-serif;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#141215;--card:#1e1b1f;--ink:#f1eef2;--muted:#aaa4ad;--line:#332f35;--red:#ff5a4e;--red-soft:#3a1d1b;--ok:#5cc98d;--gold:#e8b44a;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#141215;--card:#1e1b1f;--ink:#f1eef2;--muted:#aaa4ad;--line:#332f35;--red:#ff5a4e;--red-soft:#3a1d1b;--ok:#5cc98d;--gold:#e8b44a;color-scheme:dark}}
body{{background:var(--bg);color:var(--ink);font:16px/1.5 var(--body)}}
.wrap{{max-width:880px;margin:0 auto;padding:28px 16px 120px;display:flex;flex-direction:column;gap:18px}}
h1{{font:600 clamp(30px,6vw,44px)/1.05 var(--head);margin:0;letter-spacing:.01em;text-transform:uppercase}}
h1 em{{font-style:normal;color:var(--red)}}
.intro{{display:flex;flex-direction:column;gap:10px}}
.intro p{{margin:0;color:var(--muted);max-width:68ch}}
.stats{{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:15px}}
.stats b{{font-family:var(--head);font-size:20px;color:var(--ink);margin-right:4px}}
.rules{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;font-size:15px;columns:2 260px;column-gap:28px}}
.rules div{{break-inside:avoid;margin-bottom:6px}}
.post{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:12px}}
.post.approved{{border-color:var(--ok);box-shadow:inset 4px 0 0 var(--ok)}}
.post header{{display:grid;grid-template-columns:auto 1fr auto;gap:14px;align-items:center}}
.date{{width:58px;text-align:center;border-radius:8px;background:var(--red);color:#fff;padding:6px 0;display:flex;flex-direction:column;line-height:1.1}}
.date b{{font:600 13px var(--head);text-transform:uppercase;letter-spacing:.08em}}
.date span{{font:600 17px var(--head)}}
.meta{{min-width:0;display:flex;flex-direction:column;gap:6px}}
h2{{font:500 21px/1.15 var(--head);margin:0;text-wrap:balance}}
.chips{{display:flex;flex-wrap:wrap;gap:6px}}
.chip{{font-size:13px;border:1px solid var(--line);border-radius:999px;padding:1px 9px;color:var(--muted)}}
.chip.eve{{color:var(--gold);border-color:var(--gold)}}
.chip.gbp{{color:var(--red);border-color:var(--red)}}
.ok{{display:flex;gap:8px;align-items:center;font-weight:600;cursor:pointer;white-space:nowrap}}
.ok input{{width:20px;height:20px;accent-color:var(--ok)}}
.note{{margin:0;font-size:14px;background:var(--red-soft);border-radius:8px;padding:8px 12px}}
.tabs{{display:flex;flex-wrap:wrap;gap:6px}}
.tab{{font:600 14px var(--body);border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:8px;padding:6px 12px;cursor:pointer}}
.tab span{{font-weight:400;color:var(--muted)}}
.tab.on{{background:var(--ink);color:var(--bg);border-color:var(--ink)}}
.tab.on span{{color:var(--bg);opacity:.75}}
.tab:focus-visible,.ok input:focus-visible,button.copy:focus-visible{{outline:3px solid var(--red);outline-offset:2px}}
.pane{{display:grid;grid-template-columns:minmax(0,300px) minmax(0,1fr);gap:16px;align-items:start}}
.imgs{{display:grid;gap:6px}}
.imgs.n2{{grid-template-columns:1fr 1fr}}
.imgs img{{width:100%;border-radius:8px;display:block}}
.cap{{margin:0;white-space:pre-wrap;word-wrap:break-word;font:15px/1.5 var(--body);min-width:0}}
.cta{{font-size:13px;color:var(--muted);grid-column:2}}
.bar{{position:fixed;left:0;right:0;bottom:0;padding:12px 16px calc(12px + env(safe-area-inset-bottom,0px));background:var(--card);border-top:1px solid var(--line);display:flex;justify-content:center}}
.bar .in{{max-width:880px;width:100%;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}}
.bar .count{{font-weight:600}}
.bar .btns{{display:flex;gap:8px;flex-wrap:wrap}}
button.copy{{font:600 15px var(--body);border:0;border-radius:8px;padding:10px 16px;background:var(--red);color:#fff;cursor:pointer}}
button.copy.alt{{background:transparent;color:var(--ink);border:1px solid var(--line)}}
@media (max-width:640px){{.pane{{grid-template-columns:1fr}}.cta{{grid-column:1}}.post header{{grid-template-columns:auto 1fr}}.ok{{grid-column:1/-1}}}}
</style>
<main class="wrap">
  <section class="intro">
    <h1>Mitchell's <em>Social Month</em></h1>
    <p>Oct 8 to Nov 7, 2026. Instagram and Facebook every day, Google Business Profile Mon / Wed / Fri. All times Eastern. Nothing posts until you approve and run the schedule command.</p>
    <div class="stats"><span><b>{len(posts)}</b>days</span><span><b>{n_plat}</b>platform posts</span><span><b>{sum(len(f) for e in manifest.values() for f in e.values())}</b>images</span></div>
  </section>
  <section class="rules">
    <div><b>Morning posts</b> go out at 7:00 AM, when the doors open.</div>
    <div><b>Evening posts</b> (7:30 PM) say "See you at Mitchell's" for tomorrow or the weekend.</div>
    <div><b>Wed and Thu evenings</b> push weekend brunch.</div>
    <div><b>Every caption</b> ends with 321.338.2909 / www.MitchellsCocoa.com.</div>
    <div><b>Mimosa posts</b> say "21+. Please drink responsibly."</div>
    <div><b>Never:</b> prices, delivery, dinner, flavors, Cocoa Village.</div>
  </section>
  {"".join(cards)}
</main>
<div class="bar"><div class="in"><span class="count" id="count">0 of {len(posts)} approved</span>
  <div class="btns"><button class="copy alt" id="all" type="button">Tick all</button><button class="copy" id="copy" type="button">Copy approval message</button></div></div></div>
<script>
(function(){{
  var boxes=[].slice.call(document.querySelectorAll('.ok input')), KEY='mitchells-month-approved';
  function save(){{try{{localStorage.setItem(KEY,JSON.stringify(boxes.filter(function(b){{return b.checked}}).map(function(b){{return b.dataset.id}})))}}catch(e){{}}}}
  function paint(){{var n=0;boxes.forEach(function(b){{b.closest('.post').classList.toggle('approved',b.checked);if(b.checked)n++}});document.getElementById('count').textContent=n+' of '+boxes.length+' approved'}}
  try{{var s=JSON.parse(localStorage.getItem(KEY)||'[]');boxes.forEach(function(b){{b.checked=s.indexOf(b.dataset.id)>=0}})}}catch(e){{}}
  boxes.forEach(function(b){{b.addEventListener('change',function(){{save();paint()}})}});
  document.getElementById('all').addEventListener('click',function(){{var all=boxes.every(function(b){{return b.checked}});boxes.forEach(function(b){{b.checked=!all}});save();paint();this.textContent=all?'Tick all':'Untick all'}});
  document.querySelectorAll('.tab').forEach(function(t){{t.addEventListener('click',function(){{var post=t.closest('.post');post.querySelectorAll('.tab').forEach(function(x){{x.classList.toggle('on',x===t)}});post.querySelectorAll('.pane').forEach(function(p){{p.hidden=p.id!==t.dataset.pane}})}})}});
  document.getElementById('copy').addEventListener('click',function(){{
    var ok=boxes.filter(function(b){{return b.checked}}).map(function(b){{return b.dataset.id.replace('mitchells-','')}}), no=boxes.filter(function(b){{return !b.checked}}).map(function(b){{return b.dataset.id.replace('mitchells-','')}});
    var msg=no.length===0?'Approve all Mitchell\\'s posts (Oct 8 - Nov 7).':'Approve Mitchell\\'s posts: '+ok.join(', ')+'. Hold: '+no.join(', ')+'.';
    var btn=this;
    try{{navigator.clipboard.writeText(msg).then(function(){{btn.textContent='Copied. Paste it in chat'}},function(){{prompt0(msg)}})}}catch(e){{prompt0(msg)}}
    function prompt0(m){{btn.textContent='Copy failed: '+m}}
  }});
  paint();
}})();
</script>
'''
os.makedirs(os.path.join(ROOT, "content/review"), exist_ok=True)
out = os.path.join(ROOT, "content/review/mitchells-month.html")
open(out, "w").write(page)
print(out, round(os.path.getsize(out) / 1e6, 1), "MB")
