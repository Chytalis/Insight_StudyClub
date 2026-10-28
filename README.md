# 🎧 Dashboard Analisis Lagu Spotify

Dashboard interaktif berbasis **Streamlit** untuk menganalisis ±2.000 lagu hits Spotify (1998-2020): karakter audio, genre, artis, dan hubungannya dengan skor popularitas.

Link : https://studyclub2026insight.streamlit.app/

> Proyek  Study Club Data Analyst Kelompok 1

## 👥 Tim
- Line Budiarti
- Bunga Aulia Raya
- Suci Kartika
- Anas Sutanto
- Safa Nabil Kurniawan
- ALSYA PUTRI BELQISH
= Bilqis luthfiazra danies
= Maulida Aulia Agsan
= Senu Aulia

## 🎯 Tujuan
1. Seperti apa karakteristik audio lagu yang masuk kelompok paling populer?
2. Artis dan genre apa yang paling sering muncul, dan bagaimana polanya dari tahun ke tahun?
3. Apakah fitur audio (danceability, energy, tempo, dan lainnya) menjelaskan skor popularitas?
4. Bagaimana gaya musik hits berubah dalam dua dekade terakhir?

> **Catatan:** data tidak memuat riwayat pencarian atau rekomendasi Spotify, sehingga **skor popularitas lagu** dipakai sebagai pendekatan.

---

## 🗂️ Data Understanding

**Sumber:** dataset lagu Spotify dari Kaggle [...tambahkan tautan...]. Periode yang ditemukan di file adalah 1998-2020, sedangkan judul dataset di Kaggle menyebut periode berbeda, jadi sumber dan definisi kolom `year` perlu diverifikasi.

| Informasi | Data awal (`raw_dataset.csv`) | Data bersih (`clean_dataset.csv`) |
|---|---:|---:|
| Jumlah baris | 2.000 | 1.926 |
| Jumlah kolom | 18 | 21 |
| Artis unik | 835 | 835 |
| Judul lagu unik | 1.879 | 1.879 |
| Rentang tahun | 1998-2020 | 1998-2020 |
| Baris duplikat | 59 (persis) | 0 |
| Rata-rata popularitas | 59,87 | 59,66 |

**Atribut**

