#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify, request
import os, json, threading, datetime

# --- CONFIG FROM ENV ---
def get_envlist(key, default=None):
    raw = os.environ.get(key)
    if raw is None:
        return default or []
    return [item.strip() for item in raw.split(',') if item.strip()]

ROOT_DIR = os.environ.get("MOVIE_PATH", "/mnt/user/Movies")
OUTPUT_DIR = os.environ.get("CATALOG_PATH", "/data")
REMOVE_LABELS = get_envlist("REMOVE_LABELS", ["01BluRay", "02UHD4K", ".stfolder", "Action", "Comedy", "SciFi"])
# Filters are now explicitly user-configurable!
CATEGORY_FILTERS = get_envlist("FILTER_LABELS", ["BluRay", "UHD 4K", "1080p", "720p"])
SCAN_LOCK = threading.Lock()

# Flask app
app = Flask(__name__)

# --- UTILITIES ---
def get_output_file():
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"{date_str} Movies Catalogue.json"
    return os.path.join(OUTPUT_DIR, filename)

def cleanup_old_files(keep=2):
    files = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if f.endswith(".json")]
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    for old in files[keep:]:
        try:
            os.remove(old)
            print(f"🧹 Removed old catalogue: {os.path.basename(old)}")
        except Exception as e:
            print(f"⚠️ Could not remove {old}: {e}")

def latest_catalog_file():
    if not os.path.exists(OUTPUT_DIR):
        return None
    json_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".json")]
    if not json_files:
        return None
    latest = max(json_files, key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)))
    return os.path.join(OUTPUT_DIR, latest)

# --- CORE SCANNER ---
def build_catalog(root):
    catalog = []
    if not os.path.exists(root):
        print(f"❌ Movie path {root} does not exist.")
        return catalog
    for entry in os.scandir(root):
        if entry.name.lower().startswith("syncthing"):
            continue
        if not entry.is_dir():
            catalog.append(entry.name)
            continue
        if entry.name in REMOVE_LABELS:
            for subentry in os.scandir(entry.path):
                if subentry.is_file() or subentry.is_dir():
                    catalog.append(subentry.name)
            continue
        catalog.append(entry.name)
    return sorted(catalog, key=str.casefold)

