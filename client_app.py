import streamlit as st
import pandas as pd
import os

# 設定網頁標題
st.set_page_config(page_title="產品電子手冊", layout="wide")

# 讀取資料
def load_data():
    if os.path.exists('products.xlsx'):
        return pd.read_excel('products.xlsx')
    return None

df = load_data()

# 獲取網址參數 (最新的 Streamlit 語法)
shop_param = st.query_params.get("shop", "")
id_param = st.query_params.get("id", "")

# 顯示診斷資訊 (這段是為了幫你抓出為什麼對不上的原因)
if not id_param:
    st.title("💡 歡迎使用產品手冊系統")
    st.info("請掃描產品包裝上的二維碼查看詳情")
else:
    if df is not None:
        # 這裡會幫你自動去掉 Excel 裡的空格，防止對不上
        df['產品編號'] = df['產品編號'].astype(str).str.strip()
        
        # 搜尋資料
        product_row = df[df['產品編號'] == str(id_param).strip()]
        
        if not product_row.empty:
            row = product_row.iloc[0]
            st.header(f"🏪 {shop_param}")
            st.title(row['產品名稱'])
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if pd.notna(row['圖片路徑']) and os.path.exists(row['圖片路徑']):
                    st.image(row['圖片路徑'], use_container_width=True)
                else:
                    st.warning("暫無產品圖片")
            
            with col2:
                st.subheader("📋 產品簡介")
                st.write(row['簡介'])
                st.subheader("🍴 食用方法")
                st.write(row['食用方法'])
                st.subheader("⚠️ 注意事項")
                st.write(row['注意事項'])
        else:
            # 如果找不到編號，會顯示這段幫助我們排查
            st.error(f"找不到產品編號：{id_param}")
            st.write("目前 Excel 裡的編號有：", df['產品編號'].tolist())
            st.info("請檢查 Excel 裡的編號是否與 QR Code 產生的編號一致。")
    else:
        st.error("找不到資料庫檔案 (products.xlsx)，請確保檔案已上傳至 GitHub。")