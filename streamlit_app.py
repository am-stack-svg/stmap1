import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- ページ設定 ---
st.set_page_config(page_title="全国気温 3D Map", layout="wide")
st.title("全国主要都市の気温 3Dカラムマップ（時間変化対応）")

# --- 全国主要都市（例） ---
japan_cities = {
    'Sapporo':  {'lat': 43.0642, 'lon': 141.3469},
    'Sendai':   {'lat': 38.2682, 'lon': 140.8694},
    'Tokyo':    {'lat': 35.6895, 'lon': 139.6917},
    'Nagoya':   {'lat': 35.1815, 'lon': 136.9066},
    'Osaka':    {'lat': 34.6937, 'lon': 135.5023},
    'Hiroshima':{'lat': 34.3853, 'lon': 132.4553},
    'Fukuoka':  {'lat': 33.5904, 'lon': 130.4017},
    'Kagoshima':{'lat': 31.5600, 'lon': 130.5580},
    'Naha':     {'lat': 26.2124, 'lon': 127.6809},
}

# --- 気温 → 色変換 ---
def temp_to_color(temp):
    t = max(min(temp, 35), 0)  # 0〜35℃に制限
    r = int(255 * (t / 35))
    b = int(255 * (1 - t / 35))
    return [r, 80, b, 200]

# --- データ取得 ---
@st.cache_data(ttl=600)
def fetch_weather_data(hour):
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    records = []

    for city, coords in japan_cities.items():
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "hourly": "temperature_2m",
            "timezone": "Asia/Tokyo"
        }
        try:
            r = requests.get(BASE_URL, params=params)
            r.raise_for_status()
            data = r.json()
            temp = data["hourly"]["temperature_2m"][hour]

            records.append({
                "City": city,
                "lat": coords["lat"],
                "lon": coords["lon"],
                "Temperature": temp,
                "elevation": temp * 3000,
                "color": temp_to_color(temp)
            })

        except Exception as e:
            st.error(f"{city} の取得エラー: {e}")

    return pd.DataFrame(records)

# --- UI ---
hour = st.slider("時刻（0〜23時）", 0, 23, 12)

with st.spinner("最新データ取得中..."):
    df = fetch_weather_data(hour)

# --- レイアウト ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("気温データ")
    st.dataframe(df[["City", "Temperature"]], use_container_width=True)

    if st.button("データ更新"):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.subheader("3D 気温カラムマップ")

    view_state = pdk.ViewState(
        latitude=36.0,
        longitude=138.0,
        zoom=4.5,
        pitch=45,
        bearing=0
    )

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        radius=20000,
        get_fill_color='color',
        pickable=True,
        auto_highlight=True
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v11",
        tooltip={
            "html": "<b>{City}</b><br>気温: {Temperature}℃",
            "style": {"color": "white"}
        }
    )

    st.pydeck_chart(deck)
