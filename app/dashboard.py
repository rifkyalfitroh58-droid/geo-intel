"""
GEO INTEL Dashboard v1.0
Sistem Analisis Geospasial & Pemetaan Insiden Indonesia
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json, os, sys
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (INCIDENT_TYPES, SEVERITY_LEVELS, PROVINCES,
                    CITIES, INCIDENT_KEYWORDS)
from database import (ensure_db, get_monitors, add_monitor, delete_monitor,
                      load_incidents, load_all_incidents, load_province_stats,
                      load_hotspots, get_global_stats, update_province_stats,
                      update_hotspots)
from fetcher import fetch_geo_data, seed_demo_data

ensure_db()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GEO INTEL",
    page_icon="🗺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.2rem; padding-bottom: 1rem; }

.geo-header {
    background: linear-gradient(135deg, #0a0d0a 0%, #0d1a0d 50%, #0f2010 100%);
    border: 1px solid #1a3d1a;
    border-radius: 12px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.2rem;
    position: relative; overflow: hidden;
}
.geo-header::before {
    content: ''; position: absolute; top:0; left:0; right:0; bottom:0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(46,204,113,0.03) 2px, rgba(46,204,113,0.03) 4px
    );
}
.geo-title {
    font-family:'DM Mono',monospace; font-size:1.5rem;
    font-weight:500; color:#2ECC71; letter-spacing:.08em; margin:0;
}
.geo-sub {
    font-family:'DM Mono',monospace; font-size:.72rem;
    color:rgba(46,204,113,.5); letter-spacing:.12em;
    margin-top:4px; text-transform:uppercase;
}
.geo-badge {
    display:inline-block; font-family:'DM Mono',monospace; font-size:.65rem;
    background:rgba(46,204,113,.1); border:1px solid rgba(46,204,113,.3);
    color:#2ECC71; border-radius:4px; padding:2px 8px;
    margin-right:6px; margin-top:8px; letter-spacing:.06em;
}
.geo-badge.red    { background:rgba(231,76,60,.1); border-color:rgba(231,76,60,.3); color:#E74C3C; }
.geo-badge.yellow { background:rgba(243,156,18,.1); border-color:rgba(243,156,18,.3); color:#F39C12; }
.geo-badge.blue   { background:rgba(52,152,219,.1); border-color:rgba(52,152,219,.3); color:#3498DB; }

.metric-card {
    background:#0a0d0a; border:1px solid #1a3d1a;
    border-radius:10px; padding:1rem 1.2rem;
    text-align:center; position:relative; overflow:hidden;
}
.metric-card::after { content:''; position:absolute; bottom:0; left:0; right:0; height:2px; }
.metric-card.green::after  { background:#2ECC71; }
.metric-card.red::after    { background:#E74C3C; }
.metric-card.yellow::after { background:#F39C12; }
.metric-card.blue::after   { background:#3498DB; }
.metric-card.teal::after   { background:#1ABC9C; }
.metric-num   { font-family:'DM Mono',monospace; font-size:1.9rem; font-weight:500; line-height:1.1; }
.metric-label { font-size:.72rem; color:rgba(255,255,255,.4); margin-top:4px; letter-spacing:.06em; text-transform:uppercase; }

.section-title {
    font-family:'DM Mono',monospace; font-size:.8rem; font-weight:500;
    color:#2ECC71; letter-spacing:.12em; text-transform:uppercase;
    padding-bottom:6px; border-bottom:1px solid #1a3d1a;
    margin:1.2rem 0 .8rem;
}
.intel-box {
    background:#070a07; border:1px solid #1a3d1a; border-radius:8px;
    padding:.9rem 1.1rem; margin-bottom:.6rem;
    font-size:.84rem; color:rgba(255,255,255,.8); line-height:1.6;
}
.intel-box.critical { border-color:rgba(231,76,60,.5); background:rgba(231,76,60,.05); }
.intel-box.high     { border-color:rgba(230,126,34,.4); background:rgba(230,126,34,.04); }
.intel-box.medium   { border-color:rgba(243,156,18,.3); background:rgba(243,156,18,.04); }
.intel-box.low      { border-color:rgba(46,204,113,.3); background:rgba(46,204,113,.04); }

.incident-card {
    background:#0a0d0a; border:1px solid #1a3d1a; border-radius:8px;
    padding:.75rem 1rem; margin-bottom:6px;
}
.hotspot-card {
    background:#070a07; border:1px solid #1a3d1a; border-radius:8px;
    padding:.7rem 1rem; margin-bottom:6px;
    display:flex; align-items:center; gap:10px;
}
.report-box {
    background:#040604; border:1px solid #1a3d1a; border-radius:8px;
    padding:1.2rem; font-family:'DM Mono',monospace; font-size:.75rem;
    color:rgba(255,255,255,.75); line-height:1.8; white-space:pre-wrap;
    max-height:500px; overflow-y:auto;
}

section[data-testid="stSidebar"] { background:#050705; }
section[data-testid="stSidebar"] * { color:rgba(255,255,255,.8) !important; }
section[data-testid="stSidebar"] hr { border-color:#1a3d1a !important; }

.stTabs [data-baseweb="tab-list"] { background:transparent; border-bottom:1px solid #1a3d1a; gap:4px; }
.stTabs [data-baseweb="tab"] {
    font-family:'DM Mono',monospace; font-size:.75rem; letter-spacing:.08em;
    padding:8px 16px; border-radius:6px 6px 0 0;
    color:rgba(255,255,255,.4) !important; background:transparent; border:none;
}
.stTabs [aria-selected="true"] {
    background:rgba(46,204,113,.1) !important;
    color:#2ECC71 !important; border-bottom:2px solid #2ECC71 !important;
}
div[data-testid="stButton"] button {
    background:rgba(46,204,113,.1) !important; color:#2ECC71 !important;
    border:1px solid rgba(46,204,113,.3) !important; border-radius:6px !important;
    font-family:'DM Mono',monospace !important; font-size:.78rem !important;
}
div[data-testid="stButton"] button:hover { background:rgba(46,204,113,.2) !important; }
::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:#050705; }
::-webkit-scrollbar-thumb { background:#1a3d1a; border-radius:4px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────────────────────
PLOT = dict(
    plot_bgcolor="#070a07", paper_bgcolor="#0a0d0a",
    font=dict(family="DM Sans", color="rgba(255,255,255,0.7)", size=11),
    margin=dict(l=10, r=10, t=36, b=10),
    xaxis=dict(showgrid=True, gridcolor="#1a3d1a", showline=False,
               tickfont=dict(color="rgba(255,255,255,0.4)")),
    yaxis=dict(showgrid=True, gridcolor="#1a3d1a", showline=False,
               tickfont=dict(color="rgba(255,255,255,0.4)")),
)

def get_sev_color(score: float) -> str:
    if score >= 75: return "#E74C3C"
    if score >= 50: return "#E67E22"
    if score >= 25: return "#F39C12"
    return "#2ECC71"

def get_sev_label(score: float) -> str:
    if score >= 75: return "🔴 KRITIS"
    if score >= 50: return "🟠 TINGGI"
    if score >= 25: return "🟡 SEDANG"
    return "🟢 RENDAH"

# ── Cache helpers ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def cached_monitors():       return get_monitors()
@st.cache_data(ttl=30)
def cached_incidents(mid):   return load_incidents(mid)
@st.cache_data(ttl=30)
def cached_prov_stats(mid):  return load_province_stats(mid)
@st.cache_data(ttl=30)
def cached_hotspots(mid):    return load_hotspots(mid)
@st.cache_data(ttl=30)
def cached_stats():          return get_global_stats()

def clear_cache():
    cached_monitors.clear(); cached_incidents.clear()
    cached_prov_stats.clear(); cached_hotspots.clear()
    cached_stats.clear()


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:.8rem 0 .4rem">
        <div style="font-family:'DM Mono',monospace;font-size:1rem;color:#2ECC71;letter-spacing:.1em;font-weight:500">
            &#128506; GEO INTEL
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:.65rem;color:rgba(46,204,113,.4);
                    letter-spacing:.12em;text-transform:uppercase;margin-top:2px">
            Geospatial Intelligence System v1.0
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # ── Tambah monitor ────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-family:DM Mono;font-size:.65rem;color:rgba(46,204,113,.5);'
        'letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px">◈ PANTAU KEYWORD</div>',
        unsafe_allow_html=True
    )
    new_kw = st.text_input(
        "keyword", placeholder="mis. banjir, gempa, konflik...",
        label_visibility="collapsed", key="geo_kw_input"
    )
    col_add, col_n = st.columns([2,1])
    with col_add:
        add_btn = st.button("⬇ Ambil Data", width='stretch')
    with col_n:
        n_art = st.selectbox("Jumlah artikel", [20,50,100], label_visibility="collapsed")

    if add_btn:
        if not new_kw.strip():
            st.warning("Masukkan keyword dulu.")
        else:
            with st.spinner(f"Mengambil & memetakan: {new_kw}..."):
                mid = add_monitor(new_kw.strip())
                n_inc, n_loc, err = fetch_geo_data(mid, new_kw.strip(), n_art)
            if err:
                st.error(f"❌ {err}")
                delete_monitor(mid)
            else:
                clear_cache()
                st.success(f"✅ {n_inc} insiden · {n_loc} lokasi!")
                st.rerun()

    # Demo data button
    st.divider()
    st.markdown(
        '<div style="font-family:DM Mono;font-size:.65rem;color:rgba(46,204,113,.4);'
        'letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px">◈ DEMO DATA</div>',
        unsafe_allow_html=True
    )
    if st.button("📍 Load Data Demo BNPB", width='stretch'):
        mid_demo = add_monitor("DEMO — Insiden Indonesia")
        n_demo   = seed_demo_data(mid_demo)
        clear_cache()
        st.success(f"✅ {n_demo} insiden demo dimuat!")
        st.rerun()

    st.divider()

    # ── Pilih monitor ─────────────────────────────────────────────────────────
    df_monitors = cached_monitors()
    monitor_id  = None
    monitor_kw  = None

    if df_monitors.empty:
        st.info("Belum ada data. Tambah keyword atau load demo di atas.")
    else:
        st.markdown(
            '<div style="font-family:DM Mono;font-size:.65rem;color:rgba(46,204,113,.5);'
            'letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px">MONITOR AKTIF</div>',
            unsafe_allow_html=True
        )
        opts = {f"{r['keyword']} (#{r['id']})": r['id']
                for _, r in df_monitors.iterrows()}
        sel  = st.selectbox("Monitor", list(opts.keys()), label_visibility="collapsed")
        monitor_id = opts[sel]
        monitor_kw = sel.split(" (#")[0]

        col_del, col_ref = st.columns(2)
        with col_del:
            if st.button("🗑 Hapus", width='stretch'):
                delete_monitor(monitor_id)
                clear_cache()
                st.success("Dihapus.")
                st.rerun()
        with col_ref:
            if st.button("🔄 Update", width='stretch'):
                if "DEMO" not in monitor_kw:
                    with st.spinner("Mengambil data terbaru..."):
                        n_i, n_l, err = fetch_geo_data(monitor_id, monitor_kw, 50)
                    if err:
                        st.error(f"❌ {err}")
                    else:
                        clear_cache()
                        st.success(f"✅ {n_i} insiden baru!")
                        st.rerun()
                else:
                    st.info("Demo data tidak bisa diupdate.")

    st.divider()

    # ── Quick stats ───────────────────────────────────────────────────────────
    stats = cached_stats()
    st.markdown(f"""
    <div style="font-family:'DM Mono',monospace;font-size:.65rem;color:rgba(46,204,113,.5);
                letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px">GLOBAL STATS</div>
    <div style="background:#070a07;border:1px solid #1a3d1a;border-radius:8px;padding:.8rem">
        <div style="color:rgba(255,255,255,.4);font-size:.7rem;margin-bottom:2px">Total insiden terpetakan</div>
        <div style="font-family:'DM Mono',monospace;font-size:1.6rem;color:#2ECC71;font-weight:500">
            {stats['total']}<span style="font-size:.9rem;color:rgba(46,204,113,.4)"> insiden</span>
        </div>
    </div>
    <div style="margin-top:8px;font-family:'DM Mono',monospace;font-size:.7rem;
                color:rgba(255,255,255,.4);line-height:2">
        KRITIS &nbsp;&nbsp;&nbsp;: {stats['high_sev']}<br>
        PROVINSI &nbsp;: {stats['provinces']}<br>
        AVG SEV &nbsp;&nbsp;: {stats['avg_severity']}/100<br>
        TOP TYPE &nbsp;: {stats['top_type']}
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:.65rem;
                color:rgba(46,204,113,.2);line-height:2;letter-spacing:.06em">
        GEO INTEL v1.0<br>
        DATA: NewsAPI + BNPB<br>
        GEO: Rule-based Parser<br>
        MAP: Plotly + Mapbox
    </div>
    """, unsafe_allow_html=True)


# ── HEADER ────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%d %b %Y %H:%M")
_header = (
    "<div class=\"geo-header\">"
    "<div style=\"display:flex;justify-content:space-between;align-items:flex-start\">"
    "<div>"
    "<div class=\"geo-title\">&#128506; GEO INTELLIGENCE DASHBOARD</div>"
    "<div class=\"geo-sub\">Sistem Pemetaan Insiden &amp; Analisis Geospasial Indonesia</div>"
    "<div style=\"margin-top:8px\">"
    "<span class=\"geo-badge\">AKTIF</span>"
    "<span class=\"geo-badge blue\">INDONESIA</span>"
    "<span class=\"geo-badge yellow\">34 PROVINSI</span>"
    "</div></div>"
    f"<div style=\"font-family:'DM Mono',monospace;font-size:.72rem;"
    f"color:rgba(46,204,113,.5);text-align:right\">"
    f"{now_str}<br>"
    f"<span style=\"color:rgba(46,204,113,.25)\">SYSTEM: ONLINE</span>"
    "</div></div></div>"
)
st.markdown(_header, unsafe_allow_html=True)

if not monitor_id:
    st.info("👆 Tambah keyword atau load data demo di sidebar.")
    st.stop()

# ── Load data ─────────────────────────────────────────────────────────────────
df_inc  = cached_incidents(monitor_id)
df_prov = cached_prov_stats(monitor_id)
df_hs   = cached_hotspots(monitor_id)

if df_inc.empty:
    st.warning(f"Tidak ada data insiden untuk **{monitor_kw}**. Coba update.")
    st.stop()

# Metrik
n          = len(df_inc)
n_kritis   = int((df_inc["severity"] >= 75).sum())
n_tinggi   = int((df_inc["severity"] >= 50).sum())
n_prov     = int(df_inc["province"].nunique())
avg_sev    = float(df_inc["severity"].mean())
top_type   = df_inc["inc_type"].mode().iloc[0] if not df_inc.empty else "N/A"

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺 PETA INTERAKTIF",
    "🔥 HEATMAP PROVINSI",
    "📍 HOTSPOT",
    "📊 ANALISIS",
    "📋 LAPORAN",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PETA INTERAKTIF
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # Metrik row
    c1,c2,c3,c4,c5 = st.columns(5)
    for col, val, lbl, color, cc in [
        (c1, str(n),       "TOTAL INSIDEN",  "#2ECC71", "green"),
        (c2, str(n_kritis),"KRITIS",          "#E74C3C", "red"),
        (c3, str(n_tinggi),"TINGGI",          "#E67E22", "yellow"),
        (c4, str(n_prov),  "PROVINSI",        "#3498DB", "blue"),
        (c5, f"{avg_sev:.0f}", "AVG SEVERITY",
             get_sev_color(avg_sev),
             "red" if avg_sev>=75 else "yellow" if avg_sev>=50 else "green"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card {cc}">
                <div class="metric-num" style="color:{color}">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#1a3d1a;margin:.8rem 0">', unsafe_allow_html=True)

    # Filter
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        type_filter = st.multiselect(
            "Tipe Insiden",
            options=list(INCIDENT_TYPES.keys()),
            default=list(INCIDENT_TYPES.keys()),
            format_func=lambda x: INCIDENT_TYPES[x]["label"],
        )
    with col_f2:
        sev_filter = st.slider("Min Severity", 0, 100, 0)
    with col_f3:
        map_style = st.selectbox(
            "Style Peta", 
            ["carto-darkmatter","open-street-map","stamen-terrain"],
            label_visibility="collapsed"
        )

    df_map = df_inc.copy()
    if type_filter:
        df_map = df_map[df_map["inc_type"].isin(type_filter)]
    df_map = df_map[df_map["severity"] >= sev_filter]
    df_map = df_map.dropna(subset=["lat","lon"])
    df_map = df_map[(df_map["lat"] != 0) & (df_map["lon"] != 0)]

    if df_map.empty:
        st.info("Tidak ada insiden yang sesuai filter.")
    else:
        # Buat peta scatter mapbox
        df_map["color"]  = df_map["severity"].apply(get_sev_color)
        df_map["size"]   = df_map["severity"].apply(lambda x: max(8, min(x/3, 30)))
        df_map["label"]  = df_map["inc_type"].apply(
            lambda x: INCIDENT_TYPES.get(x, {}).get("label", x)
        )
        df_map["hover"]  = (
            df_map["title"].str[:60] + "...<br>" +
            df_map["location"] + ", " + df_map["province"] + "<br>" +
            "Severity: " + df_map["severity"].astype(str) + "/100"
        )

        fig_map = go.Figure()

        # Plot per tipe biar bisa legend
        for inc_type, info in INCIDENT_TYPES.items():
            subset = df_map[df_map["inc_type"] == inc_type]
            if subset.empty:
                continue
            fig_map.add_trace(go.Scattermap(
                lat=subset["lat"], lon=subset["lon"],
                mode="markers",
                marker=dict(
                    size=subset["size"],
                    color=info["color"],
                    opacity=0.8,
                ),
                text=subset["hover"],
                hovertemplate="%{text}<extra></extra>",
                name=f"{info['icon']} {info['label']}",
            ))

        fig_map.update_layout(
            map=dict(
                style=map_style,
                center=dict(lat=-2.5, lon=118.0),
                zoom=4,
            ),
            paper_bgcolor="#0a0d0a",
            plot_bgcolor="#0a0d0a",
            font=dict(color="rgba(255,255,255,0.7)", family="DM Sans"),
            height=520,
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(
                bgcolor="rgba(10,13,10,0.8)",
                bordercolor="#1a3d1a",
                borderwidth=1,
                font=dict(color="rgba(255,255,255,0.6)", size=10),
            ),
        )
        st.plotly_chart(fig_map, width='stretch')

        st.markdown(
            f'<div style="font-family:DM Mono;font-size:.7rem;color:rgba(255,255,255,.3);'
            f'text-align:center">{len(df_map)} insiden ditampilkan</div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — HEATMAP PROVINSI
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">HEATMAP INSIDEN PER PROVINSI</div>',
                unsafe_allow_html=True)

    if df_prov.empty:
        st.info("Belum ada data statistik provinsi.")
    else:
        # Bar chart provinsi
        df_prov_s = df_prov.sort_values("incident_count", ascending=True).tail(20)
        colors_prov = [get_sev_color(s) for s in df_prov_s["avg_severity"]]

        fig_prov = go.Figure(go.Bar(
            x=df_prov_s["incident_count"],
            y=df_prov_s["province"],
            orientation="h",
            marker_color=colors_prov, marker_opacity=0.8,
            text=[f"{c} insiden (avg:{s:.0f})"
                  for c,s in zip(df_prov_s["incident_count"],
                                  df_prov_s["avg_severity"])],
            textfont=dict(size=10, color="rgba(255,255,255,0.6)"),
            textposition="outside",
            hovertemplate="%{y}<br>Insiden: %{x}<extra></extra>",
        ))
        fig_prov.update_layout(**PLOT, height=max(300, len(df_prov_s)*35),
            title=dict(text="Jumlah Insiden per Provinsi",
                       font=dict(size=12, color="rgba(255,255,255,0.5)"), x=0),
        )
        st.plotly_chart(fig_prov, width='stretch')

        # Bubble map provinsi
        st.markdown('<div class="section-title">BUBBLE MAP PROVINSI</div>',
                    unsafe_allow_html=True)

        prov_coords = []
        for _, row in df_prov.iterrows():
            if row["province"] in PROVINCES:
                coord = PROVINCES[row["province"]]
                prov_coords.append({
                    "province":  row["province"],
                    "lat":       coord["lat"],
                    "lon":       coord["lon"],
                    "count":     row["incident_count"],
                    "avg_sev":   row["avg_severity"],
                    "dom_type":  row["dominant_type"],
                })

        if prov_coords:
            df_bc = pd.DataFrame(prov_coords)
            fig_bc = go.Figure(go.Scattermap(
                lat=df_bc["lat"], lon=df_bc["lon"],
                mode="markers+text",
                marker=dict(
                    size=df_bc["count"].apply(lambda x: min(10+x*5, 50)),
                    color=df_bc["avg_sev"].apply(get_sev_color),
                    opacity=0.7,
                ),
                text=df_bc["province"].apply(lambda x: x[:10]),
                textfont=dict(size=8, color="white"),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Insiden: %{customdata[0]}<br>"
                    "Avg Severity: %{customdata[1]:.0f}/100<extra></extra>"
                ),
                customdata=df_bc[["count","avg_sev"]].values,
                name="Provinsi",
            ))
            fig_bc.update_layout(
                map=dict(style="carto-darkmatter",
                            center=dict(lat=-2.5, lon=118.0), zoom=3.5),
                paper_bgcolor="#0a0d0a",
                height=480,
                margin=dict(l=0,r=0,t=0,b=0),
            )
            st.plotly_chart(fig_bc, width='stretch')

        # Tabel ringkasan
        st.markdown('<div class="section-title">RINGKASAN PER PROVINSI</div>',
                    unsafe_allow_html=True)
        df_prov_disp = df_prov.copy()
        df_prov_disp["severity_label"] = df_prov_disp["avg_severity"].apply(get_sev_label)
        df_prov_disp["tipe_dominan"]   = df_prov_disp["dominant_type"].apply(
            lambda x: INCIDENT_TYPES.get(x,{}).get("label", x)
        )
        st.dataframe(
            df_prov_disp[["province","incident_count","avg_severity","severity_label","tipe_dominan"]]
            .rename(columns={
                "province":"Provinsi",
                "incident_count":"Jumlah Insiden",
                "avg_severity":"Avg Severity",
                "severity_label":"Level",
                "tipe_dominan":"Tipe Dominan"
            }).sort_values("Jumlah Insiden", ascending=False),
            width='stretch', hide_index=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HOTSPOT
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">HOTSPOT INSIDEN</div>', unsafe_allow_html=True)

    if df_hs.empty:
        st.info("Belum ada data hotspot.")
    else:
        col_hs, col_hsc = st.columns([1, 2])

        with col_hs:
            for _, row in df_hs.head(10).iterrows():
                sc    = row["avg_sev"]
                color = get_sev_color(sc)
                info  = INCIDENT_TYPES.get(row["inc_type"], {})
                st.markdown(f"""
                <div class="hotspot-card">
                    <div style="width:36px;height:36px;border-radius:50%;
                                background:{color}22;border:2px solid {color};
                                display:flex;align-items:center;justify-content:center;
                                font-size:1rem;flex-shrink:0">
                        {info.get('icon','📍')}
                    </div>
                    <div style="flex:1">
                        <div style="font-weight:500;font-size:.84rem">{row['location']}</div>
                        <div style="font-family:'DM Mono',monospace;font-size:.68rem;
                                    color:rgba(255,255,255,.4)">
                            {row['province']} · {row['count']} insiden ·
                            <span style="color:{color}">SEV:{sc:.0f}</span>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

        with col_hsc:
            # Scatter plot hotspot
            df_hs_plot = df_hs.copy()
            df_hs_plot["color"] = df_hs_plot["avg_sev"].apply(get_sev_color)
            df_hs_plot["label"] = df_hs_plot["inc_type"].apply(
                lambda x: INCIDENT_TYPES.get(x,{}).get("label",x)
            )

            fig_hs = go.Figure(go.Scattermap(
                lat=df_hs_plot["lat"], lon=df_hs_plot["lon"],
                mode="markers",
                marker=dict(
                    size=df_hs_plot["count"].apply(lambda x: min(10+x*8, 60)),
                    color=df_hs_plot["avg_sev"].apply(get_sev_color),
                    opacity=0.75,
                ),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Insiden: %{customdata[1]}<br>"
                    "Avg Severity: %{customdata[2]:.0f}/100<br>"
                    "Tipe: %{customdata[3]}<extra></extra>"
                ),
                customdata=df_hs_plot[["location","count","avg_sev","label"]].values,
            ))
            fig_hs.update_layout(
                map=dict(style="carto-darkmatter",
                            center=dict(lat=-2.5, lon=118.0), zoom=4),
                paper_bgcolor="#0a0d0a",
                height=440,
                margin=dict(l=0,r=0,t=0,b=0),
            )
            st.plotly_chart(fig_hs, width='stretch')

    # Insiden terbaru per lokasi
    st.markdown('<div class="section-title">INSIDEN TERBARU</div>', unsafe_allow_html=True)
    for _, row in df_inc.head(8).iterrows():
        sc    = row["severity"]
        color = get_sev_color(sc)
        lvl   = get_sev_label(sc)
        info  = INCIDENT_TYPES.get(row["inc_type"], {})
        pub   = row["published_at"].strftime("%d %b %Y") \
                if pd.notna(row["published_at"]) else ""
        box_cls = "critical" if sc>=75 else "high" if sc>=50 else "medium" if sc>=25 else "low"
        url   = row.get("url","") or "#"

        st.markdown(f"""
        <div class="incident-card" style="border-left:3px solid {color}">
            <div style="display:flex;justify-content:space-between;gap:8px">
                <div style="font-weight:500;font-size:.85rem;flex:1">{row['title']}</div>
                <div style="font-family:'DM Mono',monospace;font-size:.75rem;
                            color:{color};white-space:nowrap">{sc:.0f}/100</div>
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:.68rem;
                        color:rgba(255,255,255,.35);margin-top:5px;display:flex;gap:10px;flex-wrap:wrap">
                <span>&#128205; {row['location']}, {row['province']}</span>
                <span>{info.get('icon','')} {info.get('label','')}</span>
                <span>{pub}</span>
                <span style="color:{color}">{lvl}</span>
                <a href="{url}" target="_blank"
                   style="color:rgba(46,204,113,.4);text-decoration:none">&#8599; SOURCE</a>
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ANALISIS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">ANALISIS DISTRIBUSI INSIDEN</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # Pie chart tipe insiden
        type_counts = df_inc["inc_type"].value_counts()
        colors_pie  = [INCIDENT_TYPES.get(k,{}).get("color","#888")
                       for k in type_counts.index]
        labels_pie  = [INCIDENT_TYPES.get(k,{}).get("label",k)
                       for k in type_counts.index]

        fig_pie = go.Figure(go.Pie(
            labels=labels_pie, values=type_counts.values,
            marker_colors=colors_pie, hole=0.55,
            textfont=dict(size=10, family="DM Mono"),
            hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
        ))
        fig_pie.update_layout(
            **{k:v for k,v in PLOT.items() if k not in ["xaxis","yaxis"]},
            height=280,
            title=dict(text="Distribusi Tipe Insiden",
                       font=dict(size=12, color="rgba(255,255,255,0.5)"), x=0),
            showlegend=True,
            legend=dict(font=dict(color="rgba(255,255,255,0.5)",size=9),
                        orientation="h", y=-0.15),
            annotations=[dict(text=f"<b>{n}</b><br>Insiden",
                              x=0.5, y=0.5, font_size=13,
                              font_color="#2ECC71", showarrow=False)],
        )
        st.plotly_chart(fig_pie, width='stretch')

    with c2:
        # Bar severity distribution
        bins   = [0, 25, 50, 75, 100]
        labels = ["🟢 Rendah (0-25)","🟡 Sedang (25-50)","🟠 Tinggi (50-75)","🔴 Kritis (75-100)"]
        colors_sev = ["#2ECC71","#F39C12","#E67E22","#E74C3C"]
        counts_sev = pd.cut(df_inc["severity"], bins=bins, labels=labels).value_counts().reindex(labels)

        fig_sev = go.Figure(go.Bar(
            x=labels, y=counts_sev.values,
            marker_color=colors_sev, marker_opacity=0.8,
            hovertemplate="%{x}<br>Jumlah: %{y}<extra></extra>",
        ))
        fig_sev.update_layout(**PLOT, height=280,
            title=dict(text="Distribusi Level Severity",
                       font=dict(size=12, color="rgba(255,255,255,0.5)"), x=0),
        )
        st.plotly_chart(fig_sev, width='stretch')

    # Timeline insiden
    st.markdown('<div class="section-title">TIMELINE INSIDEN</div>', unsafe_allow_html=True)
    df_tl = df_inc.dropna(subset=["published_at"]).copy()
    if not df_tl.empty:
        df_tl["date"] = df_tl["published_at"].dt.date
        tl = df_tl.groupby("date").agg(
            count=("id","count"),
            avg_sev=("severity","mean"),
        ).reset_index()

        fig_tl = go.Figure()
        fig_tl.add_trace(go.Bar(
            x=tl["date"], y=tl["count"], name="Jumlah Insiden",
            marker_color="#2ECC71", marker_opacity=0.7,
            yaxis="y1",
        ))
        fig_tl.add_trace(go.Scatter(
            x=tl["date"], y=tl["avg_sev"], name="Avg Severity",
            line=dict(color="#E74C3C", width=2), mode="lines+markers",
            marker=dict(size=6), yaxis="y2",
        ))
        # Buat layout tanpa yaxis dari PLOT (hindari konflik dual axis)
        _plot_no_ax = {k:v for k,v in PLOT.items() if k not in ["xaxis","yaxis"]}
        fig_tl.update_layout(**_plot_no_ax, height=250,
            title=dict(text="Volume Insiden &#38; Severity per Hari",
                       font=dict(size=12, color="rgba(255,255,255,0.5)"), x=0),
            xaxis=dict(showgrid=True, gridcolor="#1a3d1a", showline=False,
                       tickfont=dict(color="rgba(255,255,255,0.4)")),
            yaxis=dict(title="Insiden", showgrid=True, gridcolor="#1a3d1a",
                       tickfont=dict(color="rgba(255,255,255,0.4)")),
            yaxis2=dict(title="Severity", overlaying="y", side="right",
                        showgrid=False, range=[0,100],
                        tickfont=dict(color="rgba(255,255,255,0.4)")),
            legend=dict(orientation="h", y=-0.25,
                        font=dict(color="rgba(255,255,255,0.4)", size=10)),
            hovermode="x unified",
        )
        st.plotly_chart(fig_tl, width='stretch')

    # Sumber terbanyak
    st.markdown('<div class="section-title">SUMBER BERITA</div>', unsafe_allow_html=True)
    src_counts = df_inc["source"].value_counts().head(10)
    fig_src = go.Figure(go.Bar(
        x=src_counts.values, y=src_counts.index,
        orientation="h", marker_color="#2ECC71", marker_opacity=0.7,
        hovertemplate="%{y}: %{x} insiden<extra></extra>",
    ))
    fig_src.update_layout(**PLOT, height=max(200, len(src_counts)*35),
        title=dict(text="Sumber Berita Insiden",
                   font=dict(size=12, color="rgba(255,255,255,0.5)"), x=0),
    )
    st.plotly_chart(fig_src, width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — LAPORAN
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">GEOSPATIAL INTELLIGENCE REPORT</div>',
                unsafe_allow_html=True)

    now_rpt   = datetime.now().strftime("%d %B %Y %H:%M")
    top5_prov = df_prov.nlargest(5,"incident_count") if not df_prov.empty else pd.DataFrame()
    top5_hs   = df_hs.nlargest(5,"count") if not df_hs.empty else pd.DataFrame()
    top3_inc  = df_inc.nlargest(3,"severity")

    type_breakdown = df_inc["inc_type"].value_counts()
    type_lines = "\n".join(
        f"   {INCIDENT_TYPES.get(k,{}).get('label',k):<25}: {v} insiden"
        for k, v in type_breakdown.items()
    )
    prov_lines = "\n".join(
        f"   {i+1}. {row['province']:<30}: {row['incident_count']} insiden (avg sev: {row['avg_severity']:.0f})"
        for i, (_, row) in enumerate(top5_prov.iterrows())
    ) if not top5_prov.empty else "   Tidak ada data"

    hs_lines = "\n".join(
        f"   {i+1}. {row['location']}, {row['province']:<20}: {row['count']} insiden"
        for i, (_, row) in enumerate(top5_hs.iterrows())
    ) if not top5_hs.empty else "   Tidak ada data"

    inc_lines = "\n".join(
        f"   [{r['source']}] {str(r['title'])[:60]}... (SEV:{r['severity']:.0f})"
        for _, r in top3_inc.iterrows()
    )

    report_text = f"""
╔══════════════════════════════════════════════════════════════════╗
║         LAPORAN GEOSPATIAL INTELLIGENCE (GEOINT)                ║
║              PEMETAAN INSIDEN — INDONESIA                        ║
╚══════════════════════════════════════════════════════════════════╝

NOMOR LAPORAN  : GEOINT-{monitor_id:04d}-{datetime.now().strftime('%Y%m%d')}
TANGGAL        : {now_rpt}
SISTEM         : GEO INTEL Dashboard v1.0
KEYWORD        : {monitor_kw}
CAKUPAN        : Seluruh Indonesia (34 Provinsi)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. RINGKASAN EKSEKUTIF
   Total Insiden Terpetakan : {n}
   Insiden Kritis (>=75)    : {n_kritis}
   Insiden Tinggi (>=50)    : {n_tinggi}
   Provinsi Terdampak       : {n_prov}
   Rata-rata Severity       : {avg_sev:.1f}/100
   Tipe Dominan             : {INCIDENT_TYPES.get(top_type,{}).get('label', top_type)}

2. BREAKDOWN TIPE INSIDEN
{type_lines}

3. PROVINSI PALING TERDAMPAK
{prov_lines}

4. HOTSPOT LOKASI
{hs_lines}

5. INSIDEN PALING KRITIS
{inc_lines}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[AKHIR LAPORAN] — GEO INTEL System v1.0
Sumber: NewsAPI + BNPB (Data Publik)
"""

    st.markdown(f'<div class="report-box">{report_text}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇ DOWNLOAD LAPORAN (.txt)",
            data=report_text,
            file_name=f"geoint_{monitor_kw.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )
    with c2:
        csv = df_inc[["title","source","published_at","location","province",
                      "lat","lon","inc_type","severity","url"]].to_csv(index=False)
        st.download_button(
            "⬇ EXPORT DATA (.csv)",
            data=csv,
            file_name=f"geoint_data_{monitor_kw.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
