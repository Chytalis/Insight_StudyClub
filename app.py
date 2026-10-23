import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard Spotify", page_icon="🎧", layout="wide")
sns.set_theme(style="whitegrid", font_scale=1.1)
GREEN = "#1DB954"

# =========================================================
# LOAD DATA (data yang sudah di-cleaning)
# =========================================================
def fix_encoding(s):
    """Perbaiki teks rusak seperti 'BeyoncÃ©' -> 'Beyoncé'."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s

@st.cache_data
def load_data():
    df = pd.read_csv("clean_dataset.csv")
    df["main_genre"] = df["main_genre"].replace("set()", "Unknown")  # sisa genre kosong
    df["artist"] = df["artist"].map(fix_encoding)
    df["song"] = df["song"].map(fix_encoding)
    df["explicit"] = df["explicit"].astype(bool)
    return df

def fig_png(fig):
    """Ubah figure matplotlib menjadi bytes PNG untuk tombol unduh."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    return buf.getvalue()

df = load_data()

# =========================================================
# SIDEBAR: FILTER
# =========================================================
st.sidebar.header("⚙️ Filter Data")
y_min, y_max = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider("Rentang tahun", y_min, y_max, (y_min, y_max))

genre_opts = sorted(df["main_genre"].unique())
sel_genre = st.sidebar.multiselect("Genre utama", genre_opts, default=genre_opts)

pop_range = st.sidebar.slider("Rentang popularitas", 0, 100, (0, 100))
exp_opt = st.sidebar.radio("Jenis lagu", ["Semua", "Explicit", "Non-explicit"])

mask = (df["year"].between(*year_range)
        & df["main_genre"].isin(sel_genre)
        & df["popularity"].between(*pop_range))
if exp_opt == "Explicit":
    mask &= df["explicit"]
elif exp_opt == "Non-explicit":
    mask &= ~df["explicit"]
d = df[mask]

st.sidebar.caption(f"{len(d):,} dari {len(df):,} lagu terpilih")
if d.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Longgarkan filter di sidebar.")
    st.stop()

st.sidebar.download_button("⬇️ Unduh data terfilter (CSV)",
                           d.to_csv(index=False).encode("utf-8"),
                           "spotify_terfilter.csv", "text/csv")

# =========================================================
# HEADER
# =========================================================
st.title("🎧 Dashboard Analisis Lagu Spotify")
st.caption(
    f"Periode {year_range[0]}–{year_range[1]} · {len(d):,} lagu · "
    "Catatan: data tidak memuat riwayat pencarian/rekomendasi, sehingga "
    "**popularitas lagu** dipakai sebagai pendekatan."
)

# =========================================================
# KPI
# =========================================================
top_artist = d["artist"].value_counts()
genre_cnt = d["main_genre"].value_counts().drop("Unknown", errors="ignore")
best_song = d.sort_values("popularity", ascending=False).iloc[0]

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total lagu", f"{len(d):,}")
k2.metric("Jumlah artis", f"{d['artist'].nunique():,}")
k3.metric("Rata-rata popularitas", f"{d['popularity'].mean():.1f}")
k4.metric("Genre teratas", genre_cnt.index[0] if len(genre_cnt) else "-")
k5.metric("Artis terbanyak", top_artist.index[0], f"{top_artist.iloc[0]} lagu", delta_color="off")
st.success(f"🏆 Lagu terpopuler: **{best_song['song']}** – {best_song['artist']} "
           f"({int(best_song['year'])}, popularitas {int(best_song['popularity'])})")

# =========================================================
# TAB
# =========================================================
tab_home, tab_insight, tab_chart, tab_explore = st.tabs(
    ["🏠 Ringkasan", "📌 Insight", "📊 Grafik", "🔎 Eksplorasi"])

