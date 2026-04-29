import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# CONFIG
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    layout="wide"
)

 
# LOAD DATA
base_path = os.path.dirname(__file__)

df_hour = pd.read_csv(os.path.join(base_path, "hour.csv"))
df_day = pd.read_csv(os.path.join(base_path, "day.csv"))

 
# CLEANING
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
df_day['dteday'] = pd.to_datetime(df_day['dteday'])

# rename
rename_dict = {
    'yr': 'year',
    'mnth': 'month',
    'hr': 'hour',
    'cnt': 'total_rentals'
}

df_hour.rename(columns=rename_dict, inplace=True)
df_day.rename(columns=rename_dict, inplace=True)

# mapping
year_map = {0: 2011, 1: 2012}

season_map = {
    1: 'Spring',
    2: 'Summer',
    3: 'Fall',
    4: 'Winter'
}

weather_map = {
    1: 'Clear / Partly Cloudy',
    2: 'Mist / Cloudy',
    3: 'Light Rain / Snow',
    4: 'Heavy Rain / Snow'
}

for df in [df_hour, df_day]:
    df['year'] = df['year'].map(year_map)
    df['season'] = df['season'].map(season_map)
    df['weathersit'] = df['weathersit'].map(weather_map)

# outlier remove
Q1 = df_hour['total_rentals'].quantile(0.25)
Q3 = df_hour['total_rentals'].quantile(0.75)
IQR = Q3 - Q1

df_hour = df_hour[
    (df_hour['total_rentals'] >= Q1 - 1.5 * IQR) &
    (df_hour['total_rentals'] <= Q3 + 1.5 * IQR)
]

 
# sidebar filter
st.sidebar.subheader("🔍 Filter Data")

start_date = st.sidebar.date_input(
    "Tanggal Mulai",
    df_day['dteday'].min()
)

end_date = st.sidebar.date_input(
    "Tanggal Akhir",
    df_day['dteday'].max()
)

season_filter = st.sidebar.multiselect(
    "Pilih Season",
    options=df_day['season'].unique(),
    default=df_day['season'].unique()
)

# apply filter
df_day_filtered = df_day[
    (df_day['dteday'] >= pd.to_datetime(start_date)) &
    (df_day['dteday'] <= pd.to_datetime(end_date)) &
    (df_day['season'].isin(season_filter))
]

df_hour_filtered = df_hour[
    (df_hour['dteday'] >= pd.to_datetime(start_date)) &
    (df_hour['dteday'] <= pd.to_datetime(end_date)) &
    (df_hour['season'].isin(season_filter))
]

 
# HEADER
st.title("🚲 Bike Sharing Dashboard")
st.markdown("Analisis penyewaan sepeda berdasarkan **cuaca dan waktu**")

st.info("Gunakan filter di sidebar untuk mengeksplorasi data.")

st.markdown("---")

 
# MENU
menu = st.sidebar.radio(
    "📌 Pilih Analisis",
    ["Overview", "Pengaruh Cuaca", "Peak Hour Summer"]
)

 
# OVERVIEW
if menu == "Overview":
    st.subheader("📊 Overview Dataset (Filtered)")

    col1, col2 = st.columns(2)

    col1.metric("Total Data Hour", df_hour_filtered.shape[0])
    col2.metric("Total Data Day", df_day_filtered.shape[0])

    st.markdown("---")

    st.write("### 📅 Data Harian (Day Dataset)")
    st.dataframe(df_day_filtered.head(10))

    st.write("### ⏰ Data Per Jam (Hour Dataset)")
    st.dataframe(df_hour_filtered.head(10))

    st.markdown("### 📈 Rata-rata Penyewaan (Filtered)")

    avg_day = df_day_filtered['total_rentals'].mean()
    avg_hour = df_hour_filtered['total_rentals'].mean()

    col1, col2 = st.columns(2)
    col1.metric("Avg Day Rentals", f"{avg_day:.0f}")
    col2.metric("Avg Hour Rentals", f"{avg_hour:.0f}")

 
# PERTANYAAN 1
elif menu == "Pengaruh Cuaca":

    st.subheader("🌦️ Pengaruh Cuaca terhadap Penyewaan")

    df_q1 = df_day_filtered[
        (df_day_filtered['workingday'] == 1) &
        (df_day_filtered['year'] == 2012)
    ]

    weather_avg = df_q1.groupby('weathersit')['total_rentals'].mean().reset_index()

    col1, col2 = st.columns([2,1])

    fig, ax = plt.subplots()

    bars = ax.bar(
        weather_avg['weathersit'],
        weather_avg['total_rentals']
    )

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 50, f"{yval:.0f}", ha='center')

    ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Cuaca")
    ax.set_ylabel("Rata-rata Penyewaan")

    col1.pyplot(fig)

    try:
        clear = weather_avg.loc[
            weather_avg['weathersit'] == 'Clear / Partly Cloudy',
            'total_rentals'
        ].values[0]

        bad = weather_avg.loc[
            weather_avg['weathersit'] == 'Light Rain / Snow',
            'total_rentals'
        ].values[0]

        drop = ((clear - bad) / clear) * 100

        col2.metric("📉 Penurunan", f"{drop:.2f}%")

        st.success(
            f"Terjadi penurunan sebesar {drop:.2f}% pada kondisi cuaca buruk."
        )

    except:
        col2.warning("Data tidak cukup untuk menghitung penurunan.")

 
# PERTANYAAN 2
elif menu == "Peak Hour Summer":

    st.subheader("⏰ Peak Hour (Summer 2012 - Working Day)")

    df_q2 = df_hour_filtered[
        (df_hour_filtered['workingday'] == 1) &
        (df_hour_filtered['year'] == 2012) &
        (df_hour_filtered['season'] == 'Summer')
    ]

    hourly_avg = df_q2.groupby('hour')['total_rentals'].mean().reset_index()

    col1, col2 = st.columns([2,1])

    fig, ax = plt.subplots(figsize=(9,5))

    if len(hourly_avg) > 0:
        peak_row = hourly_avg.loc[hourly_avg['total_rentals'].idxmax()]
        peak_hour = int(peak_row['hour'])
        peak_value = peak_row['total_rentals']

        ax.plot(hourly_avg['hour'], hourly_avg['total_rentals'], marker='o')
        ax.scatter(peak_hour, peak_value)

        ax.annotate(
            f'Peak: {peak_hour}:00\n({peak_value:.0f})',
            xy=(peak_hour, peak_value),
            xytext=(peak_hour, peak_value + 80),
            ha='center',
            arrowprops=dict(arrowstyle='->')
        )

        col2.metric("⏰ Peak Hour", f"{peak_hour}:00")
        col2.metric("📊 Avg Rental", f"{peak_value:.0f}")

        st.success(
            f"Puncak penyewaan terjadi pada pukul {peak_hour}:00 "
            f"dengan rata-rata {peak_value:.0f} penyewaan."
        )
    else:
        col2.warning("Data tidak tersedia untuk filter ini.")

    ax.set_xlabel("Jam")
    ax.set_ylabel("Rata-rata Penyewaan")
    ax.set_title("Pola Penyewaan Sepeda per Jam")

    col1.pyplot(fig)