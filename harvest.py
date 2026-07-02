"""Harvest papers from Europe PMC into a local DuckDB bank.

Run:  python harvest.py
Idempotent: dedupes by DOI (or title fallback). Re-running refreshes metadata but
preserves your curation (status / relevance / notes) via an upsert that only touches
the bibliographic columns.
"""
import urllib.request, urllib.parse, json, time, sys, os
import duckdb
from lanes import LANES

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
DB = os.path.join(os.path.dirname(__file__), "research.db")

CORE_TERMS = ("premenstrual", "pmdd", "pms", "luteal", "menstrual")


def fetch(query, cap):
    params = urllib.parse.urlencode({
        "query": query, "format": "json", "pageSize": min(cap, 100),
        "resultType": "core", "sort": "P_PDATE_D desc",
    })
    with urllib.request.urlopen(f"{BASE}?{params}", timeout=45) as r:
        return json.load(r)["resultList"].get("result", [])


def study_type(rec):
    pt = (rec.get("pubType", "") or "").lower()
    blob = ((rec.get("title", "") or "") + " " + (rec.get("abstractText", "") or "")).lower()
    if "meta-analysis" in pt or "meta-analysis" in blob or "systematic review" in blob:
        return "meta-analysis/SR", "strong"
    if "randomi" in blob or "randomized controlled" in pt:
        return "RCT", "strong"
    if "review" in pt:
        return "review", "moderate"
    if any(w in blob for w in ("cohort", "cross-sectional", "case-control", "observational")):
        return "observational", "moderate"
    return "other/primary", "check"


def relevance_heuristic(rec):
    """Cheap first-pass relevance: does the abstract actually center the cycle/premenstrual?"""
    blob = ((rec.get("title", "") or "") + " " + (rec.get("abstractText", "") or "")).lower()
    return sum(blob.count(t) for t in CORE_TERMS)


def uid(rec):
    return (rec.get("doi") or "").strip().lower() or ("t:" + (rec.get("title", "") or "")[:80].lower())


def ensure_schema(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            uid TEXT PRIMARY KEY,
            doi TEXT, title TEXT, journal TEXT, year TEXT,
            study_type TEXT, grade_auto TEXT, cites INTEGER,
            lane TEXT, axis TEXT, tags TEXT, abstract TEXT, link TEXT,
            relevance INTEGER,
            status TEXT DEFAULT 'new',   -- new | promoted | irrelevant
            notes TEXT DEFAULT ''
        )
    """)


def upsert(con, rows):
    for r in rows:
        con.execute("""
            INSERT INTO papers (uid,doi,title,journal,year,study_type,grade_auto,cites,lane,axis,tags,abstract,link,relevance)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT (uid) DO UPDATE SET
                title=excluded.title, journal=excluded.journal, year=excluded.year,
                study_type=excluded.study_type, grade_auto=excluded.grade_auto, cites=excluded.cites,
                abstract=excluded.abstract, link=excluded.link, relevance=excluded.relevance
                -- lane/axis/tags/status/notes intentionally preserved on refresh
        """, r)


def main():
    con = duckdb.connect(DB)
    ensure_schema(con)
    seen = set()
    total = 0
    for name, axis, query, cap, tags in LANES:
        try:
            recs = fetch(query, cap)
        except Exception as e:
            print(f"  ! {name}: {e}", file=sys.stderr); continue
        batch = []
        for rec in recs:
            u = uid(rec)
            if u in seen:
                continue
            seen.add(u)
            st, grade = study_type(rec)
            doi = (rec.get("doi") or "").strip()
            link = f"https://doi.org/{doi}" if doi else \
                f"https://europepmc.org/abstract/{rec.get('source','MED')}/{rec.get('id','')}"
            batch.append((u, doi, (rec.get("title", "") or "")[:400],
                          rec.get("journalTitle", "") or rec.get("source", ""),
                          str(rec.get("pubYear", "")), st, grade,
                          int(rec.get("citedByCount", 0) or 0), name, axis, tags,
                          (rec.get("abstractText", "") or "").replace("\n", " ").strip(),
                          link, relevance_heuristic(rec)))
        upsert(con, batch)
        total += len(batch)
        print(f"  {name:<26} {len(batch):>3} new  ({axis})")
        time.sleep(0.3)
    n = con.execute("SELECT count(*) FROM papers").fetchone()[0]
    con.close()
    print(f"\nHarvest done. {total} rows this run. Bank now holds {n} unique papers -> {DB}")


if __name__ == "__main__":
    main()
