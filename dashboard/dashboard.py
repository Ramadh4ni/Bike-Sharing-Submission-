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

df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
df_day['dteday'] = pd.to_datetime(df_day['dteday'])


# CLEANING (IQR METHOD)
Q1 = df_hour['cnt'].quantile(0.25)
Q3 = df_hour['cnt'].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

df_hour = df_hour[
    (df_hour['cnt'] >= lower) &
    (df_hour['cnt'] <= upper)
]

# HEADER
st.title("🚲 Bike Sharing Dashboard")
st.markdown("Analisis penyewaan sepeda berdasarkan **cuaca dan waktu**")

st.markdown("---")

# SIDEBAR
menu = st.sidebar.radio(
    "📌 Pilih Analisis",
    ["Overview", "Pengaruh Cuaca", "Peak Hour Summer"]
)

# OVERVIEW
if menu == "Overview":
    st.subheader("📊 Overview Dataset")

    col1, col2 = st.columns(2)

    col1.metric("Total Data Hour", df_hour.shape[0])
    col2.metric("Total Data Day", df_day.shape[0])

    st.markdown("---")

    st.write("Preview Data")
    st.dataframe(df_day.head())

# PERTANYAAN 1
elif menu == "Pengaruh Cuaca":

    st.subheader("🌦️ Pengaruh Cuaca terhadap Penyewaan")

    df_q1 = df_day[
        (df_day['workingday'] == 1) &
        (df_day['yr'] == 1)
    ]

    weather_avg = df_q1.groupby('weathersit')['cnt'].mean()

    weather_labels = {
        1: "Clear",
        2: "Mist/Cloudy",
        3: "Light Rain/Snow"
    }

    labels = [weather_labels[i] for i in weather_avg.index]
    values = weather_avg.values

    col1, col2 = st.columns([2,1])

    fig, ax = plt.subplots()
    ax.bar(labels, values)

    for i, v in enumerate(values):
        ax.text(i, v + 50, f"{v:.0f}", ha='center')

    ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Cuaca")
    ax.set_ylabel("Rata-rata Penyewaan")

    col1.pyplot(fig)

    clear = weather_avg[1]
    bad = weather_avg[3]
    drop = ((clear - bad) / clear) * 100

    col2.metric("📉 Penurunan", f"{drop:.2f}%")

    st.markdown("---")

    st.success(
        f"Terjadi penurunan sebesar {drop:.2f}% dari cuaca cerah ke cuaca buruk, "
        "menunjukkan bahwa cuaca sangat memengaruhi penggunaan sepeda."
    )

# PERTANYAAN 2 
elif menu == "Peak Hour Summer":

    st.subheader("⏰ Peak Hour (Summer 2012 - Working Day)")

    df_q2 = df_hour[
        (df_hour['workingday'] == 1) &
        (df_hour['yr'] == 1) &
        (df_hour['season'] == 2)
    ]

    hourly_avg = df_q2.groupby('hr')['cnt'].mean()

    peak_hour = hourly_avg.idxmax()
    peak_value = hourly_avg.max()

    col1, col2 = st.columns([2,1])

    fig, ax = plt.subplots(figsize=(9,5))

    ax.plot(hourly_avg.index, hourly_avg.values, marker='o')

    ax.scatter(peak_hour, peak_value)

    ax.annotate(
        f'Peak: {peak_hour}:00\n({peak_value:.0f})',
        xy=(peak_hour, peak_value),
        xytext=(peak_hour, peak_value + 80),
        ha='center',
        arrowprops=dict(arrowstyle='->')
    )

    ax.set_xlabel("Jam")
    ax.set_ylabel("Rata-rata Penyewaan")
    ax.set_title("Pola Penyewaan Sepeda per Jam (Summer 2012 - Working Day)")

    col1.pyplot(fig)

    col2.metric("⏰ Peak Hour", f"{peak_hour}:00")
    col2.metric("📊 Avg Rental", f"{peak_value:.0f}")

    st.markdown("---")

    st.success(
        f"Pada musim panas 2012, puncak penyewaan terjadi pada pukul {peak_hour}:00 "
        f"dengan rata-rata sekitar {peak_value:.0f} penyewaan."
    )
