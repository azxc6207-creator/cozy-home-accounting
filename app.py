import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar

# ==========================================
# 1. 頁面設定與莫蘭迪奶茶色系 CSS (強制並排版)
# ==========================================
st.set_page_config(
    page_title="小窩記帳 🏠",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;800;900&display=swap');

    /* 🎨 全局莫蘭迪奶茶色背景 + 🐾 半透明狗狗腳印 */
    html, body, [class*="css"], .stApp {
        font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background-color: #FAF5F0 !important;
        background-image: 
            url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="%23A07855" opacity="0.07" transform="rotate(18)"><path d="M12,11.5 C10.6,11.5 9.5,12.6 9.5,14 C9.5,15.4 10.6,17.5 12,17.5 C13.4,17.5 14.5,15.4 14.5,14 C14.5,12.6 13.4,11.5 12,11.5 Z M7.5,12 C8.3,12 9,11.3 9,10.5 C9,9.7 8.3,9 7.5,9 C6.7,9 6,9.7 6,10.5 C6,11.3 6.7,12 7.5,12 Z M16.5,12 C17.3,12 18,11.3 18,10.5 C18,9.7 17.3,9 16.5,9 C15.7,9 15,9.7 15,10.5 C15,11.3 15.7,12 16.5,12 Z M9.5,8 C10.3,8 11,7.3 11,6.5 C11,5.7 10.3,5 9.5,5 C8.7,5 8,5.7 8,6.5 C8,7.3 8.7,8 9.5,8 Z M14.5,8 C15.3,8 16,7.3 16,6.5 C16,5.7 13.3,8 14.5,8 Z"/></svg>'),
            url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="130" height="130" viewBox="0 0 24 24" fill="%238C6239" opacity="0.05" transform="rotate(-32)"><path d="M12,11.5 C10.6,11.5 9.5,12.6 9.5,14 C9.5,15.4 10.6,17.5 12,17.5 C13.4,17.5 14.5,15.4 14.5,14 C14.5,12.6 13.4,11.5 12,11.5 Z M7.5,12 C8.3,12 9,11.3 9,10.5 C9,9.7 8.3,9 7.5,9 C6.7,9 6,9.7 6,10.5 C6,11.3 6.7,12 7.5,12 Z M16.5,12 C17.3,12 18,11.3 18,10.5 C18,9.7 17.3,9 16.5,9 C15.7,9 15,9.7 15,10.5 C15,11.3 15.7,12 16.5,12 Z M9.5,8 C10.3,8 11,7.3 11,6.5 C11,5.7 10.3,5 9.5,5 C8.7,5 8,5.7 8,6.5 C8,7.3 8.7,8 9.5,8 Z M14.5,8 C15.3,8 16,7.3 16,6.5 C16,5.7 13.3,8 14.5,8 Z"/></svg>'),
            radial-gradient(circle at 12% 18%, rgba(232, 221, 208, 0.85) 0%, transparent 40%),
            radial-gradient(circle at 88% 12%, rgba(212, 195, 179, 0.75) 0%, transparent 35%),
            radial-gradient(circle at 20% 70%, rgba(242, 232, 223, 0.9) 0%, transparent 45%),
            radial-gradient(circle at 85% 80%, rgba(180, 145, 115, 0.25) 0%, transparent 45%) !important;
        background-attachment: fixed !important;
        color: #3D322C !important;
        font-size: 18px !important;
    }
    
    header[data-testid="stHeader"] { visibility: hidden; }
    footer { visibility: hidden; }

    /* 📌 關鍵修復：強制所有欄位在手機上「絕對水平並排」，禁止上下折行 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 6px !important;
    }
    div[data-testid="column"] {
        min-width: 0 !important;
    }

    /* 📌 日期選擇區塊標題放大 */
    div[data-testid="stDateInput"] label {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #7A573C !important;
    }

    /* 📱 手機直式專用頂欄 */
    .vertical-header-box {
        background: rgba(255, 255, 255, 0.92) !important;
        border: 1.5px solid #E2D5C5 !important;
        border-radius: 18px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 14px rgba(160, 120, 85, 0.08) !important;
    }

    /* 🍵 三大淺奶茶色功能按鈕 */
    .action-block div[data-testid="column"] .stPopover>button, 
    .action-block div[data-testid="column"] .stButton>button {
        width: 100% !important;
        background-color: #EEDFD2 !important;
        color: #5C4A3E !important;
        border: 1.5px solid #D4C3B3 !important;
        border-radius: 16px !important;
        padding: 10px 4px !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        box-shadow: 0 2px 8px rgba(160, 120, 85, 0.08) !important;
    }

    /* 流水帳卡片字體放大 */
    .item-title { font-size: 20px !important; font-weight: 800; color: #3D322C; }
    .item-amount { font-size: 22px !important; font-weight: 900; color: #8C6239; text-align: right; }
    .badge-tag {
        background-color: #EEDFD2; color: #7A573C;
        font-size: 13px !important; padding: 3px 10px; border-radius: 12px; font-weight: 700;
    }
    .sub-info { font-size: 15px !important; color: #8C7A6B; margin-top: 4px; }

    /* 🗑️ 刪除與 ✏️ 編輯白底按鈕 (保證並排且置中) */
    .stButton>button, div[data-testid="stPopover"]>button {
        border-radius: 14px !important;
        background-color: #FFFFFF !important;
        color: #3D322C !important;
        border: 1px solid #E2D5C5 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 6px 4px !important;
        box-shadow: 0 2px 6px rgba(160, 120, 85, 0.06) !important;
        transition: all 0.2s ease !important;
        display: inline-flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    .stButton>button:hover, div[data-testid="stPopover"]>button:hover {
        background-color: #FAF5F0 !important;
        border-color: #A07855 !important;
    }

    /* 分頁 Tabs 導覽列 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #E8DDD0;
        padding: 6px;
        border-radius: 25px;
        margin-bottom: 14px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 18px;
        padding: 8px 18px;
        color: #6E5A4C;
        font-weight: 700;
        font-size: 16px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #A07855 !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Session State 初始化 (加入區間日期)
# ==========================================
today_date = date.today()

if "start_date" not in st.session_state:
    st.session_state.start_date = date(today_date.year, today_date.month, 1)

if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today_date.year, today_date.month)
    st.session_state.end_date = date(today_date.year, today_date.month, last_day)

if "members" not in st.session_state:
    st.session_state.members = ["🐱 鼠", "🐱 熊"]

if "expense_categories" not in st.session_state:
    st.session_state.expense_categories = ["🍽️ 餐費", "🛋️ 居家日用", "🚗 交通費", "🏠 水電瓦斯網路費", "🎬 休閒娛樂", "🏥 醫療健康", "📦 其他"]

if "income_categories" not in st.session_state:
    st.session_state.income_categories = ["💰 薪資收入", "🎁 獎金紅包", "📈 投資理財", "🤝 副業兼職", "💵 其他收入"]

if "memos" not in st.session_state:
    st.session_state.memos = [{"id": 1, "text": "確認下個月水電費轉帳帳號"}]

if "shopping_list" not in st.session_state:
    st.session_state.shopping_list = [{"id": 101, "item": "鮮奶 🥛"}]

# ==========================================
# 3. 連接 Google Sheets 資料庫
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(ttl="0s")
        cols = ["ID", "日期", "類型", "類別", "項目", "金額", "記帳人", "備註", "結帳狀態", "結帳單號", "已同意人"]
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        df["類型"] = df["類型"].replace("", "支出")
        df["金額"] = pd.to_numeric(df["金額"], errors="coerce").fillna(0)
        return df
    except Exception:
        return pd.DataFrame(columns=["ID", "日期", "類型", "類別", "項目", "金額", "記帳人", "備註", "結帳狀態", "結帳單號", "已同意人"])

if "expenses_df" not in st.session_state:
    st.session_state.expenses_df = load_data()

# ==========================================
# 4. 主選單 Header & 分頁
# ==========================================
st.markdown("<h2 style='color:#7A573C; font-weight:900; margin-bottom:10px;'>🏠 小窩記帳 🐾</h2>", unsafe_allow_html=True)

tab_home, tab_charts, tab_memo, tab_shopping, tab_settings = st.tabs([
    "🏠 主頁記帳", "📊 統計圖表", "💬 備忘錄", "🛒 購物清單", "⚙️ 小窩設定"
])

# ==========================================
# TAB 1: 🏠 主頁記帳
# ==========================================
with tab_home:
    # 📌 頂欄：自訂日期區間查詢器
    st.markdown("<div class='vertical-header-box'>", unsafe_allow_html=True)
    v_col1, v_col2 = st.columns([2.5, 1])
    
    with v_col1:
        picked_range = st.date_input(
            "📅 選擇查詢區間", 
            value=(st.session_state.start_date, st.session_state.end_date),
            key="v_date_picker"
        )
        # 處理 Tuple 回傳值 (防止單選時的報錯)
        if isinstance(picked_range, tuple):
            if len(picked_range) == 2:
                st.session_state.start_date = picked_range[0]
                st.session_state.end_date = picked_range[1]
            elif len(picked_range) == 1:
                st.session_state.start_date = picked_range[0]
                st.session_state.end_date = picked_range[0]

    with v_col2:
        st.write("")
        st.write("")
        if st.button("↺ 本月", use_container_width=True):
            today = date.today()
            st.session_state.start_date = date(today.year, today.month, 1)
            _, last_day = calendar.monthrange(today.year, today.month)
            st.session_state.end_date = date(today.year, today.month, last_day)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 🍵 三大可愛按鈕區塊
    st.markdown("<div class='action-block'>", unsafe_allow_html=True)
    top_col1, top_col2, top_col3 = st.columns(3)
    
    with top_col1:
        with st.popover("💸 記一筆支出", use_container_width=True):
            st.markdown("### 💸 新增支出筆數")
            with st.form("add_exp_form", clear_on_submit=True):
                e_date = st.date_input("支出日期", datetime.now().date())
                e_payer = st.selectbox("付款人", st.session_state.members)
                e_cat = st.selectbox("支出分類", st.session_state.expense_categories)
                e_item = st.text_input("消費項目 (非必填)", placeholder="例如：加油、麵包")
                e_amount = st.number_input("金額 ($)", min_value=1, step=10, value=100)
                e_note = st.text_input("備註 (非必填)", placeholder="選填")
                
                if st.form_submit_button("確認新增支出"):
                    final_item = e_item.strip() if e_item else "未填寫"
                    new_row = pd.DataFrame([{
                        "ID": f"EXP-{int(datetime.now().timestamp())}",
                        "日期": str(e_date),
                        "類型": "支出",
                        "類別": str(e_cat),
                        "項目": str(final_item),
                        "金額": float(e_amount),
                        "記帳人": str(e_payer),
                        "備註": str(e_note),
                        "結帳狀態": "未結帳",
                        "結帳單號": "",
                        "已同意人": ""
                    }])
                    st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_row], ignore_index=True)
                    try:
                        conn.update(data=st.session_state.expenses_df)
                    except Exception:
                        pass
                    st.toast("🎉 支出新增成功！")
                    st.rerun()

    with top_col2:
        with st.popover("✨ 記一筆收入", use_container_width=True):
            st.markdown("### ✨ 新增收入筆數")
            with st.form("add_inc_form", clear_on_submit=True):
                i_date = st.date_input("收入日期", datetime.now().date())
                i_receiver = st.selectbox("收款人", st.session_state.members)
                i_cat = st.selectbox("收入分類", st.session_state.income_categories)
                i_item = st.text_input("收入項目 (非必填)", placeholder="例如：薪資發放")
                i_amount = st.number_input("金額 ($)", min_value=1, step=100, value=1000)
                i_note = st.text_input("備註 (非必填)", placeholder="選填")
                
                if st.form_submit_button("確認新增收入"):
                    final_item = i_item.strip() if i_item else "未填寫"
                    new_row = pd.DataFrame([{
                        "ID": f"INC-{int(datetime.now().timestamp())}",
                        "日期": str(i_date),
                        "類型": "收入",
                        "類別": str(i_cat),
                        "項目": str(final_item),
                        "金額": float(i_amount),
                        "記帳人": str(i_receiver),
                        "備註": str(i_note),
                        "結帳狀態": "未結帳",
                        "結帳單號": "",
                        "已同意人": ""
                    }])
                    st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_row], ignore_index=True)
                    try:
                        conn.update(data=st.session_state.expenses_df)
                    except Exception:
                        pass
                    st.toast("🎉 收入新增成功！")
                    st.rerun()

    with top_col3:
        with st.popover("🐾 歡樂算算帳", use_container_width=True):
            st.markdown("### 🐾 結帳專區")
            unsettled_df = st.session_state.expenses_df[st.session_state.expenses_df["結帳狀態"] != "已結帳"].copy()
            if unsettled_df.empty:
                st.info("目前沒有待結帳筆數。")
            else:
                st.write(f"待結帳總筆數：**{len(unsettled_df)}** 筆")
                st.markdown("請全員勾選確認同意：")
                chk_cols = st.columns(len(st.session_state.members))
                agreed_flags = [chk_cols[i].checkbox(f"{m}", key=f"settle_chk_{m}") for i, m in enumerate(st.session_state.members)]
                
                if st.button("🤝 完成結帳", use_container_width=True, disabled=(not all(agreed_flags))):
                    settle_id = f"SETTLE-{datetime.now().strftime('%Y%m%d%H%M')}"
                    st.session_state.expenses_df.loc[unsettled_df.index, "結帳狀態"] = "已結帳"
                    st.session_state.expenses_df.loc[unsettled_df.index, "結帳單號"] = settle_id
                    try:
                        conn.update(data=st.session_state.expenses_df)
                    except Exception:
                        pass
                    st.success("🎉 已完成結帳！")
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # 📌 放大置中顯示當前查詢的區間
    start_str = st.session_state.start_date.strftime('%Y-%m-%d')
    end_str = st.session_state.end_date.strftime('%Y-%m-%d')
    display_title = f"📅 {start_str}" if start_str == end_str else f"📅 {start_str} ~ {end_str}"
    
    st.markdown(
        f"<h2 style='text-align: center; color: #7A573C; font-weight: 900; font-size: 24px; margin: 10px 0;'>{display_title}</h2>", 
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 📊 根據區間過濾資料
    df_current = st.session_state.expenses_df.copy()
    if not df_current.empty:
        df_current["日期_dt"] = pd.to_datetime(df_current["日期"]).dt.date
        filtered_df = df_current[
            (df_current["日期_dt"] >= st.session_state.start_date) &
            (df_current["日期_dt"] <= st.session_state.end_date)
        ]
    else:
        filtered_df = pd.DataFrame()

    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values(by="日期", ascending=False)

    week_days_tw = ["一", "二", "三", "四", "五", "六", "日"]

    # 📌 逐條收支卡片 (編輯與刪除絕對並排)
    if filtered_df.empty:
        st.info("此區間內尚無任何收支紀錄。")
    else:
        for idx, row in filtered_df.iterrows():
            r_date = datetime.strptime(row["日期"], "%Y-%m-%d")
            day_week_str = week_days_tw[r_date.weekday()]
            
            # 使用精細的比例讓按鈕區塊有足夠空間並排
            c_card1, c_card2, c_actions = st.columns([3.5, 2, 1.8])
            
            with c_card1:
                st.markdown(f"<div class='item-title'>{row['項目']}</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class='sub-info'>
                    <span class='badge-tag'>{row['記帳人']}</span> 
                    {r_date.month}/{r_date.day} ({day_week_str}) · {row['類別']}
                </div>
                """, unsafe_allow_html=True)
                
            with c_card2:
                amt_prefix = "+" if row["類型"] == "收入" else ""
                amt_color = "#558B6E" if row["類型"] == "收入" else "#8C6239"
                st.markdown(f"<div class='item-amount' style='color:{amt_color};'>{amt_prefix}{row['金額']:,.0f}</div>", unsafe_allow_html=True)
            
            # ✏️ 與 🗑️ ICON 絕對並排區塊
            with c_actions:
                act_col1, act_col2 = st.columns([1, 1])
                
                with act_col1:
                    with st.popover("✏️"):
                        st.markdown("### ✏️ 編輯紀錄")
                        with st.form(f"edit_form_{row['ID']}"):
                            e_date_val = st.date_input("日期", r_date)
                            e_type_val = st.radio("類型", ["支出", "收入"], index=0 if row["類型"] == "支出" else 1)
                            cats = st.session_state.expense_categories if e_type_val == "支出" else st.session_state.income_categories
                            cat_idx = cats.index(row["類別"]) if row["類別"] in cats else 0
                            e_cat_val = st.selectbox("分類", cats, index=cat_idx)
                            e_item_val = st.text_input("項目", value=row["項目"])
                            e_amt_val = st.number_input("金額", value=float(row["金額"]))
                            e_payer_val = st.selectbox("成員", st.session_state.members, index=st.session_state.members.index(row["記帳人"]) if row["記帳人"] in st.session_state.members else 0)
                            e_note_val = st.text_input("備註", value=row["備註"])

                            if st.form_submit_button("儲存修改"):
                                match_idx = st.session_state.expenses_df[st.session_state.expenses_df["ID"] == row["ID"]].index
                                st.session_state.expenses_df.loc[match_idx, ["日期", "類型", "類別", "項目", "金額", "記帳人", "備註"]] = [
                                    str(e_date_val), e_type_val, e_cat_val, e_item_val, float(e_amt_val), e_payer_val, e_note_val
                                ]
                                try:
                                    conn.update(data=st.session_state.expenses_df)
                                except Exception:
                                    pass
                                st.toast("✅ 修改成功！")
                                st.rerun()

                with act_col2:
                    if st.button("🗑️", key=f"del_btn_{row['ID']}"):
                        st.session_state.expenses_df = st.session_state.expenses_df[st.session_state.expenses_df["ID"] != row["ID"]]
                        try:
                            conn.update(data=st.session_state.expenses_df)
                        except Exception:
                            pass
                        st.toast("🗑️ 已刪除紀錄！")
                        st.rerun()
            st.divider()

# ==========================================
# TAB 2: 📊 統計圖表
# ==========================================
with tab_charts:
    st.subheader("📊 統計圖表視覺化分析")
    st.divider()

    current_df = st.session_state.expenses_df.copy()
    
    if current_df.empty:
        st.info("尚無數據可繪製圖表。")
    else:
        st.markdown("<h4 style='text-align: center; color: #8C6239;'>🍕 支出類別比例 (圓餅圖)</h4>", unsafe_allow_html=True)
        exp_df = current_df[current_df["類型"] == "支出"]
        if not exp_df.empty:
            fig_pie = px.pie(
                exp_df, names="類別", values="金額", hole=0.45,
                color_discrete_sequence=["#A07855", "#C5A880", "#8C6239", "#7A573C", "#B08968"]
            )
            fig_pie.update_traces(textfont=dict(size=16), textinfo='percent+label')
            fig_pie.update_layout(
                font=dict(size=15), 
                showlegend=True, 
                legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
                margin=dict(t=10, b=10, l=10, r=10), 
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

        st.divider()
        st.markdown("<h4 style='text-align: center; color: #8C6239;'>📊 時間支出趨勢圖 (長條圖)</h4>", unsafe_allow_html=True)
        if not exp_df.empty:
            exp_df["日期_dt"] = pd.to_datetime(exp_df["日期"])
            daily_sum = exp_df.groupby(exp_df["日期_dt"].dt.day)["金額"].sum().reset_index()
            
            fig_bar = px.bar(
                daily_sum, x="日期_dt", y="金額", color_discrete_sequence=["#A07855"], text_auto=',.0f'
            )
            fig_bar.update_traces(textfont=dict(size=16), textposition='outside')
            fig_bar.update_layout(
                font=dict(size=15),
                xaxis=dict(title=dict(text="日期 (日)", font=dict(size=15))),
                yaxis=dict(title=dict(text="金額 ($)", font=dict(size=15))),
                margin=dict(t=30, b=10, l=10, r=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# TAB 3: 💬 備忘錄
# ==========================================
with tab_memo:
    st.subheader("💬 家族備忘錄")
    st.divider()

    with st.form("add_memo_form", clear_on_submit=True):
        col_m1, col_m2 = st.columns([3, 1])
        new_memo_text = col_m1.text_input("輸入備忘事項", placeholder="輸入需要討論的事項...", label_visibility="collapsed")
        submit_memo = col_m2.form_submit_button("➕ 新增事項")
        if submit_memo and new_memo_text:
            new_id = int(datetime.now().timestamp() * 1000)
            st.session_state.memos.append({"id": new_id, "text": new_memo_text})
            st.success("已新增備忘事項！")
            st.rerun()

    st.markdown("#### 📌 待處理備忘事項：")
    for memo in list(st.session_state.memos):
        col_chk, col_txt, col_edit = st.columns([0.8, 4.5, 1])
        with col_chk:
            checked = st.checkbox("", key=f"memo_chk_{memo['id']}")
            if checked:
                st.session_state.memos.remove(memo)
                st.toast("✅ 已完成並刪除！")
                st.rerun()
        with col_txt:
            st.markdown(f"<div style='font-size:18px; padding-top:4px;'>• {memo['text']}</div>", unsafe_allow_html=True)
        with col_edit:
            with st.popover("✏️"):
                edited_text = st.text_input("修改備忘內容", value=memo["text"], key=f"edit_memo_input_{memo['id']}")
                if st.button("儲存修改", key=f"save_memo_{memo['id']}"):
                    memo["text"] = edited_text
                    st.toast("修改成功！")
                    st.rerun()
        st.divider()

# ==========================================
# TAB 4: 🛒 購物清單
# ==========================================
with tab_shopping:
    st.subheader("🛒 待買清單")
    st.divider()

    with st.form("add_shop_form", clear_on_submit=True):
        col_s1, col_s2 = st.columns([3, 1])
        new_shop_item = col_s1.text_input("輸入待買商品", placeholder="輸入要購買的物品...", label_visibility="collapsed")
        submit_shop = col_s2.form_submit_button("➕ 新增商品")
        if submit_shop and new_shop_item:
            new_id = int(datetime.now().timestamp() * 1000)
            st.session_state.shopping_list.append({"id": new_id, "item": new_shop_item})
            st.success("已新增待買商品！")
            st.rerun()

    st.markdown("#### 🛒 待採買項目：")
    for shop_item in list(st.session_state.shopping_list):
        col_chk, col_txt, col_edit = st.columns([0.8, 4.5, 1])
        with col_chk:
            checked = st.checkbox("", key=f"shop_chk_{shop_item['id']}")
            if checked:
                st.session_state.shopping_list.remove(shop_item)
                st.toast("🎉 已採買完成並移除！")
                st.rerun()
        with col_txt:
            st.markdown(f"<div style='font-size:18px; padding-top:4px;'>🛒 {shop_item['item']}</div>", unsafe_allow_html=True)
        with col_edit:
            with st.popover("✏️"):
                edited_item = st.text_input("修改商品名稱", value=shop_item["item"], key=f"edit_shop_input_{shop_item['id']}")
                if st.button("儲存修改", key=f"save_shop_{shop_item['id']}"):
                    shop_item["item"] = edited_item
                    st.toast("修改成功！")
                    st.rerun()
        st.divider()

# ==========================================
# TAB 5: ⚙️ 小窩設定
# ==========================================
with tab_settings:
    st.subheader("⚙️ 小窩設定")
    st.divider()

    set_col1, set_col2, set_col3 = st.columns(3)

    # 🐱 1. 成員管理
    with set_col1:
        st.markdown(f"### 🐱 成員管理 (`{len(st.session_state.members)}` / 30 人)")
        with st.form("add_member_form", clear_on_submit=True):
            col_icon, col_name = st.columns([1, 2])
            new_m_icon = col_icon.text_input("Icon", value="🐱", key="new_m_icon")
            new_m_name = col_name.text_input("名稱", placeholder="阿嬤", key="new_m_name")
            
            if st.form_submit_button("➕ 新增成員"):
                if len(st.session_state.members) < 30 and new_m_name:
                    full_m = f"{new_m_icon.strip()} {new_m_name.strip()}"
                    st.session_state.members.append(full_m)
                    st.success(f"已新增：{full_m}")
                    st.rerun()

        for idx, m in enumerate(st.session_state.members):
            m_col1, m_actions = st.columns([3, 1.8])
            m_col1.write(f"• **{m}**")
            
            with m_actions:
                act1, act2 = st.columns([1, 1])
                with act1:
                    with st.popover("✏️"):
                        parts = m.split(" ", 1)
                        cur_icon = parts[0] if len(parts) > 1 else "🐱"
                        cur_name = parts[1] if len(parts) > 1 else parts[0]
                        
                        edit_icon = st.text_input("修改 Icon", value=cur_icon, key=f"m_icon_{idx}")
                        edit_name = st.text_input("修改名稱", value=cur_name, key=f"m_name_{idx}")
                        if st.button("儲存", key=f"save_m_{idx}"):
                            st.session_state.members[idx] = f"{edit_icon.strip()} {edit_name.strip()}"
                            st.toast("✅ 修改成功！")
                            st.rerun()
                with act2:
                    if st.button("🗑️", key=f"del_mem_{idx}"):
                        if len(st.session_state.members) > 1:
                            st.session_state.members.pop(idx)
                            st.rerun()

    # 🏷️ 2. 支出類別管理
    with set_col2:
        st.markdown(f"### 🏷️ 支出類別 (`{len(st.session_state.expense_categories)}` / 30 項)")
        with st.form("add_exp_cat_form", clear_on_submit=True):
            col_icon, col_name = st.columns([1, 2])
            new_e_icon = col_icon.text_input("Icon", value="📦", key="new_e_icon")
            new_e_name = col_name.text_input("類別名稱", placeholder="寵物費用", key="new_e_name")
            
            if st.form_submit_button("➕ 新增類別"):
                if len(st.session_state.expense_categories) < 30 and new_e_name:
                    full_c = f"{new_e_icon.strip()} {new_e_name.strip()}"
                    st.session_state.expense_categories.append(full_c)
                    st.success(f"已新增：{full_c}")
                    st.rerun()

        for idx, c in enumerate(st.session_state.expense_categories):
            c_col1, c_actions = st.columns([3, 1.8])
            c_col1.write(f"• **{c}**")
            
            with c_actions:
                act1, act2 = st.columns([1, 1])
                with act1:
                    with st.popover("✏️"):
                        parts = c.split(" ", 1)
                        cur_icon = parts[0] if len(parts) > 1 else "📦"
                        cur_name = parts[1] if len(parts) > 1 else parts[0]
                        
                        edit_icon = st.text_input("修改 Icon", value=cur_icon, key=f"ec_icon_{idx}")
                        edit_name = st.text_input("修改名稱", value=cur_name, key=f"ec_name_{idx}")
                        if st.button("儲存", key=f"save_ec_{idx}"):
                            st.session_state.expense_categories[idx] = f"{edit_icon.strip()} {edit_name.strip()}"
                            st.toast("✅ 修改成功！")
                            st.rerun()
                with act2:
                    if st.button("🗑️", key=f"del_exp_cat_{idx}"):
                        if len(st.session_state.expense_categories) > 1:
                            st.session_state.expense_categories.pop(idx)
                            st.rerun()

    # 💰 3. 收入類別管理
    with set_col3:
        st.markdown(f"### 💰 收入類別 (`{len(st.session_state.income_categories)}` / 10 項)")
        with st.form("add_inc_cat_form", clear_on_submit=True):
            col_icon, col_name = st.columns([1, 2])
            new_i_icon = col_icon.text_input("Icon", value="💵", key="new_i_icon")
            new_i_name = col_name.text_input("類別名稱", placeholder="壓歲紅包", key="new_i_name")
            
            if st.form_submit_button("➕ 新增類別"):
                if len(st.session_state.income_categories) < 10 and new_i_name:
                    full_ic = f"{new_i_icon.strip()} {new_i_name.strip()}"
                    st.session_state.income_categories.append(full_ic)
                    st.success(f"已新增：{full_ic}")
                    st.rerun()

        for idx, ic in enumerate(st.session_state.income_categories):
            ic_col1, ic_actions = st.columns([3, 1.8])
            ic_col1.write(f"• **{ic}**")
            
            with ic_actions:
                act1, act2 = st.columns([1, 1])
                with act1:
                    with st.popover("✏️"):
                        parts = ic.split(" ", 1)
                        cur_icon = parts[0] if len(parts) > 1 else "💵"
                        cur_name = parts[1] if len(parts) > 1 else parts[0]
                        
                        edit_icon = st.text_input("修改 Icon", value=cur_icon, key=f"ic_icon_{idx}")
                        edit_name = st.text_input("修改名稱", value=cur_name, key=f"ic_name_{idx}")
                        if st.button("儲存", key=f"save_ic_{idx}"):
                            st.session_state.income_categories[idx] = f"{edit_icon.strip()} {edit_name.strip()}"
                            st.toast("✅ 修改成功！")
                            st.rerun()
                with act2:
                    if st.button("🗑️", key=f"del_inc_cat_{idx}"):
                        if len(st.session_state.income_categories) > 1:
                            st.session_state.income_categories.pop(idx)
                            st.rerun()