# ---------------------------------------------------------
# TAB 1: RINGKASAN
# ---------------------------------------------------------
with tab_home:
    st.subheader("Top lagu paling populer")
    top_n = st.slider("Jumlah lagu yang ditampilkan", 5, 20, 10, key="top_n")
    tbl = (d.sort_values("popularity", ascending=False)
             .head(top_n)[["artist", "song", "main_genre", "year", "popularity"]]
             .rename(columns={"artist": "Artis", "song": "Lagu", "main_genre": "Genre",
                              "year": "Tahun", "popularity": "Popularitas"})
             .reset_index(drop=True))
    tbl.insert(0, "No", range(1, len(tbl) + 1))
    st.dataframe(
        tbl, hide_index=True,
        column_config={"Popularitas": st.column_config.ProgressColumn(
            "Popularitas", min_value=0, max_value=100, format="%d")})

    st.subheader("Lihat data lengkap")
    with st.expander("Tabel data terfilter"):
        st.dataframe(d.reset_index(drop=True))

# ---------------------------------------------------------
# TAB 2: INSIGHT (teks dari file insight)
# ---------------------------------------------------------
with tab_insight:
    st.header("📌 Insight Dataset Lagu Hits Spotify")
    st.caption("Hasil analisis awal pada ±2.000 lagu, 18 kolom (artis, judul, durasi, tahun, "
               "popularity, fitur audio, dan genre). Grafik memakai data setelah cleaning.")

i1, i2 = tab_insight.columns(2)
with i1:
    st.subheader("1. Gaya musik hits berubah dalam dua dekade")
    st.markdown("""
- Lagu semakin pendek: rata-rata durasi turun dari ±4,1 menit (1999–2003) menjadi ±3,5 menit (2015–2019).
- Lagu semakin "murung": rata-rata valence turun dari 0,61 menjadi 0,49, energi turun dari 0,73 menjadi 0,67.
- Lagu eksplisit semakin banyak: proporsinya naik dari ±23% (1999–2003) menjadi 37% (2015–2019), dan menyentuh 48% pada 2018.
- Danceability tetap tinggi di kisaran 0,63–0,73, jadi lagu tetap enak dipakai berdansa meski suasananya lebih gelap.
""")
    st.subheader("3. Artis lebih menentukan daripada karakter lagu")
    st.markdown("""
- **Paling banyak masuk dataset:** Rihanna (25), Drake (23), Eminem (21), Calvin Harris (20), Britney Spears (19).
- **Rata-rata popularity tertinggi** (minimal 8 lagu): Bruno Mars (77,5), Linkin Park dan Coldplay (74,4), Lady Gaga (72,9), Ed Sheeran (72,8), Eminem (72,6).
- **Lagu paling populer:** "Sweater Weather" (The Neighbourhood, 89) dan "Another Love" (Tom Odell, 88). Eminem punya tiga lagu di 10 teratas.
""")
    st.subheader("5. Lagu eksplisit sedikit lebih populer")
    st.markdown("""
Lagu eksplisit rata-rata mendapat 61,5 poin, sedikit di atas non-eksplisit yang 59,3.
Selisihnya kecil, jadi lebih tepat dibaca sebagai "tidak merugikan" daripada "pendorong popularitas".
""")
with i2:
    st.subheader("2. Fitur audio hampir tidak menjelaskan popularitas")
    st.markdown("""
Korelasi semua fitur dengan popularity sangat kecil (di bawah ±0,06). Danceability, energy, tempo, dan loudness hampir nol.
Fitur yang paling berpengaruh hanya explicit (+0,05) dan instrumentalness (−0,05), dan keduanya tetap lemah.

Artinya, di antara lagu yang sudah jadi hits, resep audio tidak menentukan seberapa populer lagunya.
Faktor lain seperti nama artis, promosi, dan momentum kemungkinan lebih berperan.
""")
    st.subheader("4. Genre")
    st.markdown("""
- Pop mendominasi (±82% lagu punya tag pop), diikuti **hip hop** (39%), **R&B** (23%), dan **Dance/Electronic** (20%).
- Rata-rata popularity tertinggi ada di **metal (68)** dan **rock (63)**, tetapi jumlahnya kecil (metal hanya 66 lagu). **Dance/Electronic** terendah (55).
- Metal dan rock berenergi tinggi tetapi kurang bisa dipakai menari (danceability ±0,51–0,56). Latin paling ceria (valence 0,69).
""")
    st.subheader("6. Catatan kualitas data")
    st.markdown("""
- **126 lagu (6,3%) punya popularity = 0.** Lebih mirip data tidak tercatat atau lagu yang ditarik. Persentasenya naik dari ±2% (awal 2000-an) menjadi 13–18% pada 2013–2017, sehingga rata-rata popularity tahun-tahun itu terlihat turun karena efek data. Tanpa nilai nol, rata-rata naik dari 59,9 ke 63,9.
- **Ada duplikat:** 59 baris identik dan 74 pasangan artis+lagu yang berulang. Setelah dibersihkan tersisa ±1.926 lagu unik.
- **Tahun 1998 dan 2020 hanya berisi 1 dan 3 lagu**, jangan dipakai untuk membaca tren.
- Nama artis bermasalah encoding (misalnya "BeyoncÃ©").
- Kolom genre kadang kosong (`set()`, 22 lagu).
""")

