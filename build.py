#!/usr/bin/env python3
"""Build buyenglishart.com static site from data/*.json. Shopify-shaped URLs."""
import json, html, pathlib, datetime

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / "site"
DATA = ROOT / "data"
DOMAIN = "https://buyenglishart.com"
KLAVIYO_KEY = "Rk2YCF"
KLAVIYO_LIST = "TQeMdY"
TODAY = datetime.date.today().isoformat()

def esc(s): return html.escape(s or "", quote=True)

SIGNUP = f"""
<section class="signup">
  <h2>When the prints are ready</h2>
  <p>Buy English Art opens in 2027 with open-edition prints of the paintings on this site. One email when it does, and a story about a painting now and then. No offers, no noise.</p>
  <form id="bea-signup" onsubmit="return beaSub(event)">
    <input type="email" name="email" required placeholder="Your email" aria-label="Email address">
    <button type="submit">Keep me posted</button>
  </form>
  <div class="ok" id="bea-ok">Thank you — you are on the list.</div>
</section>
<script>
function beaSub(e){{e.preventDefault();var f=e.target,em=f.email.value;
var body={{data:{{type:"subscription",attributes:{{profile:{{data:{{type:"profile",attributes:{{email:em}}}}}},custom_source:"buyenglishart.com early list"}},relationships:{{list:{{data:{{type:"list",id:"{KLAVIYO_LIST}"}}}}}}}}}};
fetch("https://a.klaviyo.com/client/subscriptions/?company_id={KLAVIYO_KEY}",{{method:"POST",headers:{{"Content-Type":"application/json","revision":"2024-10-15"}},body:JSON.stringify(body)}})
.then(function(){{f.style.display="none";document.getElementById("bea-ok").style.display="block";}})
.catch(function(){{document.getElementById("bea-ok").textContent="Something went wrong — please try again.";document.getElementById("bea-ok").style.display="block";}});
return false;}}
</script>
"""

def layout(title, desc, canonical, body, schema=None, og_image=None):
    schema_tag = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>' if schema else ""
    og = f'<meta property="og:image" content="{esc(og_image)}">' if og_image else ""
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{esc(canonical)}">
{og}
<link rel="stylesheet" href="/assets/site.css">
{schema_tag}
</head>
<body>
<header class="site"><div class="in">
  <a class="brand" href="/">Buy English Art</a>
  <nav><a href="/pages/artists">Artists</a><a href="/blogs/news">Journal</a><a href="/pages/about">About</a></nav>
</div></header>
<main>
{body}
{SIGNUP}
</main>
<footer class="site"><div class="in">
  Buy English Art is part of the family of <a href="https://buyirishart.com">Buy Irish Art</a> and <a href="https://buyscottishart.com">Buy Scottish Art</a> · Dublin, Ireland · Images of works in the public domain are reproduced courtesy of the collections that hold them, credited beneath each one.
</div></footer>
</body>
</html>
"""

def artist_page(a):
    slug = a["slug"]
    canonical = f"{DOMAIN}/pages/{slug}"
    works_html = []
    for w in a["works"]:
        works_html.append(f"""
<article class="work" id="{esc(w['slug'])}">
  <figure>
    <img src="{esc(w['image'])}" alt="{esc(w['title'])} by {esc(a['name'])}, {esc(w['date'])}" loading="lazy">
    <figcaption>{esc(w['title'])}, {esc(w['date'])}. {esc(w['medium'])}{', ' + esc(w['dims']) if w.get('dims') else ''}. {esc(w['credit'])}</figcaption>
  </figure>
  <h3>{esc(w['title'])}</h3>
  {''.join(f'<p>{esc(p)}</p>' for p in w['text'])}
</article>""")
    body = f"""
<h1>{esc(a['name'])}</h1>
<p class="dates">{esc(a['dates'])}</p>
{''.join(f'<p>{esc(p)}</p>' for p in a['intro'])}
<h2>Life</h2>
{''.join(f'<p>{esc(p)}</p>' for p in a['life'])}
<h2>Works</h2>
{''.join(works_html)}
<h2>Sources</h2>
<ul>{''.join(f'<li><a href="{esc(s["url"])}" rel="nofollow">{esc(s["label"])}</a></li>' for s in a['sources'])}</ul>
"""
    schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": a["name"],
        "birthDate": a["birth"], "deathDate": a["death"],
        "nationality": "English",
        "jobTitle": "Painter",
        "url": canonical,
        "sameAs": a.get("sameAs", []),
    }
    works_schema = [{
        "@context": "https://schema.org", "@type": "VisualArtwork",
        "name": w["title"], "creator": {"@type": "Person", "name": a["name"]},
        "dateCreated": w["date"], "artMedium": w["medium"], "artform": "Painting",
        "image": w["image"], "url": f"{canonical}#{w['slug']}",
        "locationCreated": w.get("where", ""), "copyrightNotice": "Public domain",
        "creditText": w["credit"],
    } for w in a["works"]]
    page = layout(f"{a['name']} — life, paintings and where they hang | Buy English Art",
                  a["meta"], canonical, body, schema=[schema] + works_schema, og_image=a["works"][0]["image"])
    out = SITE / "pages" / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    return canonical

def article_page(art):
    canonical = f"{DOMAIN}/blogs/news/{art['slug']}"
    body = f"""
