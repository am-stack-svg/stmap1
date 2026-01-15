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
def fetch_weather_d