# ---------------------------------------------------------
# TAB 3: GRAFIK
# ---------------------------------------------------------
with tab_chart:

    # ===== 1. HISTOGRAM (Matplotlib) =====
    st.subheader("1. Karakteristik Audio Lagu yang Sering Direkomendasikan Spotify")
    top_pct = st.slider("Definisi lagu 'direkomendasikan' = top berapa persen popularitas?",
                        5, 50, 10, step=5, format="%d%%")
    threshold = d["popularity"].quantile(1 - top_pct / 100)
    top_songs = d[d["popularity"] >= threshold]

    HIST_FEATURES = {
        "danceability": "Danceability", "energy": "Energy", "valence": "Valence",
        "tempo": "Tempo (BPM)", "loudness": "Loudness (dB)", "duration_min": "Durasi (menit)",
    }
    fig1, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, (col, label) in zip(axes.ravel(), HIST_FEATURES.items()):
        lo, hi = d[col].min(), d[col].max()
        bins = np.linspace(lo, hi, 26) if hi > lo else 10
        ax.hist(d[col], bins=bins, density=True, alpha=0.45, color="#9E9E9E", label="Semua lagu")
        ax.hist(top_songs[col], bins=bins, density=True, alpha=0.65, color=GREEN,
                label=f"Lagu top {top_pct}%")
        ax.axvline(d[col].mean(), color="#555555", ls="--", lw=1.5)
        ax.axvline(top_songs[col].mean(), color="#0B7A33", ls="--", lw=1.5)
        ax.set_title(label, fontweight="bold")
        ax.set_xlabel("Nilai")
        ax.set_ylabel("Proporsi lagu")
    axes[0, 0].legend(frameon=False)
    fig1.tight_layout()
    st.pyplot(fig1)

    cols1 = list(HIST_FEATURES)
    z = ((top_songs[cols1].mean() - d[cols1].mean()) / d[cols1].std().replace(0, np.nan)).abs().fillna(0)
    best = z.idxmax()
    st.markdown(
        f"💡 **Insight otomatis:** {len(top_songs):,} lagu dengan popularitas ≥ {threshold:.0f}. "
        f"Selisih rata-rata terbesar (relatif terhadap sebaran) ada pada **{HIST_FEATURES[best]}** "
        f"(top: {top_songs[best].mean():.2f} vs semua: {d[best].mean():.2f}). "
        "Sebaran yang saling menumpuk berarti fitur tersebut kurang membedakan lagu top "
        "dari lagu lain (sejalan dengan Insight 2).")
    st.download_button("⬇️ Unduh grafik 1 (PNG)", fig_png(fig1), "histogram_audio.png", "image/png")
    with st.expander("Lihat rata-rata tiap fitur"):
        st.dataframe(pd.DataFrame({
            "Lagu top": top_songs[cols1].mean(),
            "Semua lagu": d[cols1].mean(),
        }).rename(index=HIST_FEATURES).round(3))
    st.divider()

    # ===== 2. LINE CHART (Seaborn) =====
    st.subheader("2. Seberapa Sering Artis Muncul di Daftar Lagu Populer per Tahun?")
    n_artist = st.slider("Jumlah artis teratas yang ditampilkan", 3, 8, 5)
    top_artists = d["artist"].value_counts().head(n_artist).index
    trend = (d[d["artist"].isin(top_artists)]
             .groupby(["year", "artist"]).size().reset_index(name="jumlah_lagu"))
    full = pd.MultiIndex.from_product(
        [range(year_range[0], year_range[1] + 1), top_artists], names=["year", "artist"])
    trend = trend.set_index(["year", "artist"]).reindex(full, fill_value=0).reset_index()

    fig2, ax2 = plt.subplots(figsize=(11, 4.8))
    sns.lineplot(data=trend, x="year", y="jumlah_lagu", hue="artist",
                 marker="o", linewidth=2.2, ax=ax2)
    ax2.set_xlabel("Tahun")
    ax2.set_ylabel("Jumlah lagu di daftar populer")
    ax2.yaxis.get_major_locator().set_params(integer=True)
    ax2.legend(title="Artis", bbox_to_anchor=(1.01, 1), loc="upper left", frameon=False)
    sns.despine()
    st.pyplot(fig2)

    lead = top_artists[0]
    peak = trend[trend["artist"] == lead].sort_values("jumlah_lagu").iloc[-1]
    st.markdown(
        f"💡 **Insight otomatis:** **{lead}** punya lagu terbanyak ({int(top_artist.iloc[0])} lagu), "
        f"dengan puncak {int(peak['jumlah_lagu'])} lagu pada {int(peak['year'])}. "
        "Total lagu: " + " · ".join(f"{a} ({n})" for a, n in top_artist.head(n_artist).items()))
    st.download_button("⬇️ Unduh grafik 2 (PNG)", fig_png(fig2), "tren_artis.png", "image/png")
    st.divider()

    # ===== 3. PIE CHART (Seaborn: tema & palet) =====
    st.subheader("3. Genre yang Paling Sering Dicari Pendengar Spotify")
    n_genre = st.slider("Jumlah genre yang ditampilkan (sisanya digabung 'Lainnya')", 3, 8, 5)
    if genre_cnt.empty:
        st.info("Tidak ada genre yang dikenali pada filter ini.")
    else:
        pie = genre_cnt.head(n_genre).copy()
        if len(genre_cnt) > n_genre:
            pie["Lainnya"] = genre_cnt.iloc[n_genre:].sum()
        pct = pie / pie.sum() * 100
        colors = sns.color_palette("Set2", len(pie))          # palet seaborn

        with sns.axes_style("white"):                          # tema seaborn
            fig3, ax3 = plt.subplots(figsize=(8, 5.5))
            wedges, _ = ax3.pie(
                pie.values, startangle=90, colors=colors, counterclock=False,
                wedgeprops=dict(edgecolor="white", linewidth=2))
            for w, p in zip(wedges, pct.values):
                if p >= 5:                                     # persen hanya di irisan besar
                    ang = np.deg2rad((w.theta1 + w.theta2) / 2)
                    ax3.text(0.65 * np.cos(ang), 0.65 * np.sin(ang), f"{p:.1f}%",
                             ha="center", va="center", fontsize=13, fontweight="bold")
            ax3.legend(wedges, [f"{g}: {p:.1f}% ({n:,} lagu)"
                                for g, p, n in zip(pie.index, pct.values, pie.values)],
                       title="Genre", loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False)
            ax3.axis("equal")
        st.pyplot(fig3)
        st.markdown(f"💡 **Insight otomatis:** genre dominan adalah **{pie.index[0]}** "
                    f"({pct.iloc[0]:.1f}% lagu), diikuti **{pie.index[1] if len(pie) > 1 else '-'}**"
                    + (f" ({pct.iloc[1]:.1f}%)." if len(pie) > 1 else "."))
        st.download_button("⬇️ Unduh grafik 3 (PNG)", fig_png(fig3), "komposisi_genre.png", "image/png")
    st.divider()

    # ===== 4. BAR CHART (Plotly) - top 1 per tahun =====
    st.subheader("4. Genre Lagu Top 1 Spotify pada Setiap Tahun")
    min_n = st.slider("Abaikan tahun dengan jumlah lagu kurang dari", 1, 50, 10,
                      help="Tahun dengan sedikit data (mis. 1998 dan 2020) kurang representatif.")
    cnt = d.groupby("year")["song"].count()
    valid_years = cnt[cnt >= min_n].index
    top1 = (d[d["year"].isin(valid_years)]
            .sort_values(["year", "popularity"], ascending=[True, False])
            .drop_duplicates("year").copy())
    if top1.empty:
        st.info("Tidak ada tahun yang memenuhi batas minimal lagu. Kecilkan nilainya.")
    else:
        top1["label"] = top1["artist"] + " – " + top1["song"]
        fig4 = px.bar(top1, x="year", y="popularity", color="main_genre",
                      hover_data={"label": True, "popularity": True, "year": False},
                      text="popularity", labels={"popularity": "Popularitas", "year": "Tahun",
                                                 "main_genre": "Genre"})
        fig4.update_traces(textposition="outside")
        fig4.update_layout(height=480, xaxis=dict(dtick=1), yaxis=dict(range=[0, 105]),
                           legend=dict(orientation="h", y=-0.2), margin=dict(t=30))
        st.plotly_chart(fig4)
        genre_win = top1["main_genre"].value_counts()
        st.markdown(f"💡 **Insight otomatis:** genre yang paling sering menjadi top 1 adalah "
                    f"**{genre_win.index[0]}** ({genre_win.iloc[0]} dari {len(top1)} tahun).")
        st.download_button("⬇️ Unduh grafik 4 (HTML interaktif)", fig4.to_html(),
                           "top1_per_tahun.html", "text/html")
        with st.expander("Lihat lagu top 1 tiap tahun"):
            st.dataframe(top1[["year", "artist", "song", "main_genre", "popularity"]]
                         .reset_index(drop=True))
    st.divider()

    # ===== 5. HEATMAP KORELASI (Seaborn) =====
    st.subheader("5. Fitur Audio Apa yang Berhubungan dengan Popularitas?")
    corr_cols = ["danceability", "energy", "valence", "acousticness", "speechiness",
                 "liveness", "instrumentalness", "tempo", "loudness", "duration_min",
                 "explicit", "popularity"]
    corr = d[corr_cols].astype(float).corr().fillna(0)
    with sns.axes_style("white"):
        fig5, ax5 = plt.subplots(figsize=(10, 7.5))
        sns.heatmap(corr, mask=np.triu(np.ones_like(corr, dtype=bool), k=1),
                    annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, center=0,
                    linewidths=0.5, annot_kws={"size": 9}, cbar_kws={"shrink": 0.8}, ax=ax5)
    st.pyplot(fig5)
    cp = corr["popularity"].drop("popularity")
    strongest = cp.abs().sort_values(ascending=False).head(3).index
    st.markdown("💡 **Insight otomatis:** korelasi terkuat dengan popularitas: " +
                ", ".join(f"**{f}** (r = {cp[f]:+.2f})" for f in strongest) +
                ". Nilai yang mendekati 0 berarti hubungannya lemah.")
    st.download_button("⬇️ Unduh grafik 5 (PNG)", fig_png(fig5), "heatmap_korelasi.png", "image/png")

