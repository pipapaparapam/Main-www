# courtrhythm.com — new site (DRAFT, not deployed)

Static site, no framework, no build step needed to host it. English at `/`, Polish at `/pl/`.

## Files
- `index.html`, `pl/index.html` — home pages (generated)
- `privacy.html`, `pl/polityka-prywatnosci.html` — privacy policy (generated)
- `404.html`, `sitemap.xml` — generated
- `src/strings.py` — every text on the home pages, EN and PL
- `src/privacy.en.html`, `src/privacy.pl.html` — privacy policy text
- `build.py` — regenerates the pages above from `src/`
- `assets/` — CSS, JS, self-hosted fonts, images, QR codes
- `robots.txt`, `site.webmanifest`, `favicon.svg`, `apple-touch-icon.png`
- `CNAME` — for GitHub Pages (`www.courtrhythm.com`)
- `.htaccess` — for OVH only: HTTPS redirect, security headers, caching

## Change text
1. Edit `src/strings.py` (or the privacy files).
2. Run `python build.py`.
3. If you changed CSS or JS, bump `VERSION` in `build.py` first.

## Run locally
```
cd courtrhythm-web
python -m http.server 8000
```
Open http://localhost:8000

## Deploy to GitHub Pages (when approved)
1. Back up the current site repo (download a zip from GitHub, or make a branch `old-site`).
2. Copy all files from this folder into the repo root (keep `CNAME`).
3. Commit and push. In the repo: Settings → Pages → custom domain `www.courtrhythm.com` → tick "Enforce HTTPS".
4. Submit `https://www.courtrhythm.com/sitemap.xml` in Google Search Console.

## Deploy to OVH (later)
Upload everything (including `.htaccess`) to the `www` folder by FTP/SFTP, enable the free SSL certificate in the OVH panel, point DNS of `www` to OVH.

## Before going live
- v8 (23 Oct): no lawyer review planned for release 1. Version lines say "Version 1.0, 25 October 2026": change the date in the four `src/privacy.*` and `src/terms.*` files if the site goes live on another day.
- Deploy only together with the app build that hides age bracket and bio (the policy says the age is never shown).
- Set `PLAY_URL` in `build.py` once the Google Play listing is public, then run `python build.py`. At launch also change `get_p` in `src/strings.py` ("It isn't in the stores yet").
- Add real screenshots/clips (see the comment `SCREENSHOTS` in `build.py`).
- The launch countdown block was removed from the home page in v9 (release plan item 22). `LAUNCH_ISO` in `build.py` is unused; the old block is kept in the v9 report.