<h1>{esc(art['title'])}</h1>
<p class="dates">{esc(art['date_display'])}</p>
<figure><img src="{esc(art['image'])}" alt="{esc(art['image_alt'])}"><figcaption>{esc(art['image_caption'])}</figcaption></figure>
{art['body_html']}
<h2>Sources</h2>
<ul>{''.join(f'<li><a href="{esc(s["url"])}" rel="nofollow">{esc(s["label"])}</a></li>' for s in art['sources'])}</ul>
"""
    schema = {"@context": "https://schema.org", "@type": "Article", "headline": art["title"],
              "datePublished": art["date"], "author": {"@type": "Organization", "name": "Buy English Art"},
              "publisher": {"@type": "Organization", "name": "Buy English Art"}, "image": art["image"],
              "mainEntityOfPage": canonical, "description": art["meta"]}
    out = SITE / "blogs" / "news" / art["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(layout(f"{art['title']} | Buy English Art", art["meta"], canonical, body, schema=schema, og_image=art["image"]))
    return canonical

def index_pages(artists, articles):
    cards = "".join(f"""
<a class="card" href="/pages/{esc(a['slug'])}"><img src="{esc(a['works'][0]['image'])}" alt="{esc(a['works'][0]['title'])} by {esc(a['name'])}" loading="lazy"><h3>{esc(a['name'])}</h3><p>{esc(a['dates'])}</p></a>""" for a in artists)
    home = f"""
<h1>English painting, told plainly</h1>
<p>Five painters, their best pictures, and where each one hangs. Every fact on this site is checked against the collection that holds the work. Prints follow in 2027.</p>
<div class="grid">{cards}</div>
<h2>From the journal</h2>
<ul>{''.join(f'<li><a href="/blogs/news/{esc(x["slug"])}">{esc(x["title"])}</a></li>' for x in articles)}</ul>
"""
    (SITE / "index.html").write_text(layout("Buy English Art — English painters, their paintings and where they hang",
        "Turner, Constable, Stubbs, Gainsborough and Wright of Derby: lives, verified works and where each painting hangs. Open-edition prints coming 2027.", DOMAIN + "/", home, og_image=artists[0]["works"][0]["image"]))
    artists_body = f"<h1>Artists</h1><div class=\"grid\">{cards}</div>"
    (SITE / "pages" / "artists").mkdir(parents=True, exist_ok=True)
    (SITE / "pages" / "artists" / "index.html").write_text(layout("English artists | Buy English Art", "The painters on Buy English Art, with verified works and where they hang.", DOMAIN + "/pages/artists", artists_body))
    journal_body = f"<h1>Journal</h1><ul>{''.join(f'<li><a href=\"/blogs/news/{esc(x["slug"])}\">{esc(x["title"])}</a> — {esc(x["meta"])}</li>' for x in articles)}</ul>"
    (SITE / "blogs" / "news" / "index.html").write_text(layout("Journal | Buy English Art", "Essays on English painting.", DOMAIN + "/blogs/news", journal_body))
    about = """
<h1>About</h1>
<p>Buy English Art is a reference site for English painting that will become a print shop in 2027. It is run from Dublin by the people behind Buy Irish Art, founded 2016, and Buy Scottish Art.</p>
<p>The method is the same on every page: the works are chosen from collections that make their public-domain holdings freely available, the facts are checked against the holding collection's own record, and where a fact is contested or uncertain the page says so. Naming a gallery is a statement of where the original hangs, not a claim of endorsement.</p>
<p>When the prints arrive they will be open edition, printed to order on archival paper, framed or unframed, and shipped worldwide.</p>
"""
    (SITE / "pages" / "about").mkdir(parents=True, exist_ok=True)
    (SITE / "pages" / "about" / "index.html").write_text(layout("About | Buy English Art", "What Buy English Art is, how its pages are checked, and what comes in 2027.", DOMAIN + "/pages/about", about))

def sitemap(urls):
    items = "".join(f"<url><loc>{esc(u)}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    (SITE / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>\n')
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    (SITE / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")

def main():
    artists = [json.loads(p.read_text()) for p in sorted((DATA / "artists").glob("*.json"))]
    articles = [json.loads(p.read_text()) for p in sorted((DATA / "articles").glob("*.json"))]
    urls = [DOMAIN + "/", DOMAIN + "/pages/artists", DOMAIN + "/pages/about", DOMAIN + "/blogs/news"]
    for a in artists: urls.append(artist_page(a))
    for x in articles: urls.append(article_page(x))
    index_pages(artists, articles)
    sitemap(urls)
    print(f"built {len(artists)} artist pages, {len(articles)} articles, {len(urls)} urls")

if __name__ == "__main__":
    main()
