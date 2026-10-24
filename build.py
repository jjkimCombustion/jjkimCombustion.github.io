"""Build a dependency-free static academic homepage from CMS-managed JSON."""
from pathlib import Path
import json, html, shutil
from collections import defaultdict
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'_site'
OUT.mkdir(exist_ok=True)
def load(n): return json.loads((ROOT/'content'/f'{n}.json').read_text(encoding='utf-8'))
def esc(x): return html.escape(str(x if x is not None else ''),quote=True)
def url(x):
 x=str(x or '')
 if urlsplit(x).scheme not in ('','https','http','mailto'): raise ValueError('Unsupported URL scheme')
 return esc(x)
def link(x,label,cls=''): return f'<a class="{cls}" href="{url(x)}">{esc(label)} <span aria-hidden="true">↗</span></a>' if x else ''
def record(value):
 return defaultdict(str, {k: ('' if v is None else v) for k, v in value.items()})
p=record(load('profile'))
rs=[record(r) for r in load('research')]
ps=[record(r) for r in load('publications')]
cs=[record(r) for r in load('conferences')]
s=record(load('site'))
# Lists may be omitted or cleared by the CMS.
for key in ('education', 'experience', 'tools', 'languages'):
 p[key]=p[key] or []
p['education']=[record(e) for e in p['education']]
experience=''.join('<p>'+esc(e.get('role'))+'<br>'+esc(' · '.join(str(e.get(k) or '') for k in ('institution','period') if e.get(k)))+'</p>' for e in p['experience'])
tools='<p>'+esc(' · '.join(p['tools']))+'</p>' if p['tools'] else ''
languages='<p>'+esc(' · '.join(p['languages']))+'</p>' if p['languages'] else ''
headline='<br>'.join(esc(line) for line in p['headline'].splitlines())
short_affiliation=' / '+esc(p['short_affiliation']) if p['short_affiliation'] else ''
page_title=esc(' | '.join(v for v in (p['name'],s['title_suffix']) if v))
def year_key(r):
 try: return int(r.get('year') or 0)
 except (TypeError, ValueError): return 0

research=''
for i,r in enumerate(rs):
 research+=f'''<article class="research-row"><div class="research-text"><div class="eyebrow">{i+1:02d} / {esc(r['tag'])}</div><h3>{esc(r['title'])}</h3><p>{esc(r['summary'])}</p><div class="status">{esc(r['status'])}</div>{link(r.get('link'),s['research_link_label'],'text-link')}</div><figure><a href="{url(r['image'])}" aria-label="Open full-size research figure"><img src="{url(r['image'])}" alt="{esc(r['alt'])}" loading="lazy"></a><figcaption>{esc(r['caption'])}</figcaption></figure></article>'''
publications=''
for i,r in enumerate(sorted(ps,key=lambda r:year_key(r),reverse=True)):
 authors=esc(r['authors']).replace(esc(p['name']),'<strong>'+esc(p['name'])+'</strong>') if p['name'] else esc(r['authors'])
 details=', '.join(str(r[k]) for k in ('volume','article') if r[k])
 citation=' '.join(v for v in (esc(details), '('+esc(r['year'])+')' if r['year'] else '') if v)
 publications+=f'''<article class="publication"><div class="pub-year">{esc(r['year'])}</div><div><h3>{esc(r['title'])}</h3><p class="authors">{authors}</p><p class="journal"><em>{esc(r['journal'])}</em> {citation}.</p><p class="note">{esc(r.get('note',''))}</p><div class="paper-links">{link(r.get('doi'),s['doi_label'])}{link(r.get('pdf'),s['pdf_label'])}</div></div></article>'''
conferences=''
for r in sorted(cs,key=lambda r:r['start'],reverse=True):
 conferences+=f'''<article class="conference"><div class="conf-date">{esc(r['date'])}<span class="upcoming" data-start="{esc(r['start'])}" hidden>{esc(s['upcoming_label'])}</span></div><div><h3>{esc(r['title'])}</h3><p>{esc(r['event'])}</p><span class="muted">{esc(r['location'])}</span></div></article>'''
education=''.join(f'<div class="education"><span>{esc(e["period"])}</span><div><h3>{esc(e["degree"])}</h3><p>{esc(e["institution"])}</p><p class="muted">{esc(e["detail"])}</p></div></div>' for e in p['education'])
css=(ROOT/'style.css').read_text(encoding='utf-8')
page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{page_title}</title><meta name="description" content="{esc(p['intro'])}"><meta name="theme-color" content="#153b54"><style>{css}</style></head><body>
<a class="skip" href="#main">Skip to content</a><header><nav aria-label="Main navigation"><a class="wordmark" href="#home">{esc(p['name'])}<span>{short_affiliation}</span></a><div class="nav-links"><a href="#research">{esc(s['nav_research'])}</a><a href="#publications">{esc(s['nav_publications'])}</a><a href="#conferences">{esc(s['nav_conferences'])}</a><a href="#about">{esc(s['nav_about'])}</a></div></nav></header>
<main id="main"><section class="hero" id="home"><div class="eyebrow">{esc(p['research_fields'])}</div><h1>{esc(p['name'])}<span>{headline}</span></h1><div class="hero-bottom"><div class="affiliation"><strong>{esc(p['role'])}</strong><span>{esc(p['affiliation'])}</span><span>{esc(p['lab'])}</span></div><div class="intro"><p>{esc(p['intro'])}</p><div class="contact-links">{link(('mailto:'+p['email']) if p['email'] else '',s['email_label'])}{link(p['scholar'],s['scholar_label'])}{link(p['github'],s['github_label'])}{link(p.get('cv'),s['cv_label'])}</div></div></div></section>
<section id="research"><div class="section-heading"><h2>{esc(s['research_title'])}</h2><span>{esc(s['research_subtitle'])}</span></div>{research}</section>
<section id="publications"><div class="section-heading"><h2>{esc(s['publications_title'])}</h2>{link(p['scholar'],s['scholar_label'])}</div>{publications}</section>
<section id="conferences"><div class="section-heading"><h2>{esc(s['conferences_title'])}</h2><span>{esc(s['conferences_subtitle'])}</span></div>{conferences}</section>
<section id="about"><div class="section-heading"><h2>{esc(s['about_title'])}</h2><span>{esc(s['about_subtitle'])}</span></div><div class="about-grid"><div>{education}</div><aside><h3>{esc(s['experience_title'])}</h3>{experience}<h3>{esc(s['tools_title'])}</h3>{tools}{languages}</aside></div></section>
</main><footer><div><strong>{esc(p['name'])}</strong><span>{esc(p['affiliation'])}</span></div>{link(('mailto:'+p['email']) if p['email'] else '',p['email'])}<a href="#home">{esc(s['back_to_top'])} ↑</a></footer>
<script>document.querySelectorAll('[data-start]').forEach(el=>{{el.hidden=el.dataset.start<new Date().toLocaleDateString('en-CA',{{timeZone:'Asia/Seoul'}})}});</script></body></html>'''
(OUT/'index.html').write_text(page,encoding='utf-8')
(OUT/'.nojekyll').touch()
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
print(f'Built {len(rs)} highlights, {len(ps)} publications, {len(cs)} conferences → {OUT}')
