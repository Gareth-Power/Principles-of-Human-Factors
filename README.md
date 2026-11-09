# Principles of Human Factors - field guide

An HTML field guide made from *Human-Factors-Field-Guide-for-review 3.docx*
(Dr Peter Gogalniceanu). No tracking, no sign-in, no server code: open
`index.html` in a browser (it works from a folder, a USB stick, an intranet
or any static web host).

- `index.html`, `css/guide.css`, `js/app.js` - the app (index, pages, Toolkits, glossary, search with `/`).
- `js/content.js` - **generated** from the Word file. Don't edit it by hand.
- `img/` - the document's own images, resized to web size (WebP).

## Installing as an app (PWA)

Served over **HTTPS**, the guide can be installed on phones and computers
and then works offline. (Opened as a file, it's an ordinary page.)

- `manifest.webmanifest` + `icons/` (the blue HF square, made by
  `python tools/icons.py icons`) - name and icon on the home screen.
- `sw.js` - saves every file on the device on first visit. Its `FILES` list
  must include any new file, and 28 images are assumed (`img/image1..28`).
- `js/install.js` - the screen shown on first launch in a browser:
  **Install the app** (Chrome/Edge open their own install box; iPhone and
  iPad get the Share -> Add to Home Screen steps) or **Use in the browser**.
  The choice is kept in the browser's localStorage on that device only;
  "Install as an app" at the foot of the index brings the screen back.

**Releasing a change:** bump the number in `?v=` in `index.html` *and*
`VERSION` in `sw.js` (keep them the same). Installed copies fetch the new
files the next time they're opened online.

## Updating from a new version of the Word file

Needs Python 3 with Pillow (`python -m pip install Pillow`).

```
mkdir docx && cd docx && tar -xf "../path/to/guide.docx" && cd ..
python tools/convert.py docx blocks.json
python tools/imgs.py docx/word/media img preview
python tools/build.py blocks.json js/content.js img
python tools/check.py blocks.json js/content.js
```

There are **no em dashes** in the app (decided 2026-11-09):
`build.py` turns every one in the document into a spaced hyphen (" - ").

`check.py` must report `paragraphs missing: 0` - it proves every paragraph
of the document is in the app word for word. `build.py` holds the only
hand-made decisions: which paragraphs make up each page (`PAGES`), which are
Tool / Case / Note boxes (`CALLOUTS`, by paragraph number), headings that
Word didn't style as headings (`ROLE`) and the images' alt text (`ALT`). If
paragraphs are added or removed, the paragraph numbers move - re-check those
lists (`convert.py` prints each paragraph with its number).
