import streamlit as st
import pandas as pd
import qrcode
from PIL import Image
import os
import io
# --- 登入驗證 ---
if "admin_authed" not in st.session_state:
    st.session_state["admin_authed"] = False

if not st.session_state["admin_authed"]:
    with st.form("login_form", clear_on_submit=True):
        pwd = st.text_input("請輸入管理密碼", type="password")
        login_submit = st.form_submit_button("登入")
        if login_submit:
            if pwd == "a123456":
                st.session_state["admin_authed"] = True
            else:
                st.error("請輸入正確的管理密碼以繼續")
    # 阻止往下執行，直到驗證通過
    st.stop()

# --- 1. 初始化環境 ---
if not os.path.exists('images'):
    os.makedirs('images')
if not os.path.exists('products.xlsx'):
    df_init = pd.DataFrame(columns=['藥房名稱', '產品編號', '產品名稱', '簡介', '適用人群', '食用方法', '注意事項', '圖片路徑'])
    df_init.to_excel('products.xlsx', index=False)

st.set_page_config(page_title="產品管理與 QR 生成器", layout="wide")

# --- 2. 介面標題 ---
st.title("🛡️ 藥房專屬產品後台管理")
st.info("在這裡錄入產品資料，系統會自動生成專屬二維碼。")

# --- 3. 錄入表單 ---
with st.form("product_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        shop_name = st.selectbox("選擇藥房名稱", ["淳溢澤永連鎖藥房", "宏利藥房", "濟仁藥房", "民生藥房", "鼎泰藥房", "眾安藥房", "萬合藥房", "自家品牌"])
        prod_id = st.text_input("產品編號 (例如: NMN01)")
        prod_name = st.text_input("產品名稱")
        uploaded_file = st.file_uploader("上傳產品圖片", type=['jpg', 'png', 'jpeg'])

    with col2:
        brief = st.text_area("產品簡介")
        target = st.text_input("適用人群")
        usage = st.text_input("食用方法")
        notice = st.text_area("注意事項")

    submit_button = st.form_submit_button("儲存產品並生成 QR Code")

# --- 4. 處理邏輯 ---
if submit_button:
    if prod_id and prod_name:
        # A. 處理圖片儲存
        img_path = ""
        if uploaded_file:
            shop_dir = f"images/{shop_name}"
            if not os.path.exists(shop_dir):
                os.makedirs(shop_dir)
            img_path = f"{shop_dir}/{prod_id}.jpg"
            img = Image.open(uploaded_file)
            img = img.convert("RGB") # 統一轉為 RGB
            img.save(img_path)

        # B. 寫入 Excel
        new_data = {
            '藥房名稱': shop_name,
            '產品編號': prod_id,
            '產品名稱': prod_name,
            '簡介': brief,
            '適用人群': target,
            '食用方法': usage,
            '注意事項': notice,
            '圖片路徑': img_path
        }
        
        df = pd.read_excel('products.xlsx')
        # 如果 ID 已存在，先刪除舊的再新增 (更新邏輯)
        df = df[~((df['產品編號'] == prod_id) & (df['藥房名稱'] == shop_name))]
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel('products.xlsx', index=False)

        st.success(f"✅ {prod_name} 已成功儲存！")

        # C. 生成 QR Code
        # ⚠️ 這裡的網址請替換成你未來部署在 Streamlit Cloud 的網址
        base_url = "https://electronic-i9.streamlit.app/" 
        full_url = f"{base_url}?shop={shop_name}&id={prod_id}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(full_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # 轉為可顯示格式
        buf = io.BytesIO()
        qr_img.save(buf, format='PNG')
        byte_im = buf.getvalue()

        # D. 顯示結果
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.write("### 🔗 專屬連結")
            st.code(full_url)
            st.image(byte_im, caption="掃描此二維碼查看電子手冊", width=250)
        with c2:
            st.write("### 📥 下載資源")
            st.download_button(
                label="下載 QR Code 圖片",
                data=byte_im,
                file_name=f"QR_{shop_name}_{prod_id}.png",
                mime="image/png"
            )
    else:
        st.error("請填寫產品編號與名稱！")

# --- 5. 數據列表展示 ---
st.divider()
st.subheader("📋 目前已上傳產品清單")
df_display = pd.read_excel('products.xlsx')
st.dataframe(df_display, use_container_width=True)