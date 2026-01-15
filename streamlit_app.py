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
