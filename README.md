_____________________________________________________________________________________________________________
# SWAMI - Simple Web Accessible Movie Interface

## What is SWAMI?

SWAMI is a lightweight, Dockerized web UI for cataloguing your Movies directory—fast, filterable, and fully browser-based with zero media scraping. It's designed for plug-and-play deployment on Unraid (or any system with Docker), respecting your file structure while being safe and predictable. You control when to perform a full catalogue update, and since SWAMI does not scrape media or read file contents, it is fast and efficient even on large libraries.

---

### What's the point of this?

Sometimes you just want a quick, no-fuss way to check the contents of your media library—whether by searching for a specific title, browsing by year or resolution, or filtering by your own organization tags. SWAMI is designed for speed and convenience: 

- No need to open your media front end or library manager.
- No need to manually browse an Unraid file share (which may require spinning up disks in a large array).
- See your movie collection anytime, from any device with a browser, with instant search and filter.

SWAMI is the perfect tool for instant, read-only browsing of your Unraid Movies directory (or any similar media structure) with minimal overhead.

---

## Catalogue Structure Logic

### 🚦 How SWAMI indexes your files and folders

- **Top-level only:** SWAMI walks only the *top level* of your Movies directory (`MOVIE_PATH`).
- **Regular folders:** If a folder's name is NOT listed as an Ignored Label, only the folder's name is included in the catalogue (never its contents).
- **Label folders:** If a folder IS listed as an Ignored Label (e.g. `01BluRay`, `02UHD4K`, genres, etc.), SWAMI includes all files and folders immediately inside that label-folder, but never goes deeper.
- **Files:** Any file sitting directly in the movie root, or directly inside a label/genre folder, is included.

---

### 💡 Example Structure & Result

Suppose your layout is:

```
Movies/
  ├─ Movie1.2020.1080p.mkv
  ├─ Movie2.1981.BluRay/           # (regular folder)
  │     └─ otherfolder/            # NOT included
  ├─ 01BluRay/                     # <--- Ignored Label
  │     ├─ Movie3.1971.BluRay.mkv
  │     └─ Movie4.1981.BluRay/
  │           └─ otherfolder/      # NOT included
  │                └─ otherfile.m2ts    # NOT included
  │                └─ foo.txt           # NOT included
  └─ 02UHD4K/                      # <--- Ignored Label
        ├─ Action/                 # <--- Also Ignored Label (genre)
        │     ├─ ActionMovie1.2021.UHD 4K.mkv
        │     └─ ActionMovie2.1961.UHD 4K/
        │           └─ bar.txt          # NOT included
        ├─ Comedy/                 # <--- Also Ignored Label (genre)
        │     └─ ComedyMovie1.1992.UHD 4K.mkv
        └─ SciFi/                  # <--- Also Ignored Label (genre)
              ├─ SciFiMovie1.2001.UHD 4K/
              │      └─ deepfile.txt     # NOT included
              ├─ SciFiMovie2.1999.UHD 4K.mkv
              └─ SciFiMovie3.2012.UHD 4K.mkv
```

**If your Ignored Labels are:**  
`01BluRay,02UHD4K,Action,Comedy,SciFi`

**Your catalogue will contain:**
- Movie1.2020.1080p.mkv  
- Movie2.1981.BluRay  
- Movie3.1971.BluRay.mkv  
- Movie4.1981.BluRay  
- ActionMovie1.2021.UHD 4K.mkv  
- ActionMovie2.1961.UHD 4K  
- ComedyMovie1.1992.UHD 4K.mkv  
- SciFiMovie1.2001.UHD 4K  
- SciFiMovie2.1999.UHD 4K.mkv  
- SciFiMovie3.2012.UHD 4K.mkv  

- Files/folders inside regular folders (`Movie2.1981.BluRay/otherfolder/`) are **not included**.
- Only the top-level files/folders inside any Ignored Label folder are included.
- Anything deeper is skipped.

---

## How Filtering Works

- **Filter buttons** (BluRay, UHD 4K, 1080p, 720p, other) are configured via the `UI Filters` field (`FILTER_LABELS`) in the template.

**Filters are simple text matches:**  
SWAMI does *not* scrape, inspect, or analyze the video files themselves — it only evaluates the file/folder _names_.

### Example for Custom Filters

In the template:
```
FILTER_LABELS=BluRay,UHD 4K,1080p,720p
```
If your folder or filename contains any of these (case-insensitive), it can be filtered in the web UI.  
If not, that filter will show no results. There is no scraping—just name matching!

---

## Dark/Light Mode

SWAMI’s catalogue page defaults to dark mode, but includes a toggle for switching to normal (light) mode instantly. This is a user preference and does not require redeploying the container.

---

## Why This Approach?

- **Simplicity:** No recursion settings, no unpredictable results.
- **Predictability:** You can use label/genre folders as bins, and SWAMI always only lists up to one level deep.
- **Safety:** SWAMI never reads or lists files within regular movie title folders (unless those are in Ignored Labels).

---
Documentation & Support

All our documentation is located at https://github.com/hdagar/unraid_apps

Be gentle, this is my first docker container!