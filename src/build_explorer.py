"""Build report/creator_explorer.html: one self-contained page for the marketing manager.

Reads outputs/creators/*.csv (the frozen score, rank stability, food share, link-request share)
and writes a sortable, filterable table of all 20 creators. Nothing is typed in: every figure
comes from those files. The five chosen creators and the backups are listed once in FINAL below,
copied from DECISIONS.md.

Run:  python src/build_explorer.py
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CRE = ROOT / "outputs" / "creators"
FINAL = {"test": ["CR-13", "CR-03", "CR-11", "CR-01", "CR-19"],
         "backup": ["CR-05", "CR-09", "CR-16"],
         "set_aside": ["CR-12", "CR-15"]}

sc = pd.read_csv(CRE / "creator_scores.csv").set_index("creator_id")
bt = pd.read_csv(CRE / "bootstrap_top5.csv").set_index("creator_id")
fd = pd.read_csv(CRE / "food_scan.csv").set_index("creator_id")
ls = pd.read_csv(CRE / "link_sensitivity.csv").set_index("creator_id")
sn = pd.read_csv(CRE / "sensitivity.csv").set_index("creator_id")

def status(cid):
    for k, v in FINAL.items():
        if cid in v:
            return k
    return "not_chosen"

rows = []
for cid, s in sc.iterrows():
    tops = int(sum(bool(sn.loc[cid, c]) for c in ("top5_frozen", "top5_A", "top5_B", "top5_C")))
    flags = [n for n, c in (("hidden likes", "flag_hidden_likes"), ("no audience data", "flag_no_audience_data"),
                            ("legal review", "flag_legal_review")) if bool(s[c])]
    rows.append({
        "id": cid, "handle": s["handle"], "persona": s["persona"], "followers": int(s["followers"]),
        "rank": int(s["composite_rank"]), "score": round(float(s["composite"]), 3),
        "stability": round(float(bt.loc[cid, "top5_share"]) * 100, 1),
        "weightings": tops,
        "food": round(float(fd.loc[cid, "matched_share"]) * 100, 1),
        "sponsored": round(float(s["n_sponsored"]) / float(s["n_posts_window"]) * 100, 1),
        "link": round(float(ls.loc[cid, "link_request_share"]) * 100, 1),
        "posts": int(s["n_posts_window"]), "flags": ", ".join(flags) or "none", "status": status(cid)})

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Little Joys creator explorer</title>
<style>
:root{--ink:#1b2733;--mut:#5b6773;--acc:#2f4858;--bg:#fff;--card:#f4f2ec;--line:#d5dae0;--g:#e1efe4;--a:#fbefd0;--r:#f7dad5}
@media (prefers-color-scheme:dark){:root{--ink:#e8edf1;--mut:#9aa7b2;--acc:#9fc2d6;--bg:#12181e;--card:#1b242c;--line:#33414d;--g:#1f3a2b;--a:#4a3d17;--r:#4a2420}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,Segoe UI,Arial,sans-serif}
main{max-width:1100px;margin:0 auto;padding:20px 16px 40px}
h1{margin:0 0 4px;font-size:26px;color:var(--acc)} p{margin:6px 0}
.warn{background:#fbf3e1;color:#3a2f12;border-left:5px solid #b7791f;padding:10px 14px;margin:14px 0;border-radius:4px}
@media (prefers-color-scheme:dark){.warn{background:#3a2f12;color:#f3e6c4}}
.bar{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
button,input,select{font:inherit;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:900px}
th,td{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;white-space:nowrap}
th{cursor:pointer;background:var(--card);position:sticky;top:0} th:hover{color:var(--acc)}
td.num{text-align:right} .tag{padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600}
.test{background:var(--g)}.backup{background:var(--a)}.set_aside{background:var(--r)}
small{color:var(--mut)}
</style></head><body><main>
<h1>Little Joys creator explorer</h1>
<p>All 20 creators, from the same files as the report. Click a column to sort.</p>
<div class="warn"><b>Read this before you rely on it.</b> The ad figures behind the report are simulated, not Little Joys results. The labels come from an AI system and are not always right. Rank stability and the weightings column are post-hoc checks, not part of the frozen score. This page shows associations, not proof that a creator will sell.</div>
<div class="bar">
<button data-f="all" class="on">All 20</button><button data-f="test">My five</button><button data-f="backup">Backups</button>
<button data-f="set_aside">Set aside</button><button data-f="top5">Score's top five</button>
<input id="q" placeholder="Search handle or persona" aria-label="Search">
</div>
<div class="wrap"><table id="t"><thead><tr></tr></thead><tbody></tbody></table></div>
<p><small>Score rank is the frozen pre-set score (1 = highest). Stability is the share of 200 post-resampling runs in which the creator is in the top five. "Weightings" counts, out of 4, how many score versions (the original and three alternates) put the creator in the top five. Food, sponsored and comment-for-link are shares of the creator's posts in the 12 months to 2026-10-27. The number of posts differs by creator (see the Posts column), so a percentage on a small count moves a lot with one post.</small></p>
<script>
const D=__DATA__;
const COLS=[["id","Creator"],["handle","Handle"],["persona","Persona"],["status","Status"],["rank","Score rank"],["stability","Stability %"],["weightings","Top 5 in x of 4"],["food","Food posts %"],["sponsored","Sponsored %"],["link","Comment-for-link %"],["posts","Posts in window"],["followers","Followers"],["flags","Flags"]];
const LAB={test:"Test first",backup:"Backup",set_aside:"Set aside",not_chosen:"Not chosen"};
let filt="all",sortK="rank",asc=true,q="";
const th=document.querySelector("thead tr");
COLS.forEach(([k,l])=>{const e=document.createElement("th");e.textContent=l;e.onclick=()=>{asc=(sortK===k)?!asc:true;sortK=k;draw()};th.appendChild(e)});
function stab(v){return v>=50?"var(--g)":v>=20?"var(--a)":"var(--r)"}
function draw(){
 let r=D.filter(x=>filt==="all"||(filt==="top5"?x.rank<=5:x.status===filt)).filter(x=>(x.handle+x.persona).toLowerCase().includes(q));
 r.sort((a,b)=>{const A=a[sortK],B=b[sortK];return (A>B?1:A<B?-1:0)*(asc?1:-1)});
 const tb=document.querySelector("tbody");tb.innerHTML="";
 r.forEach(x=>{const tr=document.createElement("tr");
  COLS.forEach(([k])=>{const td=document.createElement("td");let v=x[k];
   if(k==="status"){td.innerHTML='<span class="tag '+x.status+'">'+LAB[x.status]+'</span>'}
   else if(k==="stability"){td.className="num";td.style.background=stab(v);td.textContent=v.toFixed(1)}
   else if(k==="followers"){td.className="num";td.textContent=v.toLocaleString("en-IN")}
   else if(typeof v==="number"){td.className="num";td.textContent=Number.isInteger(v)?v:v.toFixed(1)}
   else td.textContent=v;tr.appendChild(td)});tb.appendChild(tr)});
 document.querySelectorAll(".bar button").forEach(b=>b.classList.toggle("on",b.dataset.f===filt));
}
document.querySelectorAll(".bar button").forEach(b=>b.onclick=()=>{filt=b.dataset.f;draw()});
document.getElementById("q").oninput=e=>{q=e.target.value.toLowerCase();draw()};
draw();
</script></main></body></html>"""

out = ROOT / "report" / "creator_explorer.html"
out.write_text(HTML.replace("__DATA__", json.dumps(rows)), encoding="utf-8")
print("wrote", out, len(rows), "creators")
