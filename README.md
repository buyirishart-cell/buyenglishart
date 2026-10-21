# buyenglishart.com

Static reference site for Buy English Art. Content lives in `data/` (one JSON per artist and article); `python3 build.py` writes the site into `site/`. Cloudflare Pages deploys `site/` on every push to `main`.

Facts are verified against the holding collection's own record before they go in. Images are linked from the Yale Center for British Art's IIIF server under its public-domain open-access policy and credited beneath each work.
