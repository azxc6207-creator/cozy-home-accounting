import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar

# ==========================================
# 1. 頁面設定與「莫蘭迪多色塊 + 狗狗腳印」CSS
# ==========================================
st.set_page_config(
    page_title="小窩記帳 🏠",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 注入多樣化不規則色塊 + 半透明狗狗腳印 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;800;900&display=swap');

    /* 🎨 多樣化色塊背景 (結合附圖色調) + 🐾 半透明狗狗腳印 SVG 紋理 */
    html, body, [class*="css"], .stApp {
        font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background-color: #FAF5F0 !important;
        background-image: 
            /* 1. 半透明狗狗腳印花紋 */
            url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="%23A07855" opacity="0.06"><path d="M12,11.5 C10.6,11.5 9.5,12.6 9.5,14 C9.5,15.4 10.6,17.5 12,17.5 C13.4,17.5 14.5,15.4 14.5,14 C14.5,12.6 13.4,11.5 12,11.5 Z M7.5,12 C8.3,12 9,11.3 9,10.5 C9,9.7 8.3,9 7.5,9 C6.7,9 6,9.7 6,10.5 C6,11.3 6.7,12 7.5,12 Z M16.5,12 C17.3,12 18,11.3 18,10.5 C18,9.7 17.3,9 16.5,9 C15.7,9 15,9.7 15,10.5 C15,11.3 15.7,12 16.5,12 Z M9.5,8 C10.3,8 11,7.3 11,6.5 C11,5.7 10.3,5 9.5,5 C8.7,5 8,5.7 8,6.5 C8,7.3 8.7,8 9.5,8 Z M14.5,8 C15.3,8 16,7.3 16,6.5 C16,5.7 15.3,5 14.5,5 C13.7,5 13,5.7 13,6.5 C13,7.3 13.7,8 14.5,8 Z"/></svg>'),
            /* 2. 模仿附圖的不規則多色斑塊 */
            radial-gradient(circle at 10% 15%, rgba(232, 221, 208, 0.85) 0%, transparent 45%),
            radial-gradient(circle at 85% 10%, rgba(212, 195, 179, 0.75) 0%, transparent 40%),
            radial-gradient(circle at 25% 65%, rgba(242, 232, 223, 0.9) 0%, transparent 50%),
            radial-gradient(circle at 80% 85%, rgba(180, 145, 115, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 50% 40%, rgba(255, 255, 255, 0.6) 0%, transparent 60%) !important;
        background-attachment: fixed !important;
        color: #3D322C !important;
        font-size: 16px !important;
    }
    
    header[data-testid="stHeader"] { visibility: hidden; }
    footer { visibility: hidden; }

    /* 📱 需求 1：直式日期按鈕列表樣式 */
    .vertical-date-btn button {
        width: 100% !important;
        background-color: #FFFFFF !important;
        color: #5C4A3E !important;
        border: 1px solid #E2D5C5 !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        margin-bottom: 4px !important;
        box-shadow: 0 2px 6px rgba(160, 120, 85, 0.05) !important;
        display: flex !important;
        justify-content: space-between !important;
    }
    .vertical-date-btn button:hover {
        background-color: #A07855 !important;
        color: #FFFFFF !important;
        border-color: #A07855 !important;
    }

    /* 🍵 淺奶茶色三大功能區塊 */
    .action-block div[data-testid="column"] .stPopover>button {
        width: 100% !important;
        background-color: #EEDFD2 !important;
        color: #5C4A3E !important;
        border: 1.5px solid #D4C3B3 !important;
        border-radius: 14px !important;
        padding: 10px 4px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        box-shadow: 0 2px 8px rgba(160, 120, 85, 0.08) !important;
    }

    /* 流水帳卡片樣式 */
    .item-title { font-size: 17px; font-weight: 800; color: #3D322C; }
    .item-amount { font-size: 19px; font-weight: 900; color: #8C6239; text-align: right; }
    .badge-tag {
        background-color: #EEDFD2; color: #7A573C;
        font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: 700;
    }
    .sub-info { font-size: 13px; color: #8C7A6B; margin-top: 2px; }

    /* 分頁 Tabs 導覽列 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #E8DDD0;
        padding: 4px;
        border-radius: 25px;
        margin-bottom: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 18px;
        padding: 6px 14px;
        color: #6E5A4C;
        font-weight: 700;
        font-size: 14px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #A07855 !important;
        color: #FFFFFF !important;
    }

    /* 普通按鈕樣式 */
    .stButton>button {
        border-radius: 16px;
        background-color: #A07855;
        color: white; border: none;
        font-weight: 700; font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Session State 初始化
# ==========================================
if "members" not in st.session_state:
    st.session_state.members = ["鼠", "熊"]

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
st.markdown("<h3 style='color:#7A573C; font-weight:800; margin-bottom:8px;'>🏠 小窩記帳 🐾</h3>", unsafe_allow_html=True)

tab_home, tab_charts, tab_memo, tab_shopping, tab_settings = st.tabs([
    "🏠 主頁記帳", "📊 統計圖表", "💬 備忘錄", "🛒 購物清單", "⚙️ 設定"
])

# ==========================================
# TAB 1: 🏠 主頁記帳 (直式日期選擇 + 無金額 + 腳印斑塊背景)
# ==========================================
with tab_home:
    # 📌 月份與年份選擇
    cal_m_col1, cal_m_col2 = st.columns([1, 1])
    sel_year = cal_m_col1.number_input("年份", min_value=2020, max_value=2030, value=st.session_state.cal_selected_date.year, label_visibility="collapsed")
    sel_month = cal_m_col2.selectbox("月份", list(range(1, 13)), index=st.session_state.cal_selected_date.month - 1, label_visibility="collapsed")

    # 📌 需求 1 & 2：手機直式日期編排，且隱藏金額
    st.markdown("##### 📅 請選擇日期 (直式滑動視窗)：")
    
    cal = calendar.Calendar(firstweekday=0)
    month_days_flat = [d for week in cal.monthdayscalendar(int(sel_year), int(sel_month)) for d in week if d != 0]
    week_days_tw = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]

    # 採用手風琴 (Expander) 收納直式日期列表，保持主頁乾淨
    with st.expander(f"📅 展開 {sel_year}年{sel_month}月 直式日期選單", expanded=False):
        # 以每行 2 列的直式卡片堆疊呈現，適合手機垂直閱讀
        d_cols = st.columns(2)
        for idx, day_num in enumerate(month_days_flat):
            curr_d = date(int(sel_year), int(sel_month), day_num)
            w_str = week_days_tw[curr_d.weekday()]
            
            # 純日期標示，不含金額
            date_label = f"📅 {sel_month}月{day_num}日 ({w_str})"
            
            col_target = d_cols[idx % 2]
            with col_target:
                st.markdown("<div class='vertical-date-btn'>", unsafe_allow_html=True)
                if st.button(date_label, key=f"v_date_btn_{curr_d}", use_container_width=True):
                    st.session_state.cal_selected_date = curr_d
                    st.session_state.filter_to_single_day = True
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # 🍵 三大淺奶茶色功能按鈕並排
    st.markdown("<div class='action-block'>", unsafe_allow_html=True)
    top_col1, top_col2, top_col3 = st.columns(3)
    
    with top_col1:
        with st.popover("🔴 登記支出", use_container_width=True):
            st.markdown("### 🔴 新增支出筆數")
            with st.form("add_exp_form", clear_on_submit=True):
                e_date = st.date_input("支出日期", datetime.now())
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
        with st.popover("🟢 登記收入", use_container_width=True):
            st.markdown("### 🟢 新增收入筆數")
            with st.form("add_inc_form", clear_on_submit=True):
                i_date = st.date_input("收入日期", datetime.now())
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
        with st.popover("🤝 進行結帳", use_container_width=True):
            st.markdown("### 🤝 結帳專區")
            unsettled_df = st.session_state.expenses_df[st.session_state.expenses_df["結帳狀態"] != "已結帳"].copy()
            if unsettled_df.empty:
                st.info("目前沒有待結帳筆數。")
            else:
                st.write(f"待結帳總筆數：**{len(unsettled_df)}** 筆")
                st.markdown("請全員勾選確認同意：")
                chk_cols = st.columns(len(st.session_state.members))
                agreed_flags = [chk_cols[i].checkbox(f"👤 {m}", key=f"settle_chk_{m}") for i, m in enumerate(st.session_state.members)]
                
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

    # 檢視狀態說明
    list_header_col1, list_header_col2 = st.columns([3, 1])
    if st.session_state.filter_to_single_day:
        list_header_col1.markdown(f"#### 📅 正在檢視單日：`{st.session_state.cal_selected_date}`")
        if list_header_col2.button("↺ 看全月紀錄"):
            st.session_state.filter_to_single_day = False
            st.rerun()
    else:
        list_header_col1.markdown(f"#### 📅 本月全月收支紀錄 ({sel_year}年{sel_month}月)")

    # 數據篩選
    df_current = st.session_state.expenses_df.copy()
    if not df_current.empty:
        df_current["日期_dt"] = pd.to_datetime(df_current["日期"]).dt.date
        if st.session_state.filter_to_single_day:
            filtered_df = df_current[df_current["日期_dt"] == st.session_state.cal_selected_date]
        else:
            filtered_df = df_current[
                (df_current["日期_dt"].apply(lambda d: d.year if d else 0) == int(sel_year)) &
                (df_current["日期_dt"].apply(lambda d: d.month if d else 0) == int(sel_month))
            ]
    else:
        filtered_df = pd.DataFrame()

    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values(by="日期", ascending=False)

    # 逐條收支卡片
    if filtered_df.empty:
        st.info("此區間內尚無任何收支紀錄。")
    else:
        for idx, row in filtered_df.iterrows():
            r_date = datetime.strptime(row["日期"], "%Y-%m-%d")
            day_week_str = week_days_tw[r_date.weekday()]
            
            c_card1, c_card2, c_edit, c_del = st.columns([3, 2, 0.8, 0.8])
            
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
                st.markdown(f"<div class='item-amount' style='color:{amt_color};'>{amt_prefix}{row['金額']:,.0f} 元</div>", unsafe_allow_html=True)
            
            with c_edit:
                with st.popover("✏️"):
                    st.markdown("### ✏️ 編輯這筆紀錄")
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

            with c_del:
                if st.button("🗑️", key=f"del_btn_{row['ID']}"):
                    st.session_state.expenses_df = st.session_state.expenses_df[st.session_state.expenses_df["ID"] != row["ID"]]
                    try:
                        conn.update(data=st.session_state.expenses_df)
                    except Exception:
                        pass
                    st.toast("🗑️ 已成功刪除紀錄！")
                    st.rerun()
            st.divider()

# ==========================================
# TAB 2: 📊 統計圖表 (置中 + 移除工具列)
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
            fig_pie.update_traces(textfont=dict(size=15), textinfo='percent+label')
            fig_pie.update_layout(
                font=dict(size=14), 
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
            fig_bar.update_traces(textfont=dict(size=15), textposition='outside')
            fig_bar.update_layout(
                font=dict(size=14),
                xaxis=dict(title=dict(text="日期 (日)", font=dict(size=14))),
                yaxis=dict(title=dict(text="金額 ($)", font=dict(size=14))),
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
        col_chk, col_txt, col_edit = st.columns([0.8, 5, 1])
        with col_chk:
            checked = st.checkbox("", key=f"memo_chk_{memo['id']}")
            if checked:
                st.session_state.memos.remove(memo)
                st.toast("✅ 已完成並刪除！")
                st.rerun()
        with col_txt:
            st.markdown(f"<div style='font-size:16px; padding-top:4px;'>• {memo['text']}</div>", unsafe_allow_html=True)
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
        col_chk, col_txt, col_edit = st.columns([0.8, 5, 1])
        with col_chk:
            checked = st.checkbox("", key=f"shop_chk_{shop_item['id']}")
            if checked:
                st.session_state.shopping_list.remove(shop_item)
                st.toast("🎉 已採買完成並移除！")
                st.rerun()
        with col_txt:
            st.markdown(f"<div style='font-size:16px; padding-top:4px;'>🛒 {shop_item['item']}</div>", unsafe_allow_html=True)
        with col_edit:
            with st.popover("✏️"):
                edited_item = st.text_input("修改商品名稱", value=shop_item["item"], key=f"edit_shop_input_{shop_item['id']}")
                if st.button("儲存修改", key=f"save_shop_{shop_item['id']}"):
                    shop_item["item"] = edited_item
                    st.toast("修改成功！")
                    st.rerun()
        st.divider()

# ==========================================
# TAB 5: ⚙️ 設定
# ==========================================
with tab_settings:
    st.subheader("⚙️ 成員與類別設定")
    st.divider()

    set_col1, set_col2, set_col3 = st.columns(3)

    with set_col1:
        st.markdown(f"### 👥 成員管理 (`{len(st.session_state.members)}` / 30 人)")
        with st.form("add_member_form", clear_on_submit=True):
            new_mem = st.text_input("新增成員名稱", placeholder="例如：阿嬤")
            if st.form_submit_button("➕ 新增"):
                if len(st.session_state.members) < 30 and new_mem:
                    st.session_state.members.append(new_mem)
                    st.rerun()

        for m in st.session_state.members:
            m_col1, m_col2 = st.columns([3, 1])
            m_col1.write(f"• **{m}**")
            if m_col2.button("刪除", key=f"del_mem_{m}"):
                if len(st.session_state.members) > 1:
                    st.session_state.members.remove(m)
                    st.rerun()

    with set_col2:
        st.markdown(f"### 🏷️ 支出類別 (`{len(st.session_state.expense_categories)}` / 30 項)")
        with st.form("add_exp_cat_form", clear_on_submit=True):
            new_e_cat = st.text_input("新增支出類別", placeholder="例如：寵物費用")
            if st.form_submit_button("➕ 新增"):
                if len(st.session_state.expense_categories) < 30 and new_e_cat:
                    st.session_state.expense_categories.append(new_e_cat)
                    st.rerun()

        for c in st.session_state.expense_categories:
            c_col1, c_col2 = st.columns([3, 1])
            c_col1.write(f"• **{c}**")
            if c_col2.button("刪除", key=f"del_exp_cat_{c}"):
                if len(st.session_state.expense_categories) > 1:
                    st.session_state.expense_categories.remove(c)
                    st.rerun()

    with set_col3:
        st.markdown(f"### 💰 收入類別 (`{len(st.session_state.income_categories)}` / 10 項)")
        with st.form("add_inc_cat_form", clear_on_submit=True):
            new_i_cat = st.text_input("新增收入類別", placeholder="例如：壓歲紅包")
            if st.form_submit_button("➕ 新增"):
                if len(st.session_state.income_categories) < 10 and new_i_cat:
                    st.session_state.income_categories.append(new_i_cat)
                    st.rerun()

        for ic in st.session_state.income_categories:
            ic_col1, ic_col2 = st.columns([3, 1])
            ic_col1.write(f"• **{ic}**")
            if ic_col2.button("刪除", key=f"del_inc_cat_{ic}"):
                if len(st.session_state.income_categories) > 1:
                    st.session_state.income_categories.remove(ic)
                    st.rerun()
