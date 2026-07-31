import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar

# ==========================================
# 1. 頁面設定與 Noto Sans TC 美化字體 CSS
# ==========================================
st.set_page_config(
    page_title="小窩記帳 🏠",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 導入 Google Fonts (Noto Sans TC) 並優化樣式
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;800;900&display=swap');

    /* 全局背景與美化字體 */
    html, body, [class*="css"], .stApp {
        font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background-color: #FAF8F5;
        color: #2D241E;
        font-size: 17px !important;
        letter-spacing: 0.2px;
    }
    
    /* 隱藏預設 Streamlit 頂部狀態列與頁尾 */
    header[data-testid="stHeader"] { visibility: hidden; }
    footer { visibility: hidden; }

    /* 頂部 小窩 Banner */
    .cozy-banner {
        background-color: #FFFDF0;
        border: 2px dashed #FDE68A;
        border-radius: 20px;
        padding: 20px 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 22px;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.05);
    }
    .banner-title {
        font-size: 28px !important;
        font-weight: 800;
        color: #EA580C;
        margin: 0;
        letter-spacing: -0.5px;
    }

    /* 白色/奶黃高質感卡片 */
    .white-card {
        background-color: #FFFFFF;
        border: 1.5px solid #FEF3C7;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 4px 16px rgba(245, 158, 11, 0.06);
        margin-bottom: 18px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .white-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.1);
    }
    
    .yellow-card {
        background-color: #FFFBEB;
        border: 2px solid #FDE68A;
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.08);
    }

    /* 結帳明細彙整表格樣式 */
    .settlement-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        font-size: 15px;
        border-radius: 10px;
        overflow: hidden;
    }
    .settlement-table th {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 10px;
        text-align: center;
        font-weight: 700;
    }
    .settlement-table td {
        background-color: #FFFFFF;
        border-bottom: 1px solid #F3F4F6;
        padding: 10px;
        text-align: center;
    }

    /* 分頁 Tabs 圓角選單 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 30px;
        padding: 10px 24px;
        background-color: #FEF3C7;
        color: #B45309;
        font-weight: 700;
        font-size: 17px !important;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EA580C !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(234, 88, 12, 0.35);
    }

    /* 輸入框與按鈕美化 */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input {
        border-radius: 12px !important;
        font-size: 16px !important;
    }
    
    .stButton>button {
        border-radius: 24px;
        background-color: #EA580C;
        color: white;
        border: none;
        font-weight: 700;
        font-size: 16px !important;
        padding: 8px 22px;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #C2410C;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.3);
    }

    /* 📱 RWD 手機版專屬優化 */
    @media (max-width: 768px) {
        html, body, [class*="css"], .stApp { font-size: 15px !important; }
        .cozy-banner { padding: 14px 18px; }
        .banner-title { font-size: 22px !important; }
        .white-card, .yellow-card { padding: 16px; margin-bottom: 12px; }
        
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto;
            white-space: nowrap;
            flex-wrap: nowrap;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 6px 16px;
            font-size: 15px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Session State 初始化 (資料快取與狀態管理)
# ==========================================
if "members" not in st.session_state:
    st.session_state.members = ["鼠", "熊"]

if "expense_categories" not in st.session_state:
    st.session_state.expense_categories = [
        "🍽️ 餐飲美食", "🛋️ 居家日常", "🚗 交通出行", 
        "⚡ 水電瓦斯", "🎬 休閒娛樂", "🏥 醫療健康", "📦 其他"
    ]

if "income_categories" not in st.session_state:
    st.session_state.income_categories = [
        "💰 薪資收入", "🎁 獎金紅包", "📈 投資理財", "🤝 副業兼職", "💵 其他收入"
    ]

# 固定收支規則清單 (Recurring Rules)
if "recurring_rules" not in st.session_state:
    st.session_state.recurring_rules = [
        {
            "id": 1, 
            "type": "支出", 
            "day": 20, 
            "category": "⚡ 水電瓦斯", 
            "item": "每月固定房租/水電費用", 
            "amount": 2000.0, 
            "payer": "鼠", 
            "note": "系統每月20號自動扣款預設"
        }
    ]

if "cal_selected_date" not in st.session_state:
    st.session_state.cal_selected_date = date.today()

if "memos" not in st.session_state:
    st.session_state.memos = [
        {"id": 1, "text": "確認下個月水電費轉帳帳號"},
        {"id": 2, "text": "討論本月採買共同用品預算"}
    ]

if "shopping_list" not in st.session_state:
    st.session_state.shopping_list = [
        {"id": 101, "item": "鮮奶 🥛"},
        {"id": 102, "item": "抽取式衛生紙 🧻"}
    ]

# ==========================================
# 3. 連接 Google Sheets 資料庫與自動產生固定收支
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

# 🔄 自動檢查並產生本月「固定收支」紀錄
def auto_generate_recurring():
    today = date.today()
    curr_y = today.year
    curr_m = today.month
    
    updated = False
    for rule in st.session_state.recurring_rules:
        # 如果今天已經到了或過了當月的固定扣款日
        if today.day >= rule["day"]:
            target_date_str = f"{curr_y}-{curr_m:02d}-{rule['day']:02d}"
            rec_id = f"REC-{rule['id']}-{curr_y}-{curr_m:02d}"
            
            # 檢查是否已經產生過該筆自動紀錄
            if rec_id not in st.session_state.expenses_df["ID"].values:
                new_rec_row = pd.DataFrame([{
                    "ID": rec_id,
                    "日期": target_date_str,
                    "類型": rule["type"],
                    "類別": rule["category"],
                    "項目": f"🔄 [固定{rule['type']}] {rule['item']}",
                    "金額": float(rule["amount"]),
                    "記帳人": rule["payer"],
                    "備註": rule["note"],
                    "結帳狀態": "未結帳",
                    "結帳單號": "",
                    "已同意人": ""
                }])
                st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_rec_row], ignore_index=True)
                updated = True
                
    if updated:
        try:
            conn.update(data=st.session_state.expenses_df)
        except Exception:
            pass

