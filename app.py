import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar
import streamlit.components.v1 as components

# ==========================================
# 1. 頁面設定與莫蘭迪奶茶色系 CSS (強制防跑版)
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

    /* 📌 永遠置頂的日曆與按鈕容器 (Sticky Top) */
    .sticky-calendar-bar {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 0px !important;
        z-index: 9999 !important;
        background: rgba(250, 245, 240, 0.96) !important;
        backdrop-filter: blur(12px) !important;
        padding: 10px 10px 14px 10px !important;
        border-bottom: 2px solid #E2D5C5 !important;
        margin: -1rem -1rem 12px -1rem !important; /* 擴展貼合螢幕邊緣 */
        border-radius: 0 0 20px 20px !important;
        box-shadow: 0 4px 16px rgba(160, 120, 85, 0.1) !important;
    }

    /* 🛑 終極修復：強制所有特定容器內的手機排版絕對「水平並排」，絕不自動折行 */
    .cal-compact-grid div[data-testid="stHorizontalBlock"],
    .action-block div[data-testid="stHorizontalBlock"],
    .tx-row div[data-testid="stHorizontalBlock"],
    .tx-actions div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    
    .cal-compact-grid div[data-testid="stHorizontalBlock"] { gap: 2px !important; }
    .action-block div[data-testid="stHorizontalBlock"] { gap: 6px !important; }
    .tx-row div[data-testid="stHorizontalBlock"] { gap: 4px !important; }
    .tx-actions div[data-testid="stHorizontalBlock"] { gap: 4px !important; justify-content: flex-end !important; }

    .cal-compact-grid div[data-testid="column"],
    .action-block div[data-testid="column"],
    .tx-row div[data-testid="column"],
    .tx-actions div[data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0px !important;
    }

    /* 日曆按鈕縮小為圓形緊湊版 */
    .cal-compact-grid div[data-testid="column"] .stButton>button {
        width: 100% !important;
        border-radius: 50% !important;
        padding: 0px !important;
        background-color: transparent !important;
        color: #3D322C !important;
        border: none !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        height: 38px !important;
        width: 38px !important;
        margin: 0 auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .cal-compact-grid div[data-testid="column"] .stButton>button:hover {
        background-color: #E2D5C5 !important;
        color: #3D322C !important;
    }

    /* 🍵 三大淺奶茶色功能按鈕 */
    .action-block div[data-testid="column"] .stPopover>button {
        width: 100% !important;
        background-color: #EEDFD2 !important;
        color: #5C4A3E !important;
        border: 1.5px solid #D4C3B3 !important;
        border-radius: 14px !important;
        padding: 8px 2px !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        box-shadow: 0 2px 6px rgba(160, 120, 85, 0.08) !important;
    }

    /* 📋 明細淺底色卡片容器 (簡單橫列呈現) */
    .tx-row {
        background-color: #FDF9F5 !important;
        border-radius: 12px !important;
        padding: 10px 12px !important;
        margin-bottom: 8px !important;
        border: 1px solid #EAE0D5 !important;
        box-shadow: 0 2px 4px rgba(160, 120, 85, 0.04) !important;
    }

    /* 🗑️ 刪除與 ✏️ 編輯白底按鈕 (保證並排) */
    .tx-actions .stButton>button, .tx-actions div[data-testid="stPopover"]>button {
        border-radius: 10px !important;
        background-color: #FFFFFF !important;
        color: #3D322C !important;
        border: 1px solid #E2D5C5 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 4px !important;
        box-shadow: 0 2px 4px rgba(160, 120, 85, 0.06) !important;
        display: inline-flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* 底部區間查詢框 */
    .bottom-query-box {
        background: rgba(255, 255, 255, 0.92) !important;
        border: 1.5px solid #E2D5C5 !important;
        border-radius: 18px !important;
        padding: 18px !important;
        margin-top: 20px !important;
        margin-bottom: 30px !important;
        box-shadow: 0 4px 14px rgba(160, 120, 85, 0.08) !important;
    }
    div[data-testid="stDateInput"] label {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #7A573C !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# ⚡ 隱藏 JavaScript: 阻擋 iPhone 日期鍵盤跳出
# ==========================================
components.html(
    """
    <script>
    // 自動監聽並攔截所有 date input，設定為 readonly 與 inputmode=none
    const observer = new MutationObserver(() => {
        const inputs = window.parent.document.querySelectorAll('[data-testid="stDateInput"] input');
        inputs.forEach(input => {
            if (input.getAttribute('inputmode') !== 'none') {
                input.setAttribute('inputmode', 'none');
                input.setAttribute('readonly', 'true');
            }
        });
    });
    // 啟動監聽器，確保連彈窗內的日期選擇器也一併被攔截
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    </script>
    """,
    height=0, width=0
)

# ==========================================
# 2. Session State 初始化
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

if "cal_selected_date" not in st.session_state:
    st.session_state.cal_selected_date = date.today()

if "filter_to_single_day" not in st.session_state:
    st.session_state.filter_to_single_day = False

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
    # 📌 置頂區塊：緊湊日曆 + 3大功能按鈕
    st.markdown("<div class='sticky-calendar-bar'>", unsafe_allow_html=True)
    
    # 年月切換
    cal_head_1, cal_head_2 = st.columns([1.5, 1])
    with cal_head_1:
        st.markdown(f"<div style='font-weight:900; font-size:20px; color:#3D322C; padding-top:4px;'>📅 {st.session_state.cal_selected_date.strftime('%Y年%m月')}</div>", unsafe_allow_html=True)
    with cal_head_2:
        sel_month = st.selectbox("切換月份", list(range(1, 13)), index=st.session_state.cal_selected_date.month - 1, label_visibility="collapsed")
        
    sel_year = st.session_state.cal_selected_date.year

    if sel_month != st.session_state.cal_selected_date.month:
        st.session_state.cal_selected_date = date(sel_year, sel_month, 1)
        st.rerun()

    # 7 欄日曆表頭
    st.markdown("<div class='cal-compact-grid'>", unsafe_allow_html=True)
    week_names = ["日", "一", "二", "三", "四", "五", "六"]
    w_cols = st.columns(7)
    for idx, w_name in enumerate(week_names):
        w_cols[idx].markdown(f"<div style='text-align:center; font-size:13px; color:#8C7A6B; font-weight:800;'>{w_name}</div>", unsafe_allow_html=True)

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(int(sel_year), int(sel_month))

    for week in month_days:
        cols = st.columns(7)
        for day_idx, day_num in enumerate(week):
            if day_num == 0:
                cols[day_idx].write("")
            else:
                curr_d = date(int(sel_year), int(sel_month), day_num)
                is_selected = (curr_d == st.session_state.cal_selected_date)
                btn_str = f"**{day_num}**" if is_selected else f"{day_num}"
                
                if cols[day_idx].button(btn_str, key=f"c_day_{curr_d}"):
                    st.session_state.cal_selected_date = curr_d
                    st.session_state.filter_to_single_day = True
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True) # cal-compact-grid 結束

    # 3 大可愛功能按鈕區塊
    st.markdown("<div class='action-block' style='margin-top:10px;'>", unsafe_allow_html=True)
    top_col1, top_col2, top_col3 = st.columns(3)
    
    with top_col1:
        with st.popover("💸 記一筆支出", use_container_width=True):
            st.markdown("### 💸 新增支出筆數")
            with st.form("add_exp_form", clear_on_submit=True):
                e_date = st.date_input("支出日期", st.session_state.cal_selected_date)
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
                    try: conn.update(data=st.session_state.expenses_df)
                    except: pass
                    st.toast("🎉 支出新增成功！")
                    st.rerun()

    with top_col2:
        with st.popover("✨ 記一筆收入", use_container_width=True):
            st.markdown("### ✨ 新增收入筆數")
            with st.form("add_inc_form", clear_on_submit=True):
                i_date = st.date_input("收入日期", st.session_state.cal_selected_date)
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
                    try: conn.update(data=st.session_state.expenses_df)
                    except: pass
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
                    try: conn.update(data=st.session_state.expenses_df)
                    except: pass
                    st.success("🎉 已完成結帳！")
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True) # action-block 結束
    st.markdown("</div>", unsafe_allow_html=True) # sticky-calendar-bar 結束

    # 📌 顯示當前查詢的區間狀態
    if st.session_state.filter_to_single_day:
        display_title = f"📅 {st.session_state.cal_selected_date}"
    else:
        start_str = st.session_state.start_date.strftime('%Y-%m-%d')
        end_str = st.session_state.end_date.strftime('%Y-%m-%d')
        display_title = f"📅 {start_str}" if start_str == end_str else f"📅 {start_str} ~ {end_str}"
    
    st.markdown(
        f"<h2 style='text-align: center; color: #7A573C; font-weight: 900; font-size: 22px; margin: 6px 0;'>{display_title}</h2>", 
        unsafe_allow_html=True
    )

    # 📊 根據自訂區間或單日過濾資料
    df_current = st.session_state.expenses_df.copy()
    if not df_current.empty:
        df_current["日期_dt"] = pd.to_datetime(df_current["日期"]).dt.date
        if st.session_state.filter_to_single_day:
            filtered_df = df_current[df_current["日期_dt"] == st.session_state.cal_selected_date]
        else:
            filtered_df = df_current[
                (df_current["日期_dt"] >= st.session_state.start_date) &
                (df_current["日期_dt"] <= st.session_state.end_date)
            ]
    else:
        filtered_df = pd.DataFrame()

    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values(by="日期", ascending=False)

    week_days_tw = ["一", "二", "三", "四", "五", "六", "日"]

    # 📌 淺底色橫列呈現的收支清單 (手機防跑版並排)
    if filtered_df.empty:
        st.info("此區間內尚無任何收支紀錄。")
    else:
        for idx, row in filtered_df.iterrows():
            r_date = datetime.strptime(row["日期"], "%Y-%m-%d")
            day_week_str = week_days_tw[r_date.weekday()]
            
            # 使用淺底色 tx-row 容器
            st.markdown("<div class='tx-row'>", unsafe_allow_html=True)
            
            c_card1, c_card2, c_actions = st.columns([3.5, 2, 1.8])
            
            with c_card1:
                st.markdown(f"<div style='font-size:16px; font-weight:800; color:#3D322C; margin-bottom:2px;'>{row['項目']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:13px; color:#8C7A6B;'>{row['記帳人']} · {r_date.month}/{r_date.day}({day_week_str}) · {row['類別']}</div>", unsafe_allow_html=True)
                
            with c_card2:
                amt_prefix = "+" if row["類型"] == "收入" else ""
                amt_color = "#558B6E" if row["類型"] == "收入" else "#8C6239"
                st.markdown(f"<div style='font-size:18px; font-weight:900; color:{amt_color}; text-align:right;'>{amt_prefix}{row['金額']:,.0f}</div>", unsafe_allow_html=True)
            
            # ✏️ 與 🗑️ 絕對水平並排區塊
            with c_actions:
                st.markdown("<div class='tx-actions'>", unsafe_allow_html=True)
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
                                try: conn.update(data=st.session_state.expenses_df)
                                except: pass
                                st.toast("✅ 修改成功！")
                                st.rerun()

                with act_col2:
                    if st.button("🗑️", key=f"del_btn_{row['ID']}"):
                        st.session_state.expenses_df = st.session_state.expenses_df[st.session_state.expenses_df["ID"] != row["ID"]]
                        try: conn.update(data=st.session_state.expenses_df)
                        except: pass
                        st.toast("🗑️ 已刪除紀錄！")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True) # tx-actions 結束
            st.markdown("</div>", unsafe_allow_html=True) # tx-row 結束

    # 📌 底部自訂區間查詢框
    st.markdown("<div class='bottom-query-box'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#7A573C; margin-bottom:10px;'>🔍 自訂區間查詢</h3>", unsafe_allow_html=True)
    
    picked_range = st.date_input(
        "選擇起始與結束日期", 
        value=(st.session_state.start_date, st.session_state.end_date),
        key="bottom_date_picker"
    )
    
    q_col1, q_col2 = st.columns(2)
    if q_col1.button("✅ 查詢此區間", use_container_width=True):
        if isinstance(picked_range, tuple) and len(picked_range) == 2:
            st.session_state.start_date = picked_range[0]
            st.session_state.end_date = picked_range[1]
            st.session_state.filter_to_single_day = False
            st.rerun()
        elif isinstance(picked_range, tuple) and len(picked_range) == 1:
            st.session_state.start_date = picked_range[0]
            st.session_state.end_date = picked_range[0]
            st.session_state.filter_to_single_day = False
            st.rerun()
            
    if q_col2.button("↺ 看本月全部", use_container_width=True):
        today = date.today()
        st.session_state.start_date = date(today.year, today.month, 1)
        _, last_day = calendar.monthrange(today.year, today.month)
        st.session_state.end_date = date(today.year, today.month, last_day)
        st.session_state.filter_to_single_day = False
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)

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
            fig_pie.update_layout(font=dict(size=15), showlegend=True, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"), margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

        st.divider()
        st.markdown("<h4 style='text-align: center; color: #8C6239;'>📊 時間支出趨勢圖 (長條圖)</h4>", unsafe_allow_html=True)
        if not exp_df.empty:
            exp_df["日期_dt"] = pd.to_datetime(exp_df["日期"])
            daily_sum = exp_df.groupby(exp_df["日期_dt"].dt.day)["金額"].sum().reset_index()
            fig_bar = px.bar(daily_sum, x="日期_dt", y="金額", color_discrete_sequence=["#A07855"], text_auto=',.0f')
            fig_bar.update_traces(textfont=dict(size=16), textposition='outside')
            fig_bar.update_layout(font=dict(size=15), xaxis=dict(title=dict(text="日期 (日)", font=dict(size=15))), yaxis=dict(title=dict(text="金額 ($)", font=dict(size=15))), margin=dict(t=30, b=10, l=10, r=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
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

    for memo in list(st.session_state.memos):
        col_chk, col_txt, col_edit = st.columns([0.8, 4.5, 1])
        with col_chk:
            if st.checkbox("", key=f"memo_chk_{memo['id']}"):
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

    for shop_item in list(st.session_state.shopping_list):
        col_chk, col_txt, col_edit = st.columns([0.8, 4.5, 1])
        with col_chk:
            if st.checkbox("", key=f"shop_chk_{shop_item['id']}"):
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

    with set_col1:
        st.markdown(f"### 🐱 成員管理")
        with st.form("add_member_form", clear_on_submit=True):
            col_icon, col_name = st.columns([1, 2])
            new_m_icon = col_icon.text_input("Icon", value="🐱", key="new_m_icon")
            new_m_name = col_name.text_input("名稱", placeholder="阿嬤", key="new_m_name")
            if st.form_submit_button("➕ 新增成員"):
                if new_m_name:
                    st.session_state.members.append(f"{new_m_icon.strip()} {new_m_name.strip()}")
                    st.rerun()
        for idx, m in enumerate(st.session_state.members):
            m_col1, m_actions = st.columns([3, 1.8])
            m_col1.write(f"• **{m}**")
            with m_actions:
                act1, act2 = st.columns([1, 1])
                with act1:
                    with st.popover("✏️"):
                        parts = m.split(" ", 1)
                        edit_icon = st.text_input("Icon", value=parts[0] if len(parts)>1 else "🐱", key=f"m_i_{idx}")
                        edit_name = st.text_input("名稱", value=parts[1] if len(parts)>1 else parts[0], key=f"m_n_{idx}")
                        if st.button("儲存", key=f"s_m_{idx}"):
                            st.session_state.members[idx] = f"{edit_icon.strip()} {edit_name.strip()}"
                            st.rerun()
                with act2:
                    if st.button("🗑️", key=f"d_m_{idx}") and len(st.session_state.members) > 1:
                        st.session_state.members.pop(idx)
                        st.rerun()

    with set_col2:
        st.markdown(f"### 🏷️ 支出類別")
        with st.form("add_exp_cat_form", clear_on_submit=True):
            col_icon, col_name = st.columns([1, 2])
            new_e_icon = col_icon.text_input("Icon", value="📦", key="new_e_icon")
            new_e_name = col_name.text_input("類別名稱", placeholder="寵物", key="new_e_name")
            if st.form_submit_button("➕ 新增類別"):
                if new_e_name:
                    st.session_state.expense_categories.append(f"{new_e_icon.strip()} {new_e_name.strip()}")
                    st.rerun()
        for idx, c in enumerate(st.session_state.expense_categories):
            c_col1, c_actions = st.columns([3, 1.8])
            c_col1.write(f"• **{c}**")
            with c_actions:
                act1, act2 = st.columns([1, 1])
                with act1:
                    with st.popover("✏️"):
                        parts = c.split(" ", 1)
                        edit_icon = st.text_input("Icon", value=parts[0] if len(parts)>1 else "📦", key=f"e_i_{idx}")
                        edit_name = st.text_input("名稱", value=parts[1] if len(parts)>1 else parts[0], key=f"e_n_{idx}")
                        if st.button("儲存", key=f"s_e_{idx}"):
                            st.session_state.expense_categories[idx] = f"{edit_icon.strip()} {edit_name.strip()}"
                            st.rerun()
                with act2:
                    if st.button("🗑️", key=f"d_e_{idx}") and len(st.session_state.expense_categories) > 1:
                        st.session_state.expense_categories.pop(idx)
                        st.rerun()

    with set_col3:
        st.markdown(f"### 💰 收入類別")
        with st.form("add_inc_cat_form", clear_on_submit=True):
            col_icon, col_name = st.columns([1, 2])
            new_i_icon = col_icon.text_input("Icon", value="💵", key="new_i_icon")
            new_i_name = col_name.text_input("類別名稱", placeholder="紅包", key="new_i_name")
            if st.form_submit_button("➕ 新增類別"):
                if new_i_name:
                    st.session_state.income_categories.append(f"{new_i_icon.strip()} {new_i_name.strip()}")
                    st.rerun()
        for idx, ic in enumerate(st.session_state.income_categories):
            ic_col1, ic_actions = st.columns([3, 1.8])
            ic_col1.write(f"• **{ic}**")
            with ic_actions:
                act1, act2 = st.columns([1, 1])
                with act1:
                    with st.popover("✏️"):
                        parts = ic.split(" ", 1)
                        edit_icon = st.text_input("Icon", value=parts[0] if len(parts)>1 else "💵", key=f"i_i_{idx}")
                        edit_name = st.text_input("名稱", value=parts[1] if len(parts)>1 else parts[0], key=f"i_n_{idx}")
                        if st.button("儲存", key=f"s_i_{idx}"):
                            st.session_state.income_categories[idx] = f"{edit_icon.strip()} {edit_name.strip()}"
                            st.rerun()
                with act2:
                    if st.button("🗑️", key=f"d_i_{idx}") and len(st.session_state.income_categories) > 1:
                        st.session_state.income_categories.pop(idx)
                        st.rerun()
