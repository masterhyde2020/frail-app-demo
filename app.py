import streamlit as st
import os.path
import json
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from datetime import datetime

# デザイン設定
st.set_page_config(page_title="フレイル予防アプリ", page_icon="💪", layout="centered")

# カスタムCSSでスマホアプリ風に見せる
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #4CAF50; color: white; border: none; font-weight: bold; }
    .metric-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_gdrive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

# サイドバー（ナビゲーション）をアプリのメニュー風にする
with st.sidebar:
    st.title("📱 メニュー")
    page = st.radio("移動先", ["マイページ", "フレイル測定", "履歴を確認", "フレンド設定"])
    if st.button("ログアウト"):
        if os.path.exists('token.json'): os.remove('token.json')
        st.rerun()

# メイン処理
if not os.path.exists('token.json'):
    st.title("フレイル予防アプリ")
    st.write("健康な未来のために、データを自分の手で管理しましょう。")
    if st.button("Google IDでログインしてはじめる"):
        get_gdrive_service()
        st.rerun()
else:
    service = get_gdrive_service()

    if page == "マイページ":
        st.title("こんにちは！")
        st.markdown(f"""
            <div class="metric-card">
                <h3>現在の健康状態</h3>
                <p style='font-size: 24px; color: #4CAF50;'><b>良好です</b></p>
                <p>前回の測定日: 2026年1月10日</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("今すぐ測定する"):
            st.info("測定ページへ移動してください（左メニューから「フレイル測定」を選択）")

    elif page == "フレイル測定":
        st.title("測定を開始します")
        st.write("スマホを持って、その場で30秒間足踏みしてください。")
        
        # 測定の演出
        if st.button("測定開始（30秒）"):
            with st.spinner('測定中...'):
                time.sleep(3) # デモ用に短縮
            score = 75 # デモ用固定値
            st.success(f"測定完了！ あなたのスコアは {score}点 です。")
            
            if st.button("この結果をGoogleドライブに保存"):
                with st.spinner('保存中...'):
                    data = {"date": datetime.now().isoformat(), "score": score}
                    file_metadata = {'name': f'frail_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json','mimeType': 'application/json'}
                    media = MediaInMemoryUpload(json.dumps(data).encode('utf-8'), mimetype='application/json')
                    service.files().create(body=file_metadata, media_body=media).execute()
                st.balloons()
                st.success("個人のGoogleドライブに原本データを保管しました。")

    elif page == "履歴を確認":
        st.title("過去の記録")
        results = service.files().list(q="name contains 'frail_'", fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if not items:
            st.write("まだ記録がありません。")
        for item in items:
            st.markdown(f"""
                <div class="metric-card">
                    <b>測定日: {item['name'].replace('frail_', '').replace('.json', '')}</b><br>
                    状態: 保存済み（Google Drive ID: {item['id'][:10]}...）
                </div>
            """, unsafe_allow_html=True)

    elif page == "フレンド設定":
        st.title("自治体・親族連携")
        st.write("データを共有する相手を選んでください。")
        st.toggle("〇〇市 健康増進課（実名提供）", value=True)
        st.toggle("長男 太郎さん（実名提供）", value=False)
        st.toggle("開発会社（匿名提供）", value=True)
        st.button("設定を保存")