| Kategori | Kolom |
|---|---|
| Identitas lagu | `artist`, `song`, `genre`, `year` |
| Popularitas dan durasi | `popularity` (0-100), `duration_ms`, `explicit` |
| Karakter audio | `danceability`, `energy`, `key`, `loudness`, `mode`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo` |
| **Kolom turunan (cleaning)** | `duration_min` (durasi dalam menit), `main_genre` (satu genre utama per lagu), `mode_label` (Major/Minor) |

**Masalah kualitas data dan penanganannya**

| Masalah | Kondisi awal | Penanganan |
|---|---|---|
| Baris duplikat | 59 baris identik, ditambah 15 pasangan artis+judul yang berulang (total 74 pasang berulang) | Dihapus, tersisa 1.926 lagu |
| Genre kosong | 22 lagu bernilai `set()` | Diganti label `Unknown` saat data dimuat; tidak dihitung pada grafik genre |
| Teks rusak (encoding) | Nama artis/judul seperti "BeyoncÃ©" | Diperbaiki otomatis saat data dimuat di `app.py` |
| Popularitas = 0 | 126 lagu (6,3%) pada data awal | **Tidak dihapus**: masih ada 124 baris di data bersih. Lebih mirip data tidak tercatat atau lagu yang ditarik, jadi perlu diperhatikan saat membaca rata-rata |
| Tahun dengan data sangat sedikit | 1998 hanya 1 lagu, 2020 hanya 3 lagu | Tidak dihapus; dashboard menyediakan batas minimal lagu per tahun pada grafik 4 |

---

## 🖥️ Fitur Dashboard

**Filter (sidebar)**
- Rentang tahun, genre utama, rentang popularitas, dan jenis lagu (semua, explicit, non-explicit)
- Unduh data terfilter (CSV)
- Semua KPI, tabel, dan grafik mengikuti filter

**Empat tab**

| Tab | Isi |
|---|---|
| 🏠 Ringkasan | Tabel top lagu terpopuler (jumlah bisa diatur 5-20) dan tabel data lengkap |
| 📌 Insight | Enam insight hasil analisis (lihat bagian berikut) |
| 📊 Grafik | Lima grafik dengan insight otomatis dan tombol unduh |
| 🔎 Eksplorasi | Cari artis, bandingkan dua artis, rekomendasi lagu mirip |

**Lima grafik**

| # | Grafik | Library | Pertanyaan |
|---|---|---|---|
| 1 | Histogram karakter audio (6 fitur): semua lagu vs top X% populer | Matplotlib | Seperti apa karakter lagu paling populer? |
| 2 | Garis jumlah lagu per tahun untuk artis teratas | Seaborn | Seberapa sering artis muncul tiap tahun? |
| 3 | Pie komposisi genre utama | Matplotlib + palet Seaborn | Genre apa yang dominan? |
| 4 | Bar lagu top 1 tiap tahun, diwarnai genre | Plotly | Genre apa yang menjadi top 1 pada tiap tahun? |
| 5 | Heatmap korelasi fitur audio dengan popularitas | Seaborn | Fitur apa yang berhubungan dengan popularitas? |

**Fitur interaktif lain**
- Slider definisi lagu "direkomendasikan" (top 5-50% popularitas), jumlah artis, jumlah genre, dan batas minimal lagu per tahun
- **Cari Artis:** metrik, grafik lagu terpopuler, dan tabel lagu per artis
- **Bandingkan Dua Artis:** tabel metrik dan grafik perbandingan karakter audio
- **Rekomendasi Lagu Mirip:** 5 lagu paling mirip berdasarkan *cosine similarity* pada 9 fitur audio yang sudah distandarisasi. Ini kemiripan karakter audio, bukan algoritma rekomendasi asli Spotify.
- Tombol unduh grafik (PNG, dan HTML interaktif untuk grafik 4)

---

## 💡 Ringkasan Insight

### Enam insight utama (tab Insight)

1. **Gaya musik hits berubah dalam dua dekade.** Durasi rata-rata turun dari ±4,1 menit (1999-2003) menjadi ±3,5 menit (2015-2019). Valence turun dari 0,61 menjadi 0,49 dan energi dari 0,73 menjadi 0,67, jadi lagu terdengar lebih "murung". Proporsi lagu eksplisit naik dari ±23% menjadi 37%, dan menyentuh 48% pada 2018. Danceability tetap tinggi (0,63-0,73).
2. **Fitur audio hampir tidak menjelaskan popularitas.** Semua korelasi dengan popularitas berada di bawah ±0,06. Di antara lagu yang sudah menjadi hits, resep audio tidak menentukan seberapa populer sebuah lagu. Faktor seperti nama artis, promosi, dan momentum kemungkinan lebih berperan.
3. **Artis lebih menentukan daripada karakter lagu.** Artis paling banyak masuk dataset: Rihanna, Drake, Eminem, Calvin Harris, dan Britney Spears. Rata-rata popularitas tertinggi (minimal 8 lagu): Bruno Mars (77,5), Linkin Park dan Coldplay (74,4), Lady Gaga (72,9), Ed Sheeran (72,8), Eminem (72,6). Lagu paling populer: "Sweater Weather" (The Neighbourhood, 89) dan "Another Love" (Tom Odell, 88).
4. **Genre.** Dihitung dari seluruh tag genre per lagu, pop muncul pada ±82% lagu, diikuti hip hop (39%), R&B (23%), dan Dance/Electronic (20%). Rata-rata popularitas tertinggi ada pada metal (68) dan rock (63), tetapi jumlahnya kecil (metal hanya 66 lagu). Dance/Electronic terendah (55). Metal dan rock berenergi tinggi tetapi kurang bisa dipakai menari, dan latin paling ceria (valence 0,69).
5. **Lagu eksplisit sedikit lebih populer** (rata-rata 61,5 vs 59,3). Selisihnya kecil, jadi lebih tepat dibaca sebagai "tidak merugikan" daripada "pendorong popularitas".
6. **Catatan kualitas data.** Lagu dengan popularitas 0 naik dari ±2% pada awal 2000-an menjadi 13-18% pada 2013-2017, sehingga rata-rata popularitas tahun-tahun itu terlihat turun karena efek data. Tanpa nilai nol, rata-rata naik dari 59,9 ke 63,9.

### Insight otomatis dashboard (filter bawaan: seluruh data)

| Bagian | Hasil |
|---|---|
| KPI | 1.926 lagu, 835 artis, rata-rata popularitas 59,7; genre teratas pop; artis terbanyak Rihanna (23 lagu) |
| Lagu terpopuler | "Sweater Weather" - The Neighbourhood (2013, popularitas 89) |
| Grafik 1 (top 10%, popularitas ≥ 78, 225 lagu) | Selisih terbesar ada pada **Energy** (0,69 vs 0,72 untuk semua lagu). Sebaran saling menumpuk, jadi fitur audio kurang membedakan lagu top |
| Grafik 2 (5 artis teratas) | Rihanna terbanyak, dengan puncak 5 lagu pada 2008 |
| Grafik 3 (genre utama) | Pop **47,4%**, diikuti hip hop **39,1%** |
| Grafik 4 (tahun dengan ≥ 10 lagu) | **Hip hop** paling sering menjadi top 1 (13 dari 21 tahun) |
| Grafik 5 (korelasi terkuat) | `duration_min` (+0,05), `instrumentalness` (-0,05), `explicit` (+0,04): semuanya lemah |

> **Catatan membaca angka:** Grafik 3 memakai `main_genre` (satu label per lagu), sedangkan Insight 4 menghitung semua tag genre per lagu. Karena itu pop tampil 47,4% pada pie tetapi ±82% pada Insight 4. Keduanya benar menurut definisinya masing-masing. Angka insight statis sebagian dihitung sebelum cleaning dan sebagian sesudahnya, sehingga selisih kecil (beberapa lagu atau di bawah 1 poin) dengan angka di dashboard wajar terjadi.

---

## ⚠️ Keterbatasan
- Popularitas adalah pendekatan, bukan data pencarian atau rekomendasi Spotify yang sebenarnya.
- Dataset hanya memuat lagu yang sudah menjadi hits, sehingga kesimpulan tentang "apa yang membuat lagu populer" tidak berlaku untuk seluruh lagu.
- Korelasi tidak sama dengan sebab-akibat.
- Genre dengan jumlah lagu kecil (metal, latin, dan lainnya) kurang andal untuk dibandingkan.
- Tahun 1998 dan 2020 hanya berisi 1 dan 3 lagu, jangan dipakai untuk membaca tren.
- Nilai popularitas 0 masih ada pada data bersih dan memengaruhi rata-rata popularitas.
- Rekomendasi lagu hanya berdasarkan kemiripan karakter audio.

---

## 🚀 Cara Menjalankan

**Prasyarat:** Python 3.9 atau lebih baru.

1. **Clone repository**
```bash
   git clone <url-repository>
   cd <nama-folder>
