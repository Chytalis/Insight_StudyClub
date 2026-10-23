# Hasil Data Understanding

## 1. Dataset Overview

Dataset berisi informasi mengenai lagu, artis, genre, tingkat popularitas, dan karakteristik audio. Data tersebut dapat digunakan untuk mengeksplorasi karakteristik lagu serta melihat kemungkinan hubungan antara fitur audio dan skor popularitas lagu.

Dataset awal memiliki jumlah **2.000 baris dan 18 kolom**, dengan rincian berikut:

| Informasi | Hasil |
|---|---:|
| Jumlah baris | 2.000 |
| Jumlah kolom | 18 |
| Artis unik | 835 |
| Judul lagu unik | 1.879 |
| Label genre unik | 59 |
| Rentang tahun | 1998–2020 |

## 2. Data Attributes

| Kategori | Atribut | Deskripsi |
|---|---|---|
| Identitas lagu | `artist`, `song`, `genre`, `year` | Informasi mengenai artis, judul lagu, genre, dan tahun yang tercatat |
| Popularitas dan durasi | `popularity`, `duration_ms`, `explicit` | Skor popularitas, durasi lagu dalam milidetik, dan penanda konten eksplisit |
| Karakteristik audio | `danceability`, `energy`, `key`, `loudness`, `mode`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo` | Fitur untuk mengeksplorasi karakteristik musik dan hubungannya dengan popularitas |

## 3. Initial Data Quality Assessment

Pemeriksaan awal dilakukan untuk mengetahui kondisi dan kualitas dataset sebelum tahap data cleaning.

| Pemeriksaan | Hasil | Tindak lanjut |
|---|---|---|
| Missing values | Tidak ditemukan nilai kosong yang dikenali Pandas | Tetap periksa konsistensi isi data |
| Duplikasi baris | 59 baris duplikat persis | Verifikasi sebelum penghapusan |
| Genre tidak standar | 22 baris memiliki nilai `set()` | Periksa dan tentukan penanganan yang sesuai |
| Rentang tahun | 1998–2020 | Verifikasi kesesuaian dengan sumber dataset |
| Popularity | Minimum 0, maksimum 89, rata-rata 59,87 | Periksa definisi dan skala skor pada dokumentasi sumber |

Terdapat ketidaksesuaian antara periode pada judul dataset Kaggle, yaitu 2018–2026, dan rentang tahun yang ditemukan dalam file, yaitu 1998–2020. Sumber dataset dan definisi kolom `year` perlu diverifikasi sebelum analisis tren tahunan dilakukan.

## 4. Initial Findings

Beberapa temuan awal dari pemeriksaan dataset adalah:

- **Genre:** Label `pop` merupakan kategori dengan jumlah baris terbanyak, yaitu 428 baris. Label kombinasi genre, seperti `hip hop, pop` dan `hip hop, pop, R&B`, dicatat sebagai kategori terpisah.
- **Explicit content:** Sebanyak 1.449 baris memiliki nilai `explicit = False`, sedangkan 551 baris memiliki nilai `explicit = True`.
- **Duration:** Durasi lagu berada pada rentang 113.000–300.000 milidetik, atau sekitar 1 menit 53 detik hingga 5 menit.
- **Popularity:** Skor popularitas memiliki rata-rata 59,87 dan median 65,5.
- **Audio features:** Pemeriksaan awal menunjukkan bahwa fitur `danceability`, `energy`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, dan `valence` berada pada rentang 0–1.

Temuan tersebut merupakan gambaran awal dari data mentah dan belum menjadi kesimpulan akhir mengenai tren musik atau faktor yang memengaruhi popularitas lagu.

## 5. Initial Correlation Analysis

Pemeriksaan korelasi linear awal menunjukkan bahwa hubungan antara `popularity` dan fitur numerik yang diperiksa cenderung lemah.

| Variabel | Korelasi |
|---|---:|
| `duration_ms` | 0,051 |
| `loudness` | 0,031 |
| `acousticness` | 0,025 |
| `danceability` | -0,004 |
| `energy` | -0,014 |
| `instrumentalness` | -0,048 |

Nilai korelasi tersebut dihitung dari data mentah sebelum penanganan duplikasi. Hasilnya belum dapat digunakan untuk menyimpulkan hubungan sebab-akibat dan perlu diperiksa kembali setelah data cleaning serta eksplorasi visual.

## 6. Data Preparation Recommendations

Berdasarkan pemeriksaan awal, beberapa langkah yang direkomendasikan sebelum tahap Exploratory Data Analysis (EDA) adalah:

1. Memverifikasi sumber dataset, periode data, dan definisi setiap atribut penting.
2. Memeriksa 59 baris duplikat persis sebelum memutuskan apakah akan dihapus.
3. Menelusuri dan menangani 22 nilai `set()` pada kolom `genre`.
4. Memastikan tipe data dan konsistensi nilai setiap kolom.
5. Melakukan EDA untuk mengeksplorasi distribusi popularitas, genre, artis, serta hubungan fitur audio dengan popularitas.
6. Mendokumentasikan seluruh perubahan agar proses analisis dapat ditelusuri.

## 7. Conclusion

Berdasarkan Data Understanding, dataset menyediakan atribut yang dapat digunakan untuk mengeksplorasi karakteristik lagu dan skor popularitas. Namun, masih terdapat beberapa hal yang perlu diverifikasi, terutama ketidaksesuaian periode tahun, baris duplikat, dan nilai genre yang tidak standar.

Hasil Data Understanding ini menjadi dasar bagi tahap data cleaning, EDA, dan pengembangan dashboard menggunakan Streamlit. Insight dan rekomendasi akhir akan ditentukan berdasarkan hasil analisis setelah kualitas data diperiksa dan ditangani.