auto_generate_recurring()

# ==========================================
# 4. 主選單 Header
# ==========================================
head_col1, head_col2 = st.columns([1.5, 2])
with head_col1:
    st.markdown("### 🏠 小窩記帳 <span style='font-size:13px; background:#FEF3C7; color:#B45309; padding:4px 14px; border-radius:20px; font-weight:bold;'>🏡 Our Cozy Home</span>", unsafe_allow_html=True)

tab_dash, tab_memo, tab_shopping, tab_settings = st.tabs(["🏠 記帳儀表板", "💬 備忘錄", "🛒 購買清單", "⚙️ 設定"])

# ==========================================
# TAB 1: 🏠 記帳儀表板 (含結帳總表與帳戶餘額)
# ==========================================
with tab_dash:
    st.markdown("""
    <div class="cozy-banner">
        <div class="banner-title">Happiness is keeping track together! 🏠</div>
        <div style="font-size: 38px;">🏡</div>
    </div>
    """, unsafe_allow_html=True)

    # 工具列：搜尋列 + 🔴 登記支出 + 🟢 登記收入 + 🤝 進行結帳
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([2.5, 1.2, 1.2, 1.3])
    
    with btn_col1:
        search_kw = st.text_input("搜尋", placeholder="🔍 搜尋描述、分類或付款人...", label_visibility="collapsed")
        
    # 🔴 登記支出
    with btn_col2:
        with st.popover("🔴 登記支出", use_container_width=True):
            st.markdown("### 🔴 新增支出筆數")
            with st.form("add_expense_form", clear_on_submit=True):
                e_date = st.date_input("支出日期", datetime.now())
                e_payer = st.selectbox("付款人", st.session_state.members)
                e_cat = st.selectbox("支出分類", st.session_state.expense_categories)
                e_item = st.text_input("消費項目 (非必填)", placeholder="例如：全聯採買食材")
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
                    st.success("🎉 支出新增成功！")
                    st.rerun()

    # 🟢 登記收入
    with btn_col3:
        with st.popover("🟢 登記收入", use_container_width=True):
            st.markdown("### 🟢 新增收入筆數")
            with st.form("add_income_form", clear_on_submit=True):
                i_date = st.date_input("收入日期", datetime.now())
                i_receiver = st.selectbox("收款人", st.session_state.members)
                i_cat = st.selectbox("收入分類", st.session_state.income_categories)
                i_item = st.text_input("收入項目 (非必填)", placeholder="例如：7月薪資發放")
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
                    st.success("🎉 收入新增成功！")
                    st.rerun()

    # 🤝 進行結帳 (含表格與帳戶餘額)
    with btn_col4:
        with st.popover("🤝 進行結帳", use_container_width=True):
            st.markdown("### 🤝 進行結帳審核專區")
            current_unsettled = st.session_state.expenses_df[st.session_state.expenses_df["結帳狀態"] != "已結帳"].copy()
            
            if current_unsettled.empty:
                st.info("目前沒有待結帳的筆數。")
            else:
                settle_mode = st.radio("選擇結帳範圍", ["全部未結帳", "以月為單位", "日期到日期"], horizontal=True)
                current_unsettled["日期_dt"] = pd.to_datetime(current_unsettled["日期"])
                
                if settle_mode == "以月為單位":
                    col_y, col_m = st.columns(2)
                    cur_y = col_y.number_input("年份", min_value=2020, max_value=2030, value=datetime.now().year)
                    cur_m = col_m.selectbox("月份", list(range(1, 13)), index=datetime.now().month - 1)
                    to_settle_df = current_unsettled[
                        (current_unsettled["日期_dt"].dt.year == cur_y) & 
                        (current_unsettled["日期_dt"].dt.month == cur_m)
                    ]
                elif settle_mode == "日期到日期":
                    col_d1, col_d2 = st.columns(2)
                    s_date = col_d1.date_input("開始日期", datetime.now())
                    e_date = col_d2.date_input("結束日期", datetime.now())
                    to_settle_df = current_unsettled[
                        (current_unsettled["日期_dt"].dt.date >= s_date) & 
                        (current_unsettled["日期_dt"].dt.date <= e_date)
                    ]
                else:
                    to_settle_df = current_unsettled.copy()
                    
                st.write(f"📌 選定區間包含 **{len(to_settle_df)}** 筆待結帳項目")
                
                # AA 拆帳計算
                if len(st.session_state.members) >= 2 and not to_settle_df.empty:
                    m1, m2 = st.session_state.members[0], st.session_state.members[1]
                    p1_exp = to_settle_df[(to_settle_df["記帳人"] == m1) & (to_settle_df["類型"] == "支出")]["金額"].sum()
                    p2_exp = to_settle_df[(to_settle_df["記帳人"] == m2) & (to_settle_df["類型"] == "支出")]["金額"].sum()
                    diff = (p1_exp - p2_exp) / 2
                    
                    if diff > 0:
                        transfer_text = f"<b>{m2}</b> ➔ <b>{m1}</b>"
                        transfer_amt = abs(diff)
                    else:
                        transfer_text = f"<b>{m1}</b> ➔ <b>{m2}</b>"
                        transfer_amt = abs(diff)

                    st.markdown(f"<div style='font-size:16px; margin:8px 0;'>拆帳補貼：{transfer_text} <b style='color:#D97706; font-size:18px;'>$ {transfer_amt:,.2f}</b></div>", unsafe_allow_html=True)

                # 全員同意核對
                st.markdown("<div style='font-size:14px; font-weight:700; color:#B45309; margin-top:8px;'>請全員勾選確認同意：</div>", unsafe_allow_html=True)
                chk_cols = st.columns(len(st.session_state.members))
                agreed_flags = []
                for idx, member in enumerate(st.session_state.members):
                    is_chk = chk_cols[idx].checkbox(f"👤 {member}", key=f"settle_pop_agree_{member}")
                    agreed_flags.append(is_chk)
                
                all_agreed = all(agreed_flags) and len(agreed_flags) > 0

                # ------------------------------------------
                # 📊 需求 1：結帳最下方表格 (帳戶餘額、個別總支出、總收入)
                # ------------------------------------------
                st.divider()
                st.markdown("#### 📋 本期結帳收支彙整總表")
                
                summary_rows = []
                s_tot_inc = 0.0
                s_tot_exp = 0.0
                
                for m in st.session_state.members:
                    m_inc = to_settle_df[(to_settle_df["記帳人"] == m) & (to_settle_df["類型"] == "收入")]["金額"].sum()
                    m_exp = to_settle_df[(to_settle_df["記帳人"] == m) & (to_settle_df["類型"] == "支出")]["金額"].sum()
                    m_net = m_inc - m_exp
                    summary_rows.append({
                        "成員": f"👤 {m}",
                        "總收入": f"+${m_inc:,.2f}",
                        "總支出": f"-${m_exp:,.2f}",
                        "個人淨結餘": f"${m_net:,.2f}"
                    })
                    s_tot_inc += m_inc
                    s_tot_exp += m_exp

                s_balance = s_tot_inc - s_tot_exp

                # 繪製表格
                st.table(pd.DataFrame(summary_rows))
                
                st.markdown(f"""
                <div style="background:#FFFDF0; border:1.5px solid #FDE68A; padding:12px 18px; border-radius:12px; text-align:center; margin-bottom:12px;">
                    <span style="font-size:15px; color:#78350F; font-weight:700;">🏦 選定區間帳戶總餘額：</span>
                    <span style="font-size:22px; color:{'#059669' if s_balance >= 0 else '#DC2626'}; font-weight:900;">$ {s_balance:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)

                if st.button("🤝 完成結帳", use_container_width=True, disabled=(not all_agreed or len(to_settle_df) == 0)):
                    settle_id = f"SETTLE-{datetime.now().strftime('%Y%m%d%H%M')}"
                    indices = to_settle_df.index
                    st.session_state.expenses_df.loc[indices, "結帳狀態"] = "已結帳"
                    st.session_state.expenses_df.loc[indices, "結帳單號"] = settle_id
                    st.session_state.expenses_df.loc[indices, "已同意人"] = ",".join(st.session_state.members)
                    try:
                        conn.update(data=st.session_state.expenses_df)
                    except Exception:
                        pass
                    st.success("🎉 全員同意！已完成結帳作業！")
                    st.rerun()

    # 數據過濾
    current_df = st.session_state.expenses_df.copy()
    if search_kw:
        current_df = current_df[
            current_df["項目"].str.contains(search_kw, na=False) |
            current_df["類別"].str.contains(search_kw, na=False) |
            current_df["記帳人"].str.contains(search_kw, na=False)
        ]

    # 頂部關鍵數據列
    total_income = current_df[current_df["類型"] == "收入"]["金額"].sum()
    total_expense = current_df[current_df["類型"] == "支出"]["金額"].sum()
    net_balance = total_income - total_expense

    card_col1, card_col2, card_col3 = st.columns(3)

    with card_col1:
        st.markdown(f"""
        <div class="white-card">
            <div style="color:#059669; font-weight:700; font-size:16px;">🟢 累積總收入</div>
            <div style="color:#059669; font-size:32px; font-weight:900; margin:6px 0;">+ $ {total_income:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with card_col2:
        st.markdown(f"""
        <div class="white-card">
            <div style="color:#EA580C; font-weight:700; font-size:16px;">🔴 累積總支出</div>
            <div style="color:#EA580C; font-size:32px; font-weight:900; margin:6px 0;">- $ {total_expense:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with card_col3:
        balance_color = "#059669" if net_balance >= 0 else "#DC2626"
        st.markdown(f"""
        <div class="white-card">
            <div style="color:#4A3B32; font-weight:700; font-size:16px;">💵 帳戶總餘額</div>
            <div style="color:{balance_color}; font-size:32px; font-weight:900; margin:6px 0;">$ {net_balance:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    # 📅 日曆檢視區塊
    st.markdown("""
    <div style="font-weight:800; font-size:20px; color:#4A3B32; margin:16px 0 10px 0;">
        📅 日曆檢視 (點擊選擇日期看當日收支)
    </div>
    """, unsafe_allow_html=True)

    cal_year_col, cal_month_col, cal_pick_col = st.columns([1.5, 1.5, 3])
    with cal_year_col:
        sel_year = st.number_input("年份 ", min_value=2020, max_value=2030, value=st.session_state.cal_selected_date.year, label_visibility="collapsed")
    with cal_month_col:
        sel_month = st.selectbox("月份 ", list(range(1, 13)), index=st.session_state.cal_selected_date.month - 1, label_visibility="collapsed")
    with cal_pick_col:
        picked_date = st.date_input("直接選擇日期", value=st.session_state.cal_selected_date, label_visibility="collapsed")
        st.session_state.cal_selected_date = picked_date

    # 繪製月曆
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(int(sel_year), int(sel_month))

    week_cols = st.columns(7)
    week_names = ["一", "二", "三", "四", "五", "六", "日"]
    for idx, name in enumerate(week_names):
        week_cols[idx].markdown(f"<div style='text-align:center; font-weight:bold; color:#B45309;'>{name}</div>", unsafe_allow_html=True)

    df_month = current_df.copy()
    if not df_month.empty:
        df_month["日期_dt"] = pd.to_datetime(df_month["日期"]).dt.date
    else:
        df_month["日期_dt"] = None

    for week in month_days:
        w_cols = st.columns(7)
        for day_idx, day_num in enumerate(week):
            if day_num == 0:
                w_cols[day_idx].write("")
            else:
                curr_d = date(int(sel_year), int(sel_month), day_num)
                d_records = df_month[df_month["日期_dt"] == curr_d]
                
                day_inc = d_records[d_records["類型"] == "收入"]["金額"].sum()
                day_exp = d_records[d_records["類型"] == "支出"]["金額"].sum()
                
                label_text = f"{day_num}日"
                if day_inc > 0 or day_exp > 0:
                    label_text += " •"

                if w_cols[day_idx].button(label_text, key=f"cal_btn_{curr_d}"):
                    st.session_state.cal_selected_date = curr_d
                    st.rerun()

    # 顯示選定日期的詳細收支
    selected_d_str = str(st.session_state.cal_selected_date)
    st.markdown(f"#### 📌 當日收支明細：`{selected_d_str}`")

    daily_df = current_df[current_df["日期"] == selected_d_str]

    if daily_df.empty:
        st.info(f"該日期 ({selected_d_str}) 尚無任何收支紀錄。")
    else:
        d_col1, d_col2 = st.columns(2)
        d_col1.metric("當日總收入", f"+ ${daily_df[daily_df['類型'] == '收入']['金額'].sum():,.2f}")
        d_col2.metric("當日總支出", f"- ${daily_df[daily_df['類型'] == '支出']['金額'].sum():,.2f}")

        st.dataframe(
            daily_df[["類型", "類別", "項目", "金額", "記帳人", "結帳狀態", "備註"]],
            use_container_width=True,
            hide_index=True
        )

    # 圖表
    st.divider()
    chart_col1, chart_col2 = st.columns([1, 1.5])
    
    with chart_col1:
        st.markdown("##### 🍕 支出類別比例")
        exp_df = current_df[current_df["類型"] == "支出"]
        if not exp_df.empty:
            fig_pie = px.pie(
                exp_df, names="類別", values="金額", hole=0.45,
                color_discrete_sequence=["#EA580C", "#D97706", "#10B981", "#F59E0B", "#8B5CF6"]
            )
            fig_pie.update_traces(textfont=dict(size=16), textinfo='percent+label')
            fig_pie.update_layout(font=dict(size=15), showlegend=True, margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.markdown("##### 📊 時間支出趨勢圖")
        exp_df = current_df[current_df["類型"] == "支出"]
        if not exp_df.empty:
            exp_df["日期_dt"] = pd.to_datetime(exp_df["日期"])
            daily_sum = exp_df.groupby(exp_df["日期_dt"].dt.day)["金額"].sum().reset_index()
            
            fig_bar = px.bar(
                daily_sum, x="日期_dt", y="金額", color_discrete_sequence=["#D97706"], text_auto=',.0f'
            )
            fig_bar.update_traces(textfont=dict(size=16), textposition='outside')
            fig_bar.update_layout(
                font=dict(size=15),
                xaxis=dict(title=dict(text="日期 (日)", font=dict(size=15))),
                yaxis=dict(title=dict(text="金額 ($)", font=dict(size=15))),
                margin=dict(t=30, b=10, l=10, r=10),
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# TAB 2: 💬 備忘錄
# ==========================================
with tab_memo:
    st.subheader("💬 家族備忘錄")
    st.divider()

    with st.form("add_memo_form", clear_on_submit=True):
        col_m1, col_m2 = st.columns([4, 1])
        new_memo_text = col_m1.text_input("輸入備忘事項", placeholder="輸入需要討論的事項...", label_visibility="collapsed")
        submit_memo = col_m2.form_submit_button("➕ 新增事項")
        if submit_memo and new_memo_text:
            new_id = int(datetime.now().timestamp() * 1000)
            st.session_state.memos.append({"id": new_id, "text": new_memo_text})
            st.success("已新增備忘事項！")
            st.rerun()

    st.markdown("#### 📌 待處理備忘事項：")
    if not st.session_state.memos:
        st.info("目前沒有待處理的備忘事項。")
    else:
        for memo in list(st.session_state.memos):
            col_chk, col_txt, col_edit = st.columns([0.6, 4, 1])
            checked = col_chk.checkbox("", key=f"memo_chk_{memo['id']}")
            if checked:
                st.session_state.memos.remove(memo)
                st.toast("✅ 備忘事項已完成並刪除！")
                st.rerun()
            
            col_txt.markdown(f"<div style='font-size:18px; padding-top:4px;'>• {memo['text']}</div>", unsafe_allow_html=True)
            
            with col_edit.popover("✏️ 編輯"):
                edited_text = st.text_input("修改備忘內容", value=memo["text"], key=f"edit_memo_input_{memo['id']}")
                if st.button("儲存修改", key=f"save_memo_{memo['id']}"):
                    memo["text"] = edited_text
                    st.toast("修改成功！")
                    st.rerun()

# ==========================================
# TAB 3: 🛒 購買清單
# ==========================================
with tab_shopping:
    st.subheader("🛒 待買清單")
    st.divider()

    with st.form("add_shop_form", clear_on_submit=True):
        col_s1, col_s2 = st.columns([4, 1])
        new_shop_item = col_s1.text_input("輸入待買商品", placeholder="輸入要購買的物品...", label_visibility="collapsed")
        submit_shop = col_s2.form_submit_button("➕ 新增商品")
        if submit_shop and new_shop_item:
            new_id = int(datetime.now().timestamp() * 1000)
            st.session_state.shopping_list.append({"id": new_id, "item": new_shop_item})
            st.success("已新增待買商品！")
            st.rerun()

    st.markdown("#### 🛒 待採買項目：")
    if not st.session_state.shopping_list:
        st.info("目前清單是空的，沒有待買物品。")
    else:
        for shop_item in list(st.session_state.shopping_list):
            col_chk, col_txt, col_edit = st.columns([0.6, 4, 1])
            checked = col_chk.checkbox("", key=f"shop_chk_{shop_item['id']}")
            if checked:
                st.session_state.shopping_list.remove(shop_item)
                st.toast("🎉 已採買完成並自清單移除！")
                st.rerun()
            
            col_txt.markdown(f"<div style='font-size:18px; padding-top:4px;'>🛒 {shop_item['item']}</div>", unsafe_allow_html=True)
            
            with col_edit.popover("✏️ 編輯"):
                edited_item = st.text_input("修改商品名稱", value=shop_item["item"], key=f"edit_shop_input_{shop_item['id']}")
                if st.button("儲存修改", key=f"save_shop_{shop_item['id']}"):
                    shop_item["item"] = edited_item
                    st.toast("修改成功！")
                    st.rerun()

# ==========================================
# TAB 4: ⚙️ 設定 (新增：🔄 固定收支設定)
# ==========================================
with tab_settings:
    st.subheader("⚙️ 系統設定與固定收支管理")
    st.divider()

    # ------------------------------------------
    # 🔄 需求 3：固定支出/收入設定專區
    # ------------------------------------------
    st.markdown("### 🔄 固定收支管理 (每月自動扣款/入帳)")
    st.caption("設定後，系統每月到達指定扣款日，會自動在背景產生對應的記帳紀錄。")

    with st.form("add_recurring_form", clear_on_submit=True):
        r_type = st.radio("收支類型", ["支出", "收入"], horizontal=True)
        r_col1, r_col2, r_col3 = st.columns(3)
        
        r_day = r_col1.number_input("每月固定幾號 (1~31 日)", min_value=1, max_value=31, value=20)
        r_payer = r_col2.selectbox("責任/付款人", st.session_state.members, key="rec_payer_select")
        
        cats = st.session_state.expense_categories if r_type == "支出" else st.session_state.income_categories
        r_cat = r_col3.selectbox("分類", cats, key="rec_cat_select")
        
        r_item = st.text_input("固定項目名稱", placeholder="例如：每月房租、水電費、薪資")
        r_amount = st.number_input("固定金額 ($)", min_value=1.0, value=2000.0, step=100.0)
        r_note = st.text_input("備註說明", placeholder="選填")
        
        if st.form_submit_button("➕ 新增固定收支規則"):
            if r_item:
                new_rule_id = int(datetime.now().timestamp())
                st.session_state.recurring_rules.append({
                    "id": new_rule_id,
                    "type": r_type,
                    "day": r_day,
                    "category": r_cat,
                    "item": r_item,
                    "amount": r_amount,
                    "payer": r_payer,
                    "note": r_note
                })
                auto_generate_recurring()
                st.success("🎉 成功新增固定收支設定！")
                st.rerun()

    st.markdown("#### 📋 現有固定收支規則：")
    if not st.session_state.recurring_rules:
        st.info("目前無任何固定收支設定。")
    else:
        for rule in list(st.session_state.recurring_rules):
            r_c1, r_c2 = st.columns([4, 1])
            type_color = "#EA580C" if rule["type"] == "支出" else "#059669"
            r_c1.markdown(f"""
            <div style="background:#FFFDF0; border:1px solid #FDE68A; padding:10px 14px; border-radius:12px; margin-bottom:8px;">
                <b>每月 {rule['day']} 號</b> | <span style="color:{type_color}; font-weight:700;">[{rule['type']}]</span> {rule['item']} - <b>${rule['amount']:,.0f}</b> ({rule['payer']})
            </div>
            """, unsafe_allow_html=True)
            
            if r_c2.button("刪除", key=f"del_rec_{rule['id']}"):
                st.session_state.recurring_rules.remove(rule)
                st.rerun()

    st.divider()

    # 基礎成員與類別設定
    set_col1, set_col2, set_col3 = st.columns(3)

    # 成員管理
    with set_col1:
        st.markdown(f"### 👥 成員管理 (`{len(st.session_state.members)}` / 30 人)")
        with st.form("add_member_form", clear_on_submit=True):
            new_mem = st.text_input("新增成員名稱", placeholder="例如：阿嬤、小明")
            if st.form_submit_button("➕ 新增成員"):
                if len(st.session_state.members) >= 30:
                    st.error("已達上限 30 人！")
                elif new_mem and new_mem not in st.session_state.members:
                    st.session_state.members.append(new_mem)
                    st.success(f"已新增成員：{new_mem}")
                    st.rerun()

        for idx, m in enumerate(st.session_state.members):
            m_col1, m_col2 = st.columns([3, 1])
            m_col1.write(f"{idx+1}. **{m}**")
            if m_col2.button("刪除", key=f"del_mem_{m}"):
                if len(st.session_state.members) <= 1:
                    st.error("至少需保留 1 位成員！")
                else:
                    st.session_state.members.remove(m)
                    st.rerun()

    # 支出類別管理
    with set_col2:
        st.markdown(f"### 🏷️ 支出類別 (`{len(st.session_state.expense_categories)}` / 30 項)")
        with st.form("add_exp_cat_form", clear_on_submit=True):
            new_e_cat = st.text_input("新增支出類別", placeholder="例如：🐶 寵物費用")
            if st.form_submit_button("➕ 新增支出類別"):
                if len(st.session_state.expense_categories) >= 30:
                    st.error("已達上限 30 項！")
                elif new_e_cat and new_e_cat not in st.session_state.expense_categories:
                    st.session_state.expense_categories.append(new_e_cat)
                    st.success(f"已新增支出類別：{new_e_cat}")
                    st.rerun()

        for idx, c in enumerate(st.session_state.expense_categories):
            c_col1, c_col2 = st.columns([3, 1])
            c_col1.write(f"{idx+1}. **{c}**")
            if c_col2.button("刪除", key=f"del_exp_cat_{c}"):
                if len(st.session_state.expense_categories) <= 1:
                    st.error("至少需保留 1 個類別！")
                else:
                    st.session_state.expense_categories.remove(c)
                    st.rerun()

    # 收入類別管理
    with set_col3:
        st.markdown(f"### 💰 收入類別 (`{len(st.session_state.income_categories)}` / 10 項)")
        with st.form("add_inc_cat_form", clear_on_submit=True):
            new_i_cat = st.text_input("新增收入類別", placeholder="例如：🧧 壓歲紅包")
            if st.form_submit_button("➕ 新增收入類別"):
                if len(st.session_state.income_categories) >= 10:
                    st.error("已達上限 10 項！")
                elif new_i_cat and new_i_cat not in st.session_state.income_categories:
                    st.session_state.income_categories.append(new_i_cat)
                    st.success(f"已新增收入類別：{new_i_cat}")
                    st.rerun()

        for idx, ic in enumerate(st.session_state.income_categories):
            ic_col1, ic_col2 = st.columns([3, 1])
            ic_col1.write(f"{idx+1}. **{ic}**")
            if ic_col2.button("刪除", key=f"del_inc_cat_{ic}"):
                if len(st.session_state.income_categories) <= 1:
                    st.error("至少需保留 1 個類別！")
                else:
                    st.session_state.income_categories.remove(ic)
                    st.rerun()