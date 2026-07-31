import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar

# ==========================================
# 1. 頁面設定與「莫蘭迪摩卡奶茶色系」CSS
# ==========================================
st.set_page_config(
    page_title="小窩記帳 🏠",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 注入莫蘭迪大地奶茶色系 CSS (比照附圖色彩)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;800;900&display=swap');

    /* 全局奶茶大地色漸層背景 */
    html, body, [class*="css"], .stApp {
        font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background: linear-gradient(135deg, #FAF5F0 0%, #F2E8DF 50%, #E8DDD0 100%) !important;
        color: #3D322C !important;
        font-size: 16px !important;
    }
    
    header[data-testid="stHeader"] { visibility: hidden; }
    footer { visibility: hidden; }

    /* 頂部極簡 Banner */
    .cozy-banner {
        background-color: #FFFFFF;
        border: 1.5px solid #E2D5C5;
        border-radius: 20px;
        padding: 18px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(160, 120, 85, 0.06);
    }
    .banner-title {
        font-size: 24px !important;
        font-weight: 800;
        color: #8C6239;
        margin: 0;
        letter-spacing: -0.5px;
    }

    /* 📱 關鍵修復：強制 7 欄日曆在手機版不跑版 */
    [data-testid="column"] {
        min-width: 0 !important;
        padding: 0 1px !important;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 2px !important;
    }

    /* 日曆按鈕奶茶色風格 */
    div[data-testid="column"] .stButton>button {
        width: 100% !important;
        border-radius: 10px !important;
        padding: 4px 0px !important;
        background-color: #FFFFFF !important;
        color: #5C4A3E !important;
        border: 1px solid #E2D5C5 !important;
        font-size: 11px !important;
        min-height: 48px !important;
        line-height: 1.2 !important;
        transition: all 0.2s ease;
    }
    div[data-testid="column"] .stButton>button:hover {
        background-color: #A07855 !important;
        color: #FFFFFF !important;
        border-color: #A07855 !important;
    }

    /* 比照附圖的奶茶色流水帳卡片樣式 */
    .transaction-card {
        background-color: #FFFFFF;
        border: 1px solid #E2D5C5;
        padding: 16px 18px;
        border-radius: 16px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(160, 120, 85, 0.05);
    }
    .item-title {
        font-size: 18px;
        font-weight: 800;
        color: #3D322C;
    }
    .item-amount {
        font-size: 20px;
        font-weight: 900;
        color: #8C6239;
        text-align: right;
    }
    .badge-tag {
        background-color: #EEDFD2;
        color: #7A573C;
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: 700;
        margin-right: 6px;
    }
    .sub-info {
        font-size: 13px;
        color: #8C7A6B;
        margin-top: 4px;
    }

    /* 分頁 Tabs 圓角導覽列 (摩卡奶茶風) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #E8DDD0;
        padding: 6px;
        border-radius: 30px;
        margin-bottom: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 20px;
        padding: 8px 18px;
        color: #6E5A4C;
        font-weight: 700;
        font-size: 15px !important;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #A07855 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(160, 120, 85, 0.3);
    }

    /* 按鈕樣式美化 (深摩卡棕色) */
    .stButton>button {
        border-radius: 20px;
        background-color: #A07855;
        color: white;
        border: none;
        font-weight: 700;
        font-size: 15px !important;
        padding: 6px 18px;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #8A6443;
        box-shadow: 0 4px 12px rgba(138, 100, 67, 0.3);
    }

    /* 輸入框美化 */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input {
        border-radius: 12px !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2D5C5 !important;
        color: #3D322C !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Session State 初始化
# ==========================================
if "members" not in st.session_state:
    st.session_state.members = ["鼠", "熊"]

if "expense_categories" not in st.session_state:
    st.session_state.expense_categories = [
        "🍽️ 餐費", "🛋️ 居家日用", "🚗 交通費", "🏠 水電瓦斯網路費", "🎬 休閒娛樂", "🏥 醫療健康", "📦 其他"
    ]

if "income_categories" not in st.session_state:
    st.session_state.income_categories = [
        "💰 薪資收入", "🎁 獎金紅包", "📈 投資理財", "🤝 副業兼職", "💵 其他收入"
    ]

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
st.markdown("<h2 style='color:#7A573C; font-weight:800; margin-bottom:12px;'>🏠 小窩記帳</h2>", unsafe_allow_html=True)

tab_home, tab_charts, tab_memo, tab_shopping, tab_settings = st.tabs([
    "🏠 主頁記帳", "📊 統計圖表", "💬 備忘錄", "🛒 購物清單", "⚙️ 設定"
])

# ==========================================
# TAB 1: 🏠 主頁記帳 (摩卡奶茶風：月曆 + 下方流水帳)
# ==========================================
with tab_home:
    # 頂部操作按鈕 (支出 / 收入 / 結帳)
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

    st.divider()

    # 月份選單
    cal_m_col1, cal_m_col2 = st.columns([1, 1])
    sel_year = cal_m_col1.number_input("年份", min_value=2020, max_value=2030, value=st.session_state.cal_selected_date.year, label_visibility="collapsed")
    sel_month = cal_m_col2.selectbox("月份", list(range(1, 13)), index=st.session_state.cal_selected_date.month - 1, label_visibility="collapsed")

    # 繪製月曆
    week_names = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    w_cols = st.columns(7)
    for idx, w_name in enumerate(week_names):
        w_cols[idx].markdown(f"<div style='text-align:center; font-size:12px; color:#8C7A6B; font-weight:700;'>{w_name}</div>", unsafe_allow_html=True)

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(int(sel_year), int(sel_month))

    df_current = st.session_state.expenses_df.copy()
    if not df_current.empty:
        df_current["日期_dt"] = pd.to_datetime(df_current["日期"]).dt.date
    else:
        df_current["日期_dt"] = None

    for week in month_days:
        cols = st.columns(7)
        for day_idx, day_num in enumerate(week):
            if day_num == 0:
                cols[day_idx].write("")
            else:
                curr_d = date(int(sel_year), int(sel_month), day_num)
                d_records = df_current[df_current["日期_dt"] == curr_d]
                
                day_exp = d_records[d_records["類型"] == "支出"]["金額"].sum()
                day_inc = d_records[d_records["類型"] == "收入"]["金額"].sum()
                net_day = day_inc - day_exp

                btn_label = f"{day_num}\n"
                if net_day < 0:
                    btn_label += f"-{int(abs(net_day))}元"
                elif net_day > 0:
                    btn_label += f"+{int(net_day)}元"

                if cols[day_idx].button(btn_label, key=f"cal_btn_{curr_d}"):
                    st.session_state.cal_selected_date = curr_d
                    st.session_state.filter_to_single_day = True
                    st.rerun()

    # 顯示目前檢視區間控制與重置
    st.divider()
    list_header_col1, list_header_col2 = st.columns([3, 1])
    
    if st.session_state.filter_to_single_day:
        list_header_col1.markdown(f"#### 📅 正在檢視單日：`{st.session_state.cal_selected_date}`")
        if list_header_col2.button("↺ 看全月紀錄"):
            st.session_state.filter_to_single_day = False
            st.rerun()
    else:
        list_header_col1.markdown(f"#### 📅 本月全月收支紀錄 ({sel_year}年{sel_month}月)")

    # 數據篩選
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

    # 逐條收支卡片 (摩卡奶茶色系)
    if filtered_df.empty:
        st.info("此區間內尚無任何收支紀錄。")
    else:
        for idx, row in filtered_df.iterrows():
            r_date = datetime.strptime(row["日期"], "%Y-%m-%d")
            week_days_tw = ["一", "二", "三", "四", "五", "六", "日"]
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
                amt_color = "#558B6E" if row["類型"] == "收入" else "#8C6239" # 綠色/摩卡棕
                st.markdown(f"<div class='item-amount' style='color:{amt_color};'>{amt_prefix}{row['金額']:,.0f} 元</div>", unsafe_allow_html=True)
            
            # 可編輯與可刪除功能
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
# TAB 2: 📊 統計圖表 (莫蘭迪色系)
# ==========================================
with tab_charts:
    st.subheader("📊 統計圖表視覺化分析")
    st.divider()

    current_df = st.session_state.expenses_df.copy()
    
    if current_df.empty:
        st.info("尚無數據可繪製圖表。")
    else:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### 🍕 支出類別比例 (圓餅圖)")
            exp_df = current_df[current_df["類型"] == "支出"]
            if not exp_df.empty:
                fig_pie = px.pie(
                    exp_df, names="類別", values="金額", hole=0.45,
                    color_discrete_sequence=["#A07855", "#C5A880", "#8C6239", "#7A573C", "#B08968"]
                )
                fig_pie.update_traces(textfont=dict(size=16), textinfo='percent+label')
                fig_pie.update_layout(font=dict(size=15), showlegend=True, margin=dict(t=20, b=20, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            st.markdown("#### 👥 各成員支出貢獻 (長條圖)")
            exp_df = current_df[current_df["類型"] == "支出"]
            if not exp_df.empty:
                fig_bar_person = px.bar(
                    exp_df.groupby("記帳人")["金額"].sum().reset_index(),
                    x="記帳人", y="金額", color="記帳人",
                    color_discrete_sequence=["#A07855", "#C5A880"],
                    text_auto=',.0f'
                )
                fig_bar_person.update_traces(textfont=dict(size=16))
                fig_bar_person.update_layout(font=dict(size=15), margin=dict(t=20, b=20, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_bar_person, use_container_width=True)

        st.divider()
        st.markdown("#### 📊 時間支出趨勢圖 (長條圖)")
        exp_df = current_df[current_df["類型"] == "支出"]
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
            st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# TAB 3: 💬 備忘錄
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
    for memo in list(st.session_state.memos):
        col_chk, col_txt, col_edit = st.columns([0.6, 4, 1])
        checked = col_chk.checkbox("", key=f"memo_chk_{memo['id']}")
        if checked:
            st.session_state.memos.remove(memo)
            st.toast("✅ 已完成並刪除！")
            st.rerun()
        col_txt.markdown(f"<div style='font-size:18px; padding-top:4px;'>• {memo['text']}</div>", unsafe_allow_html=True)
        with col_edit.popover("✏️"):
            edited_text = st.text_input("修改備忘內容", value=memo["text"], key=f"edit_memo_input_{memo['id']}")
            if st.button("儲存修改", key=f"save_memo_{memo['id']}"):
                memo["text"] = edited_text
                st.toast("修改成功！")
                st.rerun()

# ==========================================
# TAB 4: 🛒 購物清單
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
    for shop_item in list(st.session_state.shopping_list):
        col_chk, col_txt, col_edit = st.columns([0.6, 4, 1])
        checked = col_chk.checkbox("", key=f"shop_chk_{shop_item['id']}")
        if checked:
            st.session_state.shopping_list.remove(shop_item)
            st.toast("🎉 已採買完成並移除！")
            st.rerun()
        col_txt.markdown(f"<div style='font-size:18px; padding-top:4px;'>🛒 {shop_item['item']}</div>", unsafe_allow_html=True)
        with col_edit.popover("✏️"):
            edited_item = st.text_input("修改商品名稱", value=shop_item["item"], key=f"edit_shop_input_{shop_item['id']}")
            if st.button("儲存修改", key=f"save_shop_{shop_item['id']}"):
                shop_item["item"] = edited_item
                st.toast("修改成功！")
                st.rerun()

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
