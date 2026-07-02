"""Niyora Research Cockpit — a light, cute wall of little discoveries about your body.
Read a card, heart it, tag it (Medicine / Content / Feature / Solution / your own).

Run:  streamlit run app.py
"""
import os, re, datetime
import duckdb
import streamlit as st

DB = os.path.join(os.path.dirname(__file__), "research.db")
THIS_YEAR = 2026
PER_ROW = 2
DEFAULT_TAGS = ["Medicine", "Content", "Feature", "Solution"]
TAG_STYLE = {"Medicine": "#e7f0fb,#2c6bb3", "Content": "#fdeef4,#c14d84",
             "Feature": "#eafaf1,#2e8b57", "Solution": "#fdf3e3,#b57e14"}
CUSTOM_STYLE = "#f0ecf9,#6a4fb0"
AXIS_ORDER = ["core", "modulator", "impact", "context"]
AXIS_COLOR = {"core": "#e6799b", "modulator": "#6bbf8f", "impact": "#6d9be0", "context": "#e6b45a"}
AXIS_ABOUT = {"core": "PMS / PMDD itself", "modulator": "what makes yours different",
              "impact": "what it affects (mood, self-harm, work, relationships)",
              "context": "history, myths, wonder — content fuel"}

st.set_page_config(page_title="Niyora · what we're learning", page_icon="🌸", layout="wide")


def _secret(key):
    try:
        return st.secrets.get(key)
    except Exception:
        return None


def _require_password():
    pw = os.environ.get("APP_PASSWORD") or _secret("app_password")
    if not pw or st.session_state.get("authed"):
        return  # no password configured (local) -> open
    st.markdown("### 🌸 Niyora Research")
    entered = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Password")
    if entered == pw:
        st.session_state.authed = True
        st.rerun()
    elif entered:
        st.error("Not quite.")
    st.stop()


@st.cache_resource
def _conn():
    token = os.environ.get("MOTHERDUCK_TOKEN") or _secret("motherduck_token")
    if token:
        os.environ["MOTHERDUCK_TOKEN"] = token   # extension reads it from env
        c = duckdb.connect("md:niyora_research")
    else:
        c = duckdb.connect(DB)                    # local fallback
    c.execute("ALTER TABLE papers ADD COLUMN IF NOT EXISTS friendly_title TEXT")
    c.execute("ALTER TABLE papers ADD COLUMN IF NOT EXISTS user_tags TEXT DEFAULT ''")
    c.execute("ALTER TABLE papers ADD COLUMN IF NOT EXISTS seq INTEGER")
    if c.execute("SELECT count(*) FROM papers WHERE seq IS NULL").fetchone()[0]:
        c.execute("""CREATE OR REPLACE TEMP TABLE _ord AS SELECT uid,
            row_number() OVER (ORDER BY (friendly_title IS NULL), relevance DESC, cites DESC) rn
            FROM papers""")
        c.execute("UPDATE papers SET seq=_ord.rn FROM _ord WHERE papers.uid=_ord.uid")
    c.execute("CREATE TABLE IF NOT EXISTS app_state (k TEXT PRIMARY KEY, v TEXT)")
    return c


def _run(sql, params, want_df):
    try:
        r = _conn().execute(sql, params or [])
    except Exception:               # stale/broken cached connection -> reconnect once
        _conn.clear()
        r = _conn().execute(sql, params or [])
    return r.df() if want_df else None


def q(sql, params=None):
    return _run(sql, params, True)


def set_status(uid, status):
    _run("UPDATE papers SET status=? WHERE uid=?", [status, uid], False)


def set_utags(uid, tags):
    keep = sorted({t.strip() for t in tags if t and t.strip()})
    _run("UPDATE papers SET user_tags=? WHERE uid=?", [",".join(keep), uid], False)


def get_state(k):
    r = _run("SELECT v FROM app_state WHERE k=?", [k], True)
    return r["v"][0] if len(r) else None


def set_state(k, v):
    _run("INSERT INTO app_state VALUES (?,?) ON CONFLICT (k) DO UPDATE SET v=excluded.v", [k, str(v)], False)


def utags_of(r):
    v = r.get("user_tags")
    return [t.strip() for t in v.split(",") if t.strip()] if isinstance(v, str) else []