# ---------------------------------------------------------
# TAB 4: EKSPLORASI
# ---------------------------------------------------------
with tab_explore:
    artists = sorted(d["artist"].unique())
    by_count = d["artist"].value_counts().index.tolist()

    # ===== A. PENCARIAN ARTIS =====
    st.subheader("🔎 Cari Artis")
    sel_artist = st.selectbox("Ketik atau pilih nama artis", artists,
                              index=artists.index(by_count[0]), key="search_artist")
    a = d[d["artist"] == sel_artist].sort_values("popularity", ascending=False)
    main_g = a["main_genre"].mode().iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Jumlah lagu", len(a))
    m2.metric("Rata-rata popularitas", f"{a['popularity'].mean():.1f}")
    m3.metric("Popularitas tertinggi", int(a["popularity"].max()))
    m4.metric("Genre utama", main_g)
    fig_a = px.bar(a.head(10).sort_values("popularity"), x="popularity", y="song",
                   orientation="h", title=f"Lagu populer {sel_artist}",
                   labels={"popularity": "Popularitas", "song": "Lagu"})
    fig_a.update_traces(marker_color=GREEN)
    st.plotly_chart(fig_a)
    st.dataframe(a[["song", "year", "main_genre", "popularity"]].reset_index(drop=True))
    st.divider()

    # ===== B. BANDINGKAN 2 ARTIS =====
    st.subheader("⚔️ Bandingkan Dua Artis")
    cc1, cc2 = st.columns(2)
    idx_b = artists.index(by_count[1]) if len(by_count) > 1 else 0
    art_a = cc1.selectbox("Artis A", artists, index=artists.index(by_count[0]), key="cmp_a")
    art_b = cc2.selectbox("Artis B", artists, index=idx_b, key="cmp_b")
    if art_a == art_b:
        st.info("Pilih dua artis yang berbeda untuk dibandingkan.")
    else:
        metrics = {
            "Jumlah lagu": lambda x: len(x),
            "Rata-rata popularitas": lambda x: x["popularity"].mean(),
            "Popularitas tertinggi": lambda x: x["popularity"].max(),
            "Durasi rata-rata (menit)": lambda x: x["duration_min"].mean(),
            "Tempo rata-rata (BPM)": lambda x: x["tempo"].mean(),
        }
        feats = ["danceability", "energy", "valence", "acousticness"]
        table, long_rows = {}, []
        for name in (art_a, art_b):
            sub = d[d["artist"] == name]
            table[name] = {k: round(float(f(sub)), 2) for k, f in metrics.items()}
            for ft in feats:
                long_rows.append({"Artis": name, "Fitur": ft.capitalize(),
                                  "Nilai rata-rata": float(sub[ft].mean())})
        st.dataframe(pd.DataFrame(table))
        fig_c = px.bar(pd.DataFrame(long_rows), x="Fitur", y="Nilai rata-rata", color="Artis",
                       barmode="group", title="Perbandingan karakter audio",
                       color_discrete_sequence=[GREEN, "#191414"])
        st.plotly_chart(fig_c)
    st.divider()

    # ===== C. REKOMENDASI LAGU MIRIP =====
    st.subheader("🎯 Rekomendasi Lagu Mirip")
    RFEATS = ["danceability", "energy", "valence", "acousticness", "speechiness",
              "liveness", "instrumentalness", "tempo", "loudness"]
    labels = (d["artist"] + " – " + d["song"]).tolist()
    default_label = f"{best_song['artist']} – {best_song['song']}"
    choice = st.selectbox("Pilih sebuah lagu", labels,
                          index=labels.index(default_label), key="rec_song")
    other_artist = st.checkbox("Hanya tampilkan artis lain", value=True)

    X = d[RFEATS]
    Z = ((X - X.mean()) / X.std().replace(0, 1)).fillna(0).to_numpy()
    pos = labels.index(choice)
    v = Z[pos]
    sim = Z @ v / (np.linalg.norm(Z, axis=1) * np.linalg.norm(v) + 1e-9)
    res = d.assign(Kemiripan=((sim + 1) / 2 * 100).round(1)).drop(index=d.index[pos])
    if other_artist:
        res = res[res["artist"] != d.iloc[pos]["artist"]]
    res = res.sort_values("Kemiripan", ascending=False).head(5)
    st.dataframe(
        res[["artist", "song", "main_genre", "year", "popularity", "Kemiripan"]]
        .rename(columns={"artist": "Artis", "song": "Lagu", "main_genre": "Genre",
                         "year": "Tahun", "popularity": "Popularitas"})
        .reset_index(drop=True),
        column_config={"Kemiripan": st.column_config.ProgressColumn(
            "Kemiripan (%)", min_value=0, max_value=100, format="%.1f")})
    st.caption("Kemiripan dihitung dari 9 fitur audio (danceability, energy, valence, "
               "acousticness, speechiness, liveness, instrumentalness, tempo, loudness) "
               "memakai cosine similarity pada data yang sudah distandarisasi. "
               "Ini kemiripan karakter audio, bukan algoritma rekomendasi asli Spotify.")