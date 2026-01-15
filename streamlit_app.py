import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- ページ設定 ---
st.set_page_config(page_title="九州気温 3D Map", layout="wide")
st.title("九州主要都市の現在の気温 3Dカラムマップ")

# 九州7県のデータ
kyushu_capitals = {
    'Fukuoka':    {'lat': 33.5904, 'lon': 130.4017},
    'Saga':       {'lat': 33.2494, 'lon': 130.2974},
    'Nagasaki':   {'lat': 32.7450, 'lon': 129.8739},
    'Kumamoto':   {'lat': 32.7900, 'lon': 130.7420},
    'Oita':       {'lat': 33.2381, 'lon': 131.6119},
    'Miyazaki':   {'lat': 31.9110, 'lon': 131.4240},
    'Kagoshima':  {'lat': 31.5600, 'lon': 130.5580}
}

# --- データ取得関数 ---
@st.cache_data(ttl=600)
def fetch_weather_data():
    weather_info = []
    BASE_URL = 'https://api.open-meteo.com/v1/forecast'
    
    for city, coords in kyushu_capitals.items():
        params = {
            'latitude':  coords['lat'],
            'longitude': coords['lon'],
            'current': 'temperature_2m'
        }
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            weather_info.append({
                'City': city,
                'lat': coords['lat'],
                'lon': coords['lon'],
                'Temperature': data['current']['temperature_2m'],
                'Time': data['current']['time']   # ← 追加
            })

        except Exception as e:
            st.error(f"Error fetching {city}: {e}")
            
    return pd.DataFrame(weather_info)

# データの取得
with st.spinner('最新の気温データを取得中...'):
    df = fetch_weather_data()

# 気温を高さ（メートル）に変換（例：1度 = 3000m）
df['elevation'] = df['Temperature'] * scale

# データ取得
with st.spinner('最新の気温データを取得中...'):
    df = fetch_weather_data()

# --- メインレイアウト ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("取得したデータ")

    scale = st.slider(
        "カラム高さ倍率（1℃あたり）",
        min_value=1000,
        max_value=5000,
        step=500,
        value=3000
    )

    st.dataframe(df[['City', 'Temperature', 'Time']], use_container_width=True)

    if st.button('データを更新'):
        st.cache_data.clear()
        st.rerun()

# 👇 ここで初めて計算する
df['elevation'] = df['Temperature'] * scale

df['color'] = df['Temperature'].apply(
    lambda t: [100, min(255, int(100 + t * 5)), 255, 180]
)


# --- メインレイアウト ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("取得したデータ")

    scale = st.slider(
        "カラム高さ倍率（1℃あたり）",
        min_value=1000,
        max_value=5000,
        step=500,
        value=3000
    )

    st.dataframe(df[['City', 'Temperature']], use_container_width=True)

    
    if st.button('データを更新'):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.subheader("3D カラムマップ")

    # Pydeck の設定
    view_state = pdk.ViewState(
        latitude=32.7,
        longitude=131.0,
        zoom=6.2,
        pitch=45,  # 地図を傾ける
        bearing=0
    )
    layer = pdk.Layer(
    "ColumnLayer",
    data=df,
    get_position='[lon, lat]',
    get_elevation='elevation',
    radius=12000,
    get_fill_color='color',   # ← 追加した列を使用
    pickable=True,
    auto_highlight=True,
)


    

    # 描画
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{City}</b><br>気温: {Temperature}°C",
            "style": {"color": "white"}
        }
    ))