def toggle_utag(uid, current, tag):
    s = set(current)
    s.discard(tag) if tag in s else s.add(tag)
    set_utags(uid, s)


def tag_editor(uid, cur, customs, sfx):
    new = st.text_input("Your own tag", key=f"nt{sfx}{uid}", placeholder="make your own…")
    if st.button("Add", key=f"sv{sfx}{uid}", use_container_width=True):
        set_utags(uid, cur + ([new] if new else [])); st.rerun()
    for tg in customs:
        if st.button("✕ " + tg, key=f"rm{sfx}{tg}{uid}", use_container_width=True):
            toggle_utag(uid, cur, tg); st.rerun()


def all_known_tags():
    found = set()
    for row in q("SELECT DISTINCT user_tags FROM papers WHERE user_tags <> ''")["user_tags"]:
        found |= {t.strip() for t in (row or "").split(",") if t.strip()}
    return DEFAULT_TAGS + sorted(found - set(DEFAULT_TAGS))


def clean(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip() if isinstance(t, str) else ""


def preview(t):
    return re.sub(r"^(background|objectives?|aims?|rationale|introduction|methods?|purpose|importance)\s+",
                  "", clean(t), flags=re.I)


def nice_fallback(title):
    t = clean(title)
    if not t:
        return "Untitled finding"
    t = re.split(r":\s", t)[0]
    return (t[:110] + "…") if len(t) > 112 else t


def card_title(r):
    ft = r["friendly_title"]
    return ft.strip() if isinstance(ft, str) and ft.strip() else nice_fallback(r["title"])


def chip(tag):
    bg, fg = TAG_STYLE.get(tag, CUSTOM_STYLE).split(",")
    return (f'<span style="background:{bg};color:{fg};padding:2px 11px;border-radius:20px;'
            f'font-size:.76rem;margin-right:4px;white-space:nowrap;">{tag}</span>')


st.markdown("""
<style>
.block-container {padding-top:1.6rem; max-width:1400px;}
#MainMenu, footer {visibility:hidden;}
.hero h1 {font-size:1.95rem; margin-bottom:.4rem; font-weight:700; letter-spacing:-.01em;}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background:#fff; border:1px solid #f0e7e2 !important; border-radius:18px !important;
    box-shadow:0 1px 2px rgba(0,0,0,.03); transition:transform .12s ease, box-shadow .12s ease;
    min-height:132px; padding:.5rem .7rem;}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform:translateY(-2px); box-shadow:0 8px 22px rgba(224,122,155,.12);}
.ctitle {font-size:1.3rem; line-height:1.32; font-weight:680; color:#2f2c2a;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;}
.ctitle a {color:inherit; text-decoration:none;}
.ctitle a:hover {text-decoration:underline; text-decoration-color:#e07a9b;}
.cmeta {color:#a99f98; font-size:.8rem; margin-top:.5rem;}
.pill {padding:1px 9px; border-radius:20px; font-size:.72rem; margin-right:8px;}
.pill.new {background:#eaf5ee; color:#2e7d5b;} .pill.old {background:#f1eeec; color:#9a9088;}
.utags {margin-top:.5rem;}
.stopmark {display:inline-block; background:#fbe4ee; color:#c14d84; font-size:.72rem;
    font-weight:600; padding:2px 11px; border-radius:20px; margin-bottom:8px;}
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stHorizontalBlock"] {gap:4px !important;}
div[data-testid="stVerticalBlockBorderWrapper"] .stButton button,
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stPopover"] button {
    border:1px solid #efe7e2 !important; background:#fff !important; box-shadow:none !important;
    color:#8a8078; font-size:.8rem; padding:.15rem .6rem; min-height:0; border-radius:12px;
    white-space:nowrap !important;}
div[data-testid="stVerticalBlockBorderWrapper"] .stButton button:hover {border-color:#e07a9b !important; color:#c85a7e;}
div[data-testid="stVerticalBlockBorderWrapper"] .stButton button *,
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stPopover"] button * {white-space:nowrap !important;}
.rmark {display:none;}
/* target only the innermost action row (no nested horizontal block inside it) */
div[data-testid="stHorizontalBlock"]:has(.rmob):not(:has(div[data-testid="stHorizontalBlock"])) {display:none !important;}
@media (max-width:640px) {
    .ctitle {font-size:1.5rem; -webkit-line-clamp:unset; display:block; overflow:visible;}
    div[data-testid="stHorizontalBlock"]:has(.rdesk):not(:has(div[data-testid="stHorizontalBlock"])) {display:none !important;}
    div[data-testid="stHorizontalBlock"]:has(.rmob):not(:has(div[data-testid="stHorizontalBlock"])) {display:flex !important;}
}
</style>
""", unsafe_allow_html=True)

_require_password()

st.markdown('<div class="hero"><h1>Hey, here\'s what we\'re learning about your body 🌸</h1></div>',
            unsafe_allow_html=True)

# ---------------- top filter bar ----------------
lanes = ["All lanes"] + q("SELECT DISTINCT lane FROM papers ORDER BY lane")["lane"].tolist()
known = all_known_tags()
fb = st.columns([3, 2, 1.8, 1.9, 1.2, 1.5])
search = fb[0].text_input("Search", placeholder="Search anything…", label_visibility="collapsed")
lane = fb[1].selectbox("Lane", lanes, label_visibility="collapsed")
mytag = fb[2].selectbox("My tag", ["Any tag"] + known, label_visibility="collapsed")
sort = fb[3].selectbox("Sort", ["Reading order", "Freshest voice first", "To review first",
                                "Most cited", "Newest", "Hearted"], label_visibility="collapsed")
count = fb[4].selectbox("Show", [20, 40, 80, 160], index=3, label_visibility="collapsed")
hearted_only = fb[5].toggle("♥ hearted")

where, params = [], []
if lane != "All lanes":
    where.append("lane = ?"); params.append(lane)
if hearted_only:
    where.append("status = 'promoted'")
if mytag != "Any tag":
    where.append("(',' || user_tags || ',') LIKE ?"); params.append(f"%,{mytag},%")
if search:
    where.append("(lower(title) LIKE ? OR lower(abstract) LIKE ? OR lower(friendly_title) LIKE ?)")
    s = f"%{search.lower()}%"; params += [s, s, s]
where_sql = (" WHERE " + " AND ".join(where)) if where else ""
order = {"Reading order": "seq",
         "Freshest voice first": "(friendly_title IS NULL), relevance DESC, cites DESC",
         "To review first": "(status<>'new' OR user_tags<>''), relevance DESC, cites DESC",
         "Most cited": "cites DESC", "Newest": "year DESC",
         "Hearted": "(status!='promoted'), cites DESC"}[sort]

# reset to first page whenever the filters/sort/page-size change
fkey = (lane, mytag, sort, int(count), hearted_only, search)
if "initialized" not in st.session_state:
    st.session_state.page = int(get_state("last_page") or 0)   # resume where you left off
    st.session_state.fkey = fkey
    st.session_state.initialized = True
elif st.session_state.get("fkey") != fkey:
    st.session_state.page = 0
    st.session_state.fkey = fkey

page_size = int(count)
tot_filtered = int(q(f"SELECT count(*) n FROM papers{where_sql}", params)["n"][0])
pages = max(1, -(-tot_filtered // page_size))
st.session_state.page = min(st.session_state.get("page", 0), pages - 1)
offset = st.session_state.page * page_size
df = q(f"SELECT * FROM papers{where_sql} ORDER BY {order} LIMIT {page_size} OFFSET {offset}", params)

# ---------------- reading-progress tracker ----------------
total = q("SELECT count(*) n FROM papers")["n"][0]
hearts = q("SELECT count(*) n FROM papers WHERE status='promoted'")["n"][0]
tagged = q("SELECT count(*) n FROM papers WHERE user_tags <> ''")["n"][0]
reached = q("SELECT coalesce(max(seq),0) n FROM papers WHERE status<>'new' OR user_tags<>''")["n"][0]
to_translate = q("SELECT count(*) n FROM papers "
                 "WHERE (status='promoted' OR user_tags<>'') AND friendly_title IS NULL")["n"][0]
st.progress(reached / total if total else 0,
            text=f"You've reached {reached:,} of {total:,}  ·  {(reached/total*100 if total else 0):.0f}% through the bank")
tail = f" · 🌸 {to_translate} picks ready for their Californian rewrite" if to_translate else ""
st.caption(f"♥ {hearts} hearted · 🏷 {tagged} tagged{tail} · showing {len(df)}")

# ---------------- card grid (2 per row) ----------------
rows = df.to_dict("records")
for i in range(0, len(rows), PER_ROW):
    cols = st.columns(PER_ROW, gap="medium")
    for col, r in zip(cols, rows[i:i + PER_ROW]):
        with col.container(border=True):
            uid = r["uid"]
            cur = utags_of(r)
            is_new = str(r["year"]).isdigit() and int(r["year"]) >= THIS_YEAR - 3
            hearted = r["status"] == "promoted"
            if reached and r["seq"] == reached:
                st.markdown('<div class="stopmark">🌸 you left off here</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ctitle"><a href="{r["link"]}" target="_blank" rel="noopener">'
                        f'{card_title(r)}</a></div>', unsafe_allow_html=True)
            pill = f'<span class="pill {"new" if is_new else "old"}">{"New" if is_new else "Older"}</span>'
            st.markdown(f'<div class="cmeta">{pill}{r["cites"]} cites</div>', unsafe_allow_html=True)
            customs = [t for t in cur if t not in DEFAULT_TAGS]
            if customs:
                st.markdown(f'<div class="utags">{"".join(chip(t) for t in customs)}</div>', unsafe_allow_html=True)

            # desktop: tags sit open — one click to toggle
            d = st.columns([0.55, 1.5, 1.5, 1.5, 1.5, 0.6])
            d[0].markdown('<span class="rmark rdesk"></span>', unsafe_allow_html=True)
            if d[0].button("♥" if hearted else "♡", key=f"hd{uid}", help="Heart"):
                set_status(uid, "new" if hearted else "promoted"); st.rerun()
            for j, tg in enumerate(DEFAULT_TAGS):
                on = tg in cur
                if d[1 + j].button(("✓ " if on else "") + tg, key=f"td{tg}{uid}"):
                    toggle_utag(uid, cur, tg); st.rerun()
            with d[5].popover("＋"):
                tag_editor(uid, cur, customs, "d")

            # mobile: heart + a Tags dropdown
            m = st.columns([0.5, 2])
            m[0].markdown('<span class="rmark rmob"></span>', unsafe_allow_html=True)
            if m[0].button("♥" if hearted else "♡", key=f"hm{uid}", help="Heart"):
                set_status(uid, "new" if hearted else "promoted"); st.rerun()
            with m[1].popover("🏷 Tags"):
                for tg in DEFAULT_TAGS:
                    on = tg in cur
                    if st.button(("✓ " if on else "＋ ") + tg, key=f"tm{tg}{uid}", use_container_width=True):
                        toggle_utag(uid, cur, tg); st.rerun()
                tag_editor(uid, cur, customs, "m")

# ---------------- pager ----------------
st.write("")
pg = st.columns([1, 1, 4])
if pg[0].button("← Prev", disabled=st.session_state.page <= 0, use_container_width=True):
    st.session_state.page -= 1; set_state("last_page", st.session_state.page); st.rerun()
if pg[1].button("Next →", disabled=st.session_state.page >= pages - 1, use_container_width=True):
    st.session_state.page += 1; set_state("last_page", st.session_state.page); st.rerun()
pg[2].caption(f"Page {st.session_state.page + 1} of {pages} · "
              f"showing {offset + 1}–{offset + len(df)} of {tot_filtered:,}")

# ---------------- footer ----------------
st.divider()
if st.button("⬇ Export hearted + tagged → xlsx"):
    out = os.path.join(os.path.dirname(__file__), f"curated-{datetime.date.today().isoformat()}.xlsx")
    pr = q("SELECT lane,axis,tags AS science_tags,user_tags,friendly_title,title,journal,year,"
           "study_type,grade_auto,cites,status,abstract,link FROM papers "
           "WHERE status='promoted' OR user_tags <> '' ORDER BY axis,lane,cites DESC")
    pr.to_excel(out, index=False)
    st.success(f"Exported {len(pr)} curated papers → {os.path.basename(out)}")
