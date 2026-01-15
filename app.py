import streamlit as st
import streamlit.components.v1 as components
import json
import os
import qrcode
from io import BytesIO
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from datetime import datetime

# --- 設定（ここはあなたの環境に合わせてあるわ） ---
SCOPES = ['https://www.googleapis.com/auth/drive.file']
REDIRECT_URI = "https://frail-app-demo-gjy9srwec5ajdfhytfjxct.streamlit.app/"

st.set_page_config(page_title="フレイル予防システム", layout="centered")

# --- QRコードを表示する関数（これを忘れてたでしょ？） ---
def show_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf, caption="スマホでスキャンして検証", width=200)

# --- 認証ロジック ---
def authenticate_google():
    if 'credentials' not in st.session_state:
        if "code" in st.query_params:
            flow = Flow.from_client_secrets_file(
                'credentials.json', scopes=SCOPES, redirect_uri=REDIRECT_URI)
            flow.fetch_token(code=st.query_params["code"])
            st.session_state.credentials = flow.credentials
            st.query_params.clear()
        else:
            # ログインしていない時にQRコードとボタンを出す
            st.info("スマートフォンで検証する場合は、以下のQRコードをスキャンしてね。")
            show_qr_code(REDIRECT_URI) # ここで呼び出してるわ
            
            flow = Flow.from_client_secrets_file(
                'credentials.json', scopes=SCOPES, redirect_uri=REDIRECT_URI)
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.link_button("Googleアカウントでログイン", auth_url)
            return None
    return st.session_state.credentials

# 実行
creds = authenticate_google()

if creds:
    st.success("✅ ログイン中")
    is_anonymous = st.toggle("匿名モード", value=False)
    
    # index.htmlの読み込み
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_code = f.read()
        components.html(html_code, height=650)
        
        if st.button("測定結果を最終送信"):
            st.write("保存中...")
            # ここにDrive保存ロジックが入るわ
            st.balloons()
    except Exception as e:
        st.error(f"エラーが発生したわ: {e}")