import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- 1. ページの設定 ---
st.set_page_config(
    page_title="九州気温 3D Visualizer",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 九州主要都市の気温 3Dカラムマップ")
st.markdown("Open-Meteo APIから取得した現在の気温を、柱の高さと色で可視化しています。")

# 九州7県の県庁所在地データ
kyushu_capitals = {
    'Fukuoka':    {'lat': 33.5904, 'lon': 130.4017},
    'Saga':       {'lat': 33.2494, 'lon': 130.2974},
    'Nagasaki':   {'lat': 32.7450, 'lon': 129.8739},
    'Kumamoto':   {'lat': 32.7900, 'lon': 130.7420},
    'Oita':       {'lat': 33.2381, 'lon': 131.6119},
    'Miyazaki':   {'lat': 31.9110, 'lon': 131.4240},
    'Kagoshima':  {'lat': 31.5600, 'lon': 130.5580}
}

# --- 2. データ取得関数（キャッシュ機能付き） ---
@st.cache_data(ttl=600)  # 10分間データを保持
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
            
            temp = data['current']['temperature_2m']
            weather_info.append({
                'City': city,
                'lat': coords['lat'],
                'lon': coords['lon'],
                'Temperature': temp
            })
        except Exception as e:
            st.error(f"{city}のデータ取得に失敗しました: {e}")
            
    return pd.DataFrame(weather_info)

# --- 3. ロジック実行 ---
with st.spinner('最新の気象データを取得中...'):
    df = fetch_weather_data()

# --- 4. 可視化用の計算 ---
# 柱の高さ（気温1度につき 3,000メートル）
df['elevation'] = df['Temperature'] * 3000

# 気温に応じた色の計算関数
def get_color(t):
    # 低温（5度以下）で青、高温（35度以上）で赤になるように正規化
    r = int(min(255, max(0, (t - 5) * 8.5)))  
    b = int(min(255, max(0, (35 - t) * 8.5)))
    g = 50  # 緑は控えめに
    return [r, g, b, 200]  # RGBA形式

df['color'] = df['Temperature'].apply(get_color)

# --- 5. メイン画面のレイアウト ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 現在の気温データ")
    # 表を見やすく整形
    display_df = df[['City', 'Temperature']].copy()
    display_df.columns = ['都市名', '気温 (°C)']
    st.dataframe(display_df.set_index('都市名'), use_container_width=True)
    
    if st.button('🔄 データを更新'):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.subheader("📍 3D マップビュー")
    
    # Pydeckによる3D地図の設定
    view_state = pdk.ViewState(
        latitude=32.7,
        longitude=131.0,
        zoom=6.0,
        pitch=50,   # 傾き
        bearing=-10 # 回転
    )

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        radius=12000,           # 柱の太さ（メートル）
        get_fill_color='color', # 計算した色を適用
        pickable=True,
        auto_highlight=True,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10", # ダークモードで見やすく
        tooltip={
            "html": "<b>{City}</b><br>気温: {Temperature} °C",
            "style": {"color": "white", "backgroundColor": "#2c3e50"}
        }
    ))

# --- 6. 補足情報 ---
st.divider()
st.caption("Data source: Open-Meteo.com (Free Weather API)")
