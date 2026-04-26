import streamlit as st
import os

# 藥房名稱列表（可依需求擴充）
PHARMACY_OPTIONS = ["A連鎖", "B連鎖", "C藥房", "其他"]

def get_or_make_pharmacy_dir(pharmacy_name):
    # 清理藥房名稱，僅允許中英文數字與下劃線
    safe_name = "".join([c if (c.isalnum() or c in ('_', '-')) else '_' for c in pharmacy_name.strip()])
    path = os.path.join("images", safe_name)
    os.makedirs(path, exist_ok=True)
    return path, safe_name
import pandas as pd
import os
import qrcode
from io import BytesIO

# 設定圖片與數據存儲資料夾與路徑
IMAGES_DIR = "./images"
DATA_FILE = "products.xlsx"
CLIENT_APP_URL = "https://your-app.streamlit.app/?id="

os.makedirs(IMAGES_DIR, exist_ok=True)

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_excel(DATA_FILE, dtype=str)
    else:
        cols = ["id", "name", "intro", "suitable_for", "usage", "notes", "image"]
        return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

def save_image(uploaded_file, product_id):
    extension = os.path.splitext(uploaded_file.name)[1].lower()
    image_path = os.path.join(IMAGES_DIR, f"{product_id}{extension}")
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # 返回相對路徑給前端使用
    return image_path

def generate_qr_code(url):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

st.title("產品管理後台工具")

with st.form("upload_form", clear_on_submit=False):
    st.header("產品上傳/更新")
    col1, col2 = st.columns(2)
    with col1:
        product_id = st.text_input("產品ID（如 NMN001，唯一識別）", max_chars=32).strip()
        product_name = st.text_input("產品名稱", max_chars=128)
        intro = st.text_area("核心簡介", height=80)
    with col2:
        suitable_for = st.text_input("適用人群", max_chars=128)
        usage = st.text_input("食用方法", max_chars=128)
        notes = st.text_area("注意事項", height=60)
        image_file = st.file_uploader("產品圖片上傳（jpg/png）", type=['jpg', 'jpeg', 'png'])
    submitted = st.form_submit_button("提交/更新產品")

save_success = False
qr_img_buf = None
qr_target_url = None

if submitted:
    if not product_id:
        st.warning("產品ID不能為空")
    else:
        # 載入現有數據
        df = load_data()
        # 處理圖片
        image_path = None
        if image_file is not None:
            extension = os.path.splitext(image_file.name)[1].lower()
            image_path = os.path.join(IMAGES_DIR, f"{product_id}{extension}")
            save_image(image_file, product_id)
        else:
            # 若已有舊圖則保留舊圖
            exist_row = df[df["id"] == product_id]
            if not exist_row.empty:
                image_path = exist_row.iloc[0]["image"]
        # 文字、圖片欄位組裝
        new_row = {
            "id": product_id,
            "name": product_name,
            "intro": intro,
            "suitable_for": suitable_for,
            "usage": usage,
            "notes": notes,
            "image": image_path or "",
        }
        # 若ID已存在，覆蓋更新
        df = df[df["id"] != product_id]
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        save_success = True

        st.success(f"產品【{product_id}】已保存")
        # 顯示產品圖片
        if image_path and os.path.exists(image_path):
            st.image(image_path, caption="產品圖片", use_column_width=True)
        # 產生並展示 QRCode
        qr_target_url = f"{CLIENT_APP_URL}{product_id}"
        qr_img_buf = generate_qr_code(qr_target_url)
        st.markdown("#### 客戶網頁二維碼")
        st.image(qr_img_buf, use_column_width=False, caption=qr_target_url)
        st.download_button(
            "下載二維碼圖片",
            data=qr_img_buf,
            file_name=f"{product_id}_qrcode.png",
            mime="image/png"
        )

st.divider()
st.header("產品列表")

df = load_data()
if df.empty:
    st.info("目前尚無產品")
else:
    # 展示一個可操作表格與刪除按鈕
    def display_table():
        display_df = df.copy()
        display_df = display_df.drop(columns=["image"])
        st.dataframe(display_df, hide_index=True, use_container_width=True)

    display_table()

    with st.expander("刪除產品", expanded=False):
        delete_id = st.text_input("輸入要刪除的產品ID")
        if st.button("刪除", type="primary"):
            if delete_id and delete_id in df["id"].values:
                # 刪資料 & 圖片
                row = df[df["id"] == delete_id]
                img_path = row.iloc[0]["image"]
                df = df[df["id"] != delete_id]
                save_data(df)
                if img_path and os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                    except Exception:
                        pass
                st.success(f"已刪除產品【{delete_id}】")
                # 重新顯示表格
                display_table()
            else:
                st.warning("找不到此產品ID")