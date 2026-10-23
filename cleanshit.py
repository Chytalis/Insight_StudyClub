import pandas as pd
import numpy as np

# =========================================================
# 1. LOAD DATA
# =========================================================
# encoding='utf-8-sig' menghapus karakter BOM di nama kolom pertama ("\ufeffartist")
df = pd.read_csv("raw_dataset.csv", encoding="utf-8-sig")

print("Shape awal:", df.shape)
print(df.head())

# =========================================================
# 2. RAPIKAN NAMA KOLOM
# =========================================================
df.columns = (
    df.columns
    .str.replace("\ufeff", "", regex=False)
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

# =========================================================
# 3. CEK AWAL (info, missing value, duplikat)
# =========================================================
print("\n--- INFO ---")
df.info()

print("\n--- MISSING VALUE ---")
print(df.isnull().sum())

print("\n--- DUPLIKAT (semua kolom) ---")
print(df.duplicated().sum())

print("\n--- STATISTIK DESKRIPTIF ---")
print(df.describe().T)

# =========================================================
# 4. BERSIHKAN KOLOM TEKS
# =========================================================
text_cols = ["artist", "song", "genre"]
for col in text_cols:
    df[col] = (
        df[col]
        .astype("string")
        .str.strip()                                   # hapus spasi di awal/akhir
        .str.replace(r"\s+", " ", regex=True)          # spasi ganda -> satu spasi
    )

# Genre kadang berisi beberapa nilai dipisah koma, rapikan spasinya
df["genre"] = df["genre"].str.replace(r"\s*,\s*", ", ", regex=True)

# Ganti string kosong / placeholder menjadi NaN
df[text_cols] = df[text_cols].replace(
    {"": pd.NA, "nan": pd.NA, "NaN": pd.NA, "None": pd.NA, "N/A": pd.NA}
)

# =========================================================
# 5. PASTIKAN TIPE DATA BENAR
# =========================================================
int_cols = ["duration_ms", "year", "popularity", "key", "mode"]
float_cols = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo",
]

for col in int_cols + float_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")  # nilai aneh -> NaN

# Kolom explicit -> boolean
if df["explicit"].dtype == object or df["explicit"].dtype == "string":
    df["explicit"] = (
        df["explicit"].astype(str).str.strip().str.lower()
        .map({"true": True, "false": False, "1": True, "0": False})
    )
df["explicit"] = df["explicit"].astype("boolean")

# =========================================================
# 6. VALIDASI RENTANG NILAI (nilai tidak valid -> NaN)
# =========================================================
# Fitur audio Spotify yang berskala 0-1
zero_one_cols = [
    "danceability", "energy", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence",
]
for col in zero_one_cols:
    df.loc[~df[col].between(0, 1), col] = np.nan

df.loc[~df["popularity"].between(0, 100), "popularity"] = np.nan
df.loc[~df["key"].between(0, 11), "key"] = np.nan          # key: 0-11 (C sampai B)
df.loc[~df["mode"].isin([0, 1]), "mode"] = np.nan          # 0 = minor, 1 = major
df.loc[df["duration_ms"] <= 0, "duration_ms"] = np.nan
df.loc[df["tempo"] <= 0, "tempo"] = np.nan                 # tempo 0 = tidak terdeteksi
df.loc[df["loudness"] > 0, "loudness"] = np.nan            # loudness (dB) umumnya negatif

# Tahun: batasi ke rentang yang masuk akal
df.loc[~df["year"].between(1900, 2026), "year"] = np.nan

# =========================================================
# 7. HAPUS DUPLIKAT
# =========================================================
before = len(df)
df = df.drop_duplicates()                                  # duplikat persis
df = df.drop_duplicates(subset=["artist", "song"], keep="first")  # lagu yang sama
print(f"\nDuplikat dihapus: {before - len(df)} baris")

# =========================================================
# 8. TANGANI MISSING VALUE
# =========================================================
# a) Baris tanpa identitas lagu tidak berguna -> hapus
df = df.dropna(subset=["artist", "song"])

# b) Kolom numerik -> isi dengan median (tahan terhadap outlier)
num_cols = [c for c in int_cols + float_cols if c not in ("year",)]
for col in num_cols:
    df[col] = df[col].fillna(df[col].median())

# c) Year & genre tidak bisa ditebak dengan wajar -> hapus / beri label
df = df.dropna(subset=["year"])
df["genre"] = df["genre"].fillna("Unknown")

# =========================================================
# 9. DETEKSI OUTLIER (IQR) - hanya diberi flag, tidak dihapus
# =========================================================
def iqr_bounds(s, k=1.5):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr

for col in ["duration_ms", "tempo", "loudness"]:
    lo, hi = iqr_bounds(df[col])
    n_out = ((df[col] < lo) | (df[col] > hi)).sum()
    print(f"Outlier {col}: {n_out} baris (batas {lo:.2f} s/d {hi:.2f})")

# =========================================================
# 10. FEATURE TAMBAHAN
# =========================================================
df["duration_min"] = (df["duration_ms"] / 60000).round(2)
df["main_genre"] = df["genre"].str.split(",").str[0].str.strip()
df["mode_label"] = np.where(df["mode"] == 1, "Major", "Minor")

# =========================================================
# 11. FINALISASI TIPE DATA & SIMPAN
# =========================================================
df[["duration_ms", "year", "popularity", "key", "mode"]] = (
    df[["duration_ms", "year", "popularity", "key", "mode"]].astype(int)
)
df = df.reset_index(drop=True)

print("\nShape akhir:", df.shape)
print("Sisa missing value:\n", df.isnull().sum())

df.to_csv("clean_dataset.csv", index=False, encoding="utf-8")
print("\nData bersih disimpan ke clean_dataset.csv")