def run_scan():
    with SCAN_LOCK:
        print("🔄 Scanning movie catalog...")
        catalog = build_catalog(ROOT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = get_output_file()
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({"last_scan": datetime.datetime.now().isoformat(),"entries": catalog}, f, indent=2)
        print(f"✅ Catalogued {len(catalog)} entries → {output_file}")
        cleanup_old_files(keep=2)
        return catalog, output_file

def load_latest_catalog():
    latest = latest_catalog_file()
    if not latest:
        return run_scan()[0], datetime.datetime.now().isoformat()
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("entries", []), data.get("last_scan", "Unknown")

# --- API ROUTES ---
@app.route("/data")
def data():
    entries, last_scan = load_latest_catalog()
    return jsonify({
        "entries": entries,
        "last_scan": last_scan,
        "category_filters": CATEGORY_FILTERS
    })

@app.route("/rescan", methods=["POST"])
def rescan():
    threading.Thread(target=run_scan).start()
    return jsonify({"status": "rescan started"})

# --- WEB UI ---
@app.route("/")
def index():
    # Pass the CATEGORY_FILTERS as JSON for flexible front-end filters
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>SWAMI Movie Catalogue Search</title>
<style>
body { font-family: Arial, sans-serif; margin: 2rem; background: #181818; color: #f0f0f0; transition: background 0.2s, color 0.2s; }
body.light { background: #fff; color: #181818; }
header { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem; flex-wrap: wrap; }
#search { width: 33%; padding: 0.6rem; font-size: 1rem; border-radius: 8px; border: 1px solid #555; background: #282828; color: #f0f0f0; }
body.light #search { background: #f9f9f9; color: #282828; border: 1px solid #ccc; }
#rescan, #clear-filters { padding: 0.5rem 0.9rem; border: none; border-radius: 8px; cursor: pointer; }
#rescan { background: #d9534f; color: white; }
#rescan:hover { background: #b52b27; }
#rescan:disabled { background: #555; cursor: not-allowed; }
#clear-filters { background: #5bc0de; color: white; }
#clear-filters:hover { background: #31b0d5; }
#last-scan { font-size: 0.95rem; margin-right: 1rem;}
#stats { display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.9rem; margin-left: auto; justify-content: center;}
ul { list-style: none; padding: 0; margin-top: 1rem;}
li { background: #282828; padding: 0.4rem 0.8rem; margin: 0.2rem 0; border-radius: 6px; }
body.light li { background: #f2f2f2; color: #111; }
.index-btn.active, .category-btn.active, .stat.active { background: #00adee; color: #00121B !important; }
.index-btn, .category-btn, .stat { margin: 0 0.2rem 0.2rem 0; cursor: pointer; border-radius: 4px; padding: 0.3rem 0.6rem; background: #333; color: #f0f0f0; border: none; }
body.light .index-btn, body.light .category-btn, body.light .stat { background: #e0e0e0; color: #181818; }
#alphabet { margin-top: 0.5rem; display: flex; flex-wrap: wrap; gap: 0.3rem; justify-content: center; }
#theme-toggle {
  margin-left: 0.7em; background: #282828;
  color: #00adee; font-size: 1.4em;
  border: none; border-radius: 50%; width: 2.25em; height: 2.25em; cursor: pointer; transition: background 0.2s;
  display: flex; align-items: center; justify-content: center;
}
body.light #theme-toggle { background: #ddd; color: #b34700; }
</style>
</head>
<body>
<header>
  <input type="text" id="search" 
         placeholder="Type to search..." 
         autofocus
         autocomplete="off"
         autocorrect="off"
         autocapitalize="off"
         spellcheck="false" />
  <button id="rescan">Refresh Library</button>
  <button id="clear-filters">Clear All Filters</button>
  <div id="last-scan">Loading last scan...</div>
  <div id="stats"></div>
  <button id="theme-toggle" title="Toggle light/dark mode">☀️</button>
</header>

<div id="alphabet"></div>
<ul id="results"></ul>

<script>
let files = [];
let lastScan = "Unknown";
let categoryFilters = {{ category_filters|tojson }};
const search = document.getElementById('search');
const results = document.getElementById('results');
const rescanBtn = document.getElementById('rescan');
const clearFiltersBtn = document.getElementById('clear-filters');
const lastScanLabel = document.getElementById('last-scan');
const statsDiv = document.getElementById('stats');
const alphabetDiv = document.getElementById('alphabet');
const themeToggleBtn = document.getElementById('theme-toggle');
let currentCategoryFilter=null, currentIndexFilter=null;

// ---- THEME TOGGLE ----
function applyTheme(theme) {
    document.body.className = theme;
    localStorage.setItem('swami-theme', theme);
    themeToggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
}
themeToggleBtn.onclick = function() { applyTheme(document.body.className === 'dark' ? 'light' : 'dark'); };
const savedTheme = localStorage.getItem('swami-theme');
if(savedTheme){ applyTheme(savedTheme); }
else { const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches; applyTheme(prefersDark ? 'dark' : 'light'); }

// ---- FETCH DATA ----
async function loadData() {
  const res = await fetch('/data');
  const data = await res.json();
  files = data.entries;
  lastScan = data.last_scan;
  if(data.category_filters) categoryFilters=data.category_filters;
  lastScanLabel.textContent = "📅 Last Scan: "+new Date(lastScan).toLocaleString();
  updateStats();
  renderAlphabet();
  render();
}

// --- STATS / CATEGORY FILTERS ---
function updateStats(){
  const total = files.length;
  const statsArr = [{name:"Total", val:total,cat:null}];
  categoryFilters.forEach(filt=>{
    const count = files.filter(f=>f.toLowerCase().includes(filt.toLowerCase())).length;
    statsArr.push({name:filt, val:count, cat:filt.toLowerCase()});
  });
  const other = total - statsArr.slice(1).reduce((sum,s)=>sum+s.val,0);
  statsArr.push({name:"Other", val:other, cat:"other"});
  statsDiv.innerHTML="";
  statsArr.forEach(s=>{
    const b=document.createElement('button');
    b.textContent=`${s.name}: ${s.val}`;
    if(s.cat) b.className="stat";
    if(currentCategoryFilter===s.cat) b.classList.add("active");
    if(s.cat) b.dataset.cat=s.cat;
    b.addEventListener('click',()=>{
      currentCategoryFilter=(currentCategoryFilter===b.dataset.cat)?null:b.dataset.cat;
      render();
      updateStats();
    });
    statsDiv.appendChild(b);
  });
}

// --- ALPHABET BAR / INDEX FILTER ---
function renderAlphabet(){
  const letters=["0-9",..."ABCDEFGHIJKLMNOPQRSTUVWXYZ"];
  alphabetDiv.innerHTML="";
  letters.forEach(l=>{
    const b=document.createElement('button');
    b.textContent=l; b.className="index-btn"; b.dataset.index=l;
    if(currentIndexFilter===l) b.classList.add("active");
    b.addEventListener('click',()=>{
      currentIndexFilter=(currentIndexFilter===b.dataset.index)?null:b.dataset.index;
      render();
      renderAlphabet();
    });
    alphabetDiv.appendChild(b);
  });
}

// --- RESULTS RENDERING ---
function render(q=search.value){
  results.innerHTML="";
  let filtered = files.slice();
  if(currentCategoryFilter){
    if(currentCategoryFilter==="other")
      filtered=filtered.filter(f=>{
        // Not matching *any* category filter
        return !categoryFilters.some(cat=>f.toLowerCase().includes(cat.toLowerCase()));
      });
    else
      filtered=filtered.filter(f=>f.toLowerCase().includes(currentCategoryFilter));
  }
  if(currentIndexFilter){
    if(currentIndexFilter==="0-9") filtered=filtered.filter(f=>/^[0-9]/.test(f));
    else filtered=filtered.filter(f=>f.toUpperCase().startsWith(currentIndexFilter));
  }
  if(q) filtered=filtered.filter(f=>f.toLowerCase().includes(q.toLowerCase()));
  filtered.slice(0,200).forEach(f=>{
    const li=document.createElement('li'); li.textContent=f; results.appendChild(li);
  });
}

// --- EVENT LISTENERS ---
search.addEventListener('input',()=>render());

rescanBtn.addEventListener('click', async ()=>{
  const lastScanTime=new Date(lastScan);
  if((Date.now()-lastScanTime.getTime())<3600000){
    if(!confirm("⚠️ Library was scanned within the last hour. Proceed?")) return;
  }
  rescanBtn.disabled=true; rescanBtn.textContent="Rescanning...";

  await fetch('/rescan',{method:'POST'});

  // Polling for automatic refresh
  let scanPollingInterval = setInterval(async ()=>{
    const res = await fetch('/data');
    const data = await res.json();
    if(new Date(data.last_scan).getTime() !== new Date(lastScan).getTime()){
      files = data.entries;
      lastScan = data.last_scan;
      lastScanLabel.textContent = "📅 Last Scan: "+new Date(lastScan).toLocaleString();
      updateStats();
      renderAlphabet();
      render();
      rescanBtn.disabled=false; 
      rescanBtn.textContent="Refresh Library";
      clearInterval(scanPollingInterval);
    }
  },1000);
});

// Clear All Filters
clearFiltersBtn.addEventListener('click', ()=>{
  search.value='';
  currentIndexFilter=null;
  currentCategoryFilter=null;
  render();
  renderAlphabet();
  updateStats();
});

loadData();
</script>
</body>
</html>
""", category_filters=CATEGORY_FILTERS)

# --- MAIN ---
if __name__ == "__main__":
    print(f"🌐 Starting SWAMI Movie Catalogue Web App at http://0.0.0.0:5000")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=5000)