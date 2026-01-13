import streamlit as st
import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from datetime import datetime

# アプリのURL（あなたのURLに書き換え済み）
REDIRECT_URI = "https://frail-app-demo-gjy9srwec5ajdfhytfjxct.streamlit.app/"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

st.set_page_config(page_title="フレイル予防・自治体連携", layout="wide")

def get_gdrive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, redirect_uri=REDIRECT_URI)
            # Web上ではURLを発行してユーザーに踏んでもらう方式にする
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.link_button("Googleアカウントで認証する", auth_url)
            st.stop()
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

# サイドバーで「住民モード」と「自治体モード」を切り替え
st.sidebar.title("デモ切替")
mode = st.sidebar.radio("表示モード", ["一般ユーザー画面", "自治体管理者画面"])

if mode == "一般ユーザー画面":
    st.title("💪 フレイル予防アプリ")
    if st.button("Googleドライブと連携開始"):
        service = get_gdrive_service()
        st.success("連携完了！")
    
    if os.path.exists('token.json'):
        score = st.slider("本日の歩行測定結果", 0, 100, 75)
        if st.button("測定データを保存"):
            service = get_gdrive_service()
            data = {"date": datetime.now().isoformat(), "score": score, "user": "nagata"}
            media = MediaInMemoryUpload(json.dumps(data).encode('utf-8'), mimetype='application/json')
            file_metadata = {'name': f'frail_{datetime.now().strftime("%Y%m%d")}.json'}
            service.files().create(body=file_metadata, media_body=media).execute()
            st.balloons()
            st.success("個人のGoogleドライブに保存しました。")

else:
    st.title("🏛️ 自治体データ一括収集パネル")
    st.info("この画面は自治体の担当者のみがアクセスします。")
    
    if st.button("全住民のドライブから最新データを収集"):
        with st.spinner("各住民の原本データにアクセス中..."):
            # デモ用に現在のユーザーのデータを「住民一覧」として表示
            if os.path.exists('token.json'):
                service = get_gdrive_service()
                results = service.files().list(q="name contains 'frail_'", fields="files(name)").execute()
                items = results.get('files', [])
                
                st.write(f"集計対象： 120名（うち本日更新 {len(items)} 名）")
                st.bar_chart([75, 80, 60, 90, 85]) # デモ用のダミーグラフ
                st.table([{"住民ID": "ID_001", "状態": "良好", "最終更新": "2026/01/13"}] * 5)
            else:
                st.warning("まずユーザー画面でログインしてください。")