"""Build a dependency-free static academic homepage from CMS-managed JSON."""
from pathlib import Path
import json, html, shutil
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'_site'
OUT.mkdir(exist_ok=True)
def load(n): return json.loads((ROOT/'content'/f'{n}.json').read_text())
def esc(x): return html.escape(str(x),quote=True)
def url(x):
 x=str(x or '')
 if urlsplit(x).scheme not in ('','https','http','mailto'): raise ValueError('Unsupported URL scheme')
 return esc(x)
def link(x,label,cls=''): return f'<a class="{cls}" href="{url(x)}">{esc(label)} <span aria-hidden="true">↗</span></a>' if x else ''
p=load('profile');rs=load('research');ps=load('publications');cs=load('conferences')
research=''
for i,r in enumerate(rs):
 research+=f'''<article class="research-row"><div class="research-text"><div class="eyebrow">0{i+1} / {esc(r['tag'])}</div><h3>{esc(r['title'])}</h3><p>{esc(r['summary'])}</p><div class="status">{esc(r['status'])}</div>{link(r.get('link'),'Read paper','text-link')}</div><figure><a href="{url(r['image'])}" aria-label="Open full-size research figure"><img src="{url(r['image'])}" alt="{esc(r['alt'])}" loading="lazy"></a><figcaption>{esc(r['caption'])}</figcaption></figure></article>'''
publications=''
for i,r in enumerate(sorted(ps,key=lambda r:int(r['year']),reverse=True)):
 authors=esc(r['authors']).replace('Jae Jung Kim','<strong>Jae Jung Kim</strong>')
 publications+=f'''<article class="publication"><div class="pub-year">{esc(r['year'])}</div><div><h3>{esc(r['title'])}</h3><p class="authors">{authors}</p><p class="journal"><em>{esc(r['journal'])}</em> {esc(r['volume'])}, {esc(r['article'])} ({esc(r['year'])}).</p><p class="note">{esc(r.get('note',''))}</p><div class="paper-links">{link(r.get('doi'),'DOI')}{link(r.get('pdf'),'PDF')}</div></div></article>'''
conferences=''
for r in sorted(cs,key=lambda r:r['start'],reverse=True):
 conferences+=f'''<article class="conference"><div class="conf-date">{esc(r['date'])}<span class="upcoming" data-start="{esc(r['start'])}" hidden>Upcoming</span></div><div><h3>{esc(r['title'])}</h3><p>{esc(r['event'])}</p><span class="muted">{esc(r['location'])}</span></div></article>'''
education=''.join(f'<div class="education"><span>{esc(e["period"])}</span><div><h3>{esc(e["degree"])}</h3><p>{esc(e["institution"])}</p><p class="muted">{esc(e["detail"])}</p></div></div>' for e in p['education'])
css=(ROOT/'style.css').read_text()
page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(p['name'])} | Combustion &amp; Reduced-Order Modeling</title><meta name="description" content="{esc(p['intro'])}"><meta name="theme-color" content="#153b54"><style>{css}</style></head><body>
<a class="skip" href="#main">Skip to content</a><header><nav aria-label="Main navigation"><a class="wordmark" href="#home">{esc(p['name'])}<span> / UNIST</span></a><div class="nav-links"><a href="#research">Research</a><a href="#publications">Publications</a><a href="#conferences">Conferences</a><a href="#about">About</a></div></nav></header>
<main id="main"><section class="hero" id="home"><div class="eyebrow">COMPUTATIONAL COMBUSTION · REDUCED-ORDER MODELING</div><h1>{esc(p['name'])}<span>Understanding reacting flows.<br>Making their simulation more efficient.</span></h1><div class="hero-bottom"><div class="affiliation"><strong>{esc(p['role'])}</strong><span>{esc(p['affiliation'])}</span><span>{esc(p['lab'])}</span></div><div class="intro"><p>{esc(p['intro'])}</p><div class="contact-links">{link('mailto:'+p['email'],'Email')}{link(p['scholar'],'Google Scholar')}{link(p['github'],'GitHub')}{link(p.get('cv'),'CV')}</div></div></div></section>
<section id="research"><div class="section-heading"><h2>Research highlights</h2><span>Methods &amp; physical insights</span></div>{research}</section>
<section id="publications"><div class="section-heading"><h2>Publications</h2>{link(p['scholar'],'Google Scholar')}</div>{publications}</section>
<section id="conferences"><div class="section-heading"><h2>Conference presentations</h2><span>Talks &amp; research exchange</span></div>{conferences}</section>
<section id="about"><div class="section-heading"><h2>Background</h2><span>Education &amp; experience</span></div><div class="about-grid"><div>{education}</div><aside><h3>Research experience</h3><p>Graduate Researcher<br>CCERL, UNIST · 2023–Present</p><p>Undergraduate Research Intern<br>CCERL, UNIST · 2020–2023</p><h3>Tools &amp; methods</h3><p>OpenFOAM · ANSYS Fluent · COMSOL </p><p>C++ · Fortran · Python · MATLAB</p></aside></div></section>
</main><footer><div><strong>{esc(p['name'])}</strong><span>{esc(p['affiliation'])}</span></div>{link('mailto:'+p['email'],p['email'])}<a href="#home">Back to top ↑</a></footer>
<script>document.querySelectorAll('[data-start]').forEach(el=>{{el.hidden=el.dataset.start<new Date().toLocaleDateString('en-CA',{{timeZone:'Asia/Seoul'}})}});</script></body></html>'''
(OUT/'index.html').write_text(page)
(OUT/'.nojekyll').touch()
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
print(f'Built {len(rs)} highlights, {len(ps)} publications, {len(cs)} conferences → {OUT}')