```

2. **Buat dan aktifkan virtual environment**
```bash
   python -m venv venv
   venv\Scripts\activate           # Windows
   source venv/bin/activate        # macOS/Linux
```

3. **Instal dependensi**
```bash
   pip install -r requirements.txt
```

4. **Pastikan `clean_dataset.csv` berada di folder yang sama dengan `app.py`**, lalu jalankan perintah berikutnya dari folder tersebut. File dibaca dengan path relatif.

5. **Jalankan aplikasi**
```bash
   streamlit run app.py
```
   Browser terbuka otomatis di `http://localhost:8501`.

**Isi `requirements.txt`**
```
streamlit
pandas
numpy
matplotlib
seaborn
plotly
```

---

## 📁 Struktur Proyek
```
.
├── app.py                # dashboard Streamlit
├── clean_dataset.csv     # data hasil cleaning (1.926 baris, 21 kolom)
├── raw_dataset.csv       # data awal (2.000 baris, 18 kolom)
├── requirements.txt
├── notebooks/            # data understanding, cleaning, EDA [...]
└── README.md
```

## 🛠️ Teknologi
Python · Streamlit · Pandas · NumPy · Matplotlib · Seaborn · Plotly

## 📚 Sumber Data
Dataset lagu hits Spotify, Kaggle. [...tambahkan tautan dataset...]
