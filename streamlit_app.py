import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime, timezone, timedelta

# ==================================================
# ページ設定
# ==================================================
st.set_page_config(page_title="日本気温 3D Map", layout="wide")
st.title("🌡️ 日本主要都市の現在の気温 3Dカラムマップ")

# ==================================================
# 改善① 観測地点を全国に拡張（切替）
# ==================================================
show_all = st.checkbox("全国主要都市を表示する", value=False)

# 九州7県
kyushu_capitals = {
    'Fukuoka':    {'lat': 33.5904, 'lon': 130.4017},
    'Saga':       {'lat': 33.2494, 'lon': 130.2974},
    'Nagasaki':   {'lat': 32.7450, 'lon': 129.8739},
    'Kumamoto':   {'lat': 32.7900, 'lon': 130.7420},
    'Oita':       {'lat': 33.2381, 'lon': 131.6119},
    'Miyazaki':   {'lat': 31.9110, 'lon': 131.4240},
    'Kagoshima':  {'lat': 31.5600, 'lon': 130.5580}
}

# 全国主要都市（例）
japan_cities = {
    'Sapporo':  {'lat': 43.0642, 'lon': 141.3469},
    'Tokyo':    {'lat': 35.6895, 'lon': 139.6917},
    'Nagoya':   {'lat': 35.1815, 'lon': 136.9066},
    'Osaka':    {'lat': 34.6937, 'lon': 135.5023},
    'Hiroshima':{'lat': 34.3853, 'lon': 132.4553},
    'Fukuoka':  {'lat': 33.5904, 'lon': 130.4017},
    'Naha':     {'lat': 26.2124, 'lon': 127.6809}
}

cities = japan_cities if show_all else kyushu_capitals

# ==================================================
# 改善② キャッシュ問題を回避（citiesを引数に）
# 改善④ 疑似アニメーション（5分更新）
# ==================================================
@st.cache_data(ttl=300)
def fetch_weather_data(cities):
    weather_info = []
    BASE_URL = 'https://api.open-meteo.com/v1/forecast'

    for city, coords in cities.items():
        params = {
            'latitude': coords['lat'],
            'longitude': coords['lon'],
            'current': 'temperature_2m'
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        weather_info.append({
            'City': city,
            'lat': coords['lat'],
            'lon': coords['lon'],
            'Temperature': data['current']['temperature_2m']
        })

    return pd.DataFrame(weather_info)

# ==================================================
# データ取得
# ==================================================
with st.spinner("最新の気温データを取得中..."):
    df = fetch_weather_data(cities)

# ==================================================
# 改善③ 色合いを明るく（気温別）
# ※ Pydeckで確実に反映される「RGBA配列」
# ==================================================
def temp_color(t):
    if t < 10:
        return [0, 120, 255, 180]     # 青（寒い）
    elif t < 20:
        return [255, 200, 0, 180]     # 黄（涼しい）
    else:
        return [255, 80, 80, 180]     # 赤（暑い）

df['color'] = df['Temperature'].apply(temp_color)

# 3Dカラムの高さ
df['elevation'] = df['Temperature'] * 3000

# ==================================================
# 改善⑤ 計測時刻を表示（JST）
# ==================================================
now_jst = datetime.now(timezone.utc) + timedelta(hours=9)

# ==================================================
# レイアウト
# ==================================================
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("取得したデータ")
    st.write(f"🕒 計測時刻（JST）：{now_jst.strftime('%Y-%m-%d %H:%M:%S')}")
    st.dataframe(df[['City', 'Temperature']], use_container_width=True)

    if st.button("データを更新"):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.subheader("3D カラムマップ")

    view_state = pdk.ViewState(
        latitude=34,
        longitude=135,
        zoom=4.5 if show_all else 6.2,
        pitch=45
    )

    # ★重要：get_fill_color='@color'
    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        get_fill_color='@color',   # ← 色分けが効く決定打
        radius=12000,
        pickable=True,
        auto_highlight=True,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{City}</b><br>気温: {Temperature}℃",
            "style": {"color": "white"}
        }
    ))

st.caption("データ取得元：Open-Meteo（APIキー不要）")
