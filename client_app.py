import streamlit as st
import os
import pandas as pd

def get_query_params():
    # 讀取網址上的 query string (支援 shop, id)
    params = st.query_params if hasattr(st, "query_params") else st.experimental_get_query_params()
    shop = params.get("shop", [None])[0]
    prod_id = params.get("id", [None])[0]
    return shop, prod_id

def load_filtered_product(filepath="products.xlsx", shop=None, prod_id=None):
    # 從 Excel 過濾 藥房名稱==shop 且 id==prod_id
    df = pd.read_excel(filepath, dtype=str)
    if shop is not None:
        df = df[df["pharmacy_name"] == shop]
    if prod_id is not None:
        df = df[df["id"] == prod_id]
    return df.iloc[0] if not df.empty else None

def get_pharmacy_contact(filepath="products.xlsx", shop=None):
    df = pd.read_excel(filepath, dtype=str)
    row = df[df["pharmacy_name"] == shop]
    if row.empty:
        return None, None
    phone = row.iloc[0]["pharmacy_phone"] if "pharmacy_phone" in row.columns else None
    whatsapp = row.iloc[0]["pharmacy_whatsapp"] if "pharmacy_whatsapp" in row.columns else None
    return phone, whatsapp

def get_image_path(product, shop):
    # 根據 shop 名稱去 images/藥房名稱/ 裡找對應圖片
    if "image" in product and isinstance(product["image"], str) and product["image"]:
        file_name = os.path.basename(product["image"])
        img_path = os.path.join("images", shop, file_name)
        if os.path.exists(img_path):
            return img_path
    return None
import pandas as pd
import urllib.parse

def load_products(filepath="products.xlsx"):
    return pd.read_excel(filepath)

def get_query_params():
    query_params = st.experimental_get_query_params()
    if 'id' in query_params and query_params['id']:
        return query_params['id'][0]
    return None

def display_product(product):
    # product: a pandas Series
    # Assume columns: id, name, image, intro, suitable_for, usage, notes, pharmacy_phone, pharmacy_wechat_qrcode
    st.markdown(
        f"""
        <div style="background-color:#F7F7F7;min-height:100vh;padding:0;margin:0">
            <div style="text-align:center">
                <img src="{product['image']}" style="width:100%;max-width:450px;height:auto;display:block;margin:0 auto 16px auto;" />
                <h2 style="font-size:2.2rem;color:#232323;margin-bottom:24px;margin-top:8px">{product['name']}</h2>
            </div>
            <div style="padding:8px 16px;">
                <div style="font-size:1.1rem;color:#404040;margin-bottom:18px">
                    <b>核心簡介：</b><br>{product['intro']}
                </div>
                <div style="font-size:1.1rem;color:#404040;margin-bottom:18px">
                    <b>適用人群：</b><br>{product['suitable_for']}
                </div>
                <div style="font-size:1.1rem;color:#404040;margin-bottom:18px">
                    <b>食用方法：</b><br>{product['usage']}
                </div>
                <div style="font-size:1.1rem;color:#404040;margin-bottom:70px">
                    <b>注意事項：</b><br>{product['notes']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )

def show_pharmacy_contact(product):
    with st.sidebar:
        st.markdown("### 聯繫藥房")
        if "pharmacy_wechat_qrcode" in product and pd.notna(product["pharmacy_wechat_qrcode"]):
            st.image(product["pharmacy_wechat_qrcode"], caption="藥房微信", use_column_width=True)
        if "pharmacy_phone" in product and pd.notna(product["pharmacy_phone"]):
            st.markdown(f"<div style='font-size:1.25rem;font-weight:bold;'>電話：{product['pharmacy_phone']}</div>", unsafe_allow_html=True)
        
def show_fixed_contact_btn():
    btn_html = """
    <style>
      .contact-btn {
        position: fixed;
        bottom: 18px;
        left: 0;
        width: 94vw;
        margin: 0 3vw;
        z-index: 9999;
      }
      @media (min-width:420px) {
        .contact-btn {width:380px; left:50%; transform:translateX(-50%);}
      }
    </style>
    <div class='contact-btn'>
      <button id="contact_pharmacy_btn"
        style="background:#0C66F2;color:white;width:100%;font-size:1.3rem;font-weight:bold;padding:15px 0;border:none;border-radius:10px;box-shadow:0 3px 14px #0001;cursor:pointer;">
        聯繫藥房
      </button>
    </div>
    <script>
      const btn = window.parent.document.getElementById('contact_pharmacy_btn')
      if(btn){
        btn.onclick = () => window.parent.postMessage('openPharmacyContact','*')
      }
    </script>
    """
    st.markdown(btn_html, unsafe_allow_html=True)
    # This only "marks up" a button and expects Streamlit rerun/callback.
    # So we'll make a proper Streamlit button as well:
    if st.button("聯繫藥房", key="contact_pharmacy_fixed"):
        st.session_state['show_pharmacy'] = True

def main():
    st.set_page_config(page_title="產品說明書", page_icon="📦", layout="centered")
    st.markdown(
        """
        <style>
        body { background: #f7f7f7 !important; }
        .modern-text-large { font-size: 1.15rem;color:#232323; }
        </style>
        """, unsafe_allow_html=True
    )

    # Initialize session state for the popup
    if "show_pharmacy" not in st.session_state:
        st.session_state["show_pharmacy"] = False

    id_param = get_query_params()
    df = None
    if id_param:
        try:
            df = load_products()
        except Exception as e:
            st.error("無法讀取產品資料 (products.xlsx)")
            return

        product_row = df[df['id'] == id_param]
        if not product_row.empty:
            product = product_row.iloc[0]
            display_product(product)
            show_fixed_contact_btn()
            if st.session_state.get("show_pharmacy"):
                st.markdown(
                    """
                    <div style="
                        position:fixed; left:0; top:0; width:100vw; height:100vh;
                        background:rgba(0,0,0,0.23); z-index:20000;
                        display:flex; align-items:center; justify-content:center;
                    ">
                        <div style="
                            background:#fff; border-radius:16px; padding:30px 16px 12px 16px;
                            max-width:340px;width:90vw;text-align:center;box-shadow:0 8px 32px #0003;">
                    """, unsafe_allow_html=True
                )
                if pd.notna(product.get("pharmacy_wechat_qrcode", "")):
                    st.image(product["pharmacy_wechat_qrcode"], caption="藥房微信", use_column_width=True)
                if pd.notna(product.get("pharmacy_phone", "")):
                    st.markdown(
                        f"<div style='margin:12px 0 10px 0;font-size:1.25rem;font-weight:bold;'>電話：{product['pharmacy_phone']}</div>",
                        unsafe_allow_html=True
                    )
                st.markdown('<button onclick="window.parent.location.reload()" style="margin-top:18px;padding:12px 32px;border:none;background:#0C66F2;color:white;font-size:1.12rem;border-radius:8px;cursor:pointer;">關閉</button></div></div>', unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='margin-top:80px;text-align:center;font-size:1.5rem;color:#232323;'>請掃描產品包裝上的二維碼查看詳情</div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            "<div style='margin-top:80px;text-align:center;font-size:1.5rem;color:#232323;'>請掃描產品包裝上的二維碼查看詳情</div>",
            unsafe_allow_html=True
        )

main()