import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import calendar
import streamlit.components.v1 as components
import json
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx

# ==========================================
# 1. 頁面設定 (使用 centered 限制最大寬度)
# ==========================================
st.set_page_config(
    page_title="小窩記帳 🏠",
    page_icon="🏡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 終極防跑版 CSS + 日曆置頂 + 專案標籤隱藏與字體優化
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Klee+One:wght@400;600&family=Noto+Sans+TC:wght@400;500;700;800;900&display=swap');

    /* 🎨 全局奶黃橘色背景 + 🐱 貓咪剪影紋理 */
    html, body, [class*="css"], .stApp {
        font-family: 'Klee One', 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        -webkit-text-size-adjust: 100% !important;
        text-size-adjust: 100% !important;
        background-color: #FFF8E7 !important;
        background-image: 
            url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="260" height="260" viewBox="0 0 260 260"><g transform="translate(15,15) scale(1.6666666666666667)"><g fill="none" stroke="%23F5A623" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.11"><ellipse cx="6" cy="10" rx="1.8" ry="2.4"/><ellipse cx="10" cy="7" rx="2" ry="2.6"/><ellipse cx="14.5" cy="7" rx="2" ry="2.6"/><ellipse cx="18.5" cy="10" rx="1.8" ry="2.4"/><path d="M12 12c-3 0-5.5 1.8-5.5 4.2 0 2.3 2.3 3.8 5.5 3.8s5.5-1.5 5.5-3.8c0-2.4-2.5-4.2-5.5-4.2z"/></g></g><g transform="translate(90,8) scale(3.5416666666666665)"><g fill="none" stroke="%23D9A441" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" opacity="0.11"><path d="M5.5,3 L3.5,0.3 L6.5,2.2 Z"/><path d="M9.5,2.2 L11.5,0 L10.5,3.2 Z"/><circle cx="7.5" cy="6" r="3.2"/><path d="M4.6,7.8 C3,10 2.3,13 2.7,16 C3,18.3 4.5,19.7 6.5,20 L9.3,20 C11.3,19.5 12.7,17.3 12.5,15 C12.3,11.6 15,9 18,9 C19.6,9 20.7,10.1 20.4,11.4 C20.1,12.6 18.9,13 17.8,12.6"/><path d="M9,13 C8,15 8,18 9,20"/></g></g><g transform="translate(190,30) scale(2.2916666666666665)"><g fill="none" stroke="%23F5A623" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.11"><ellipse cx="6" cy="10" rx="1.8" ry="2.4"/><ellipse cx="10" cy="7" rx="2" ry="2.6"/><ellipse cx="14.5" cy="7" rx="2" ry="2.6"/><ellipse cx="18.5" cy="10" rx="1.8" ry="2.4"/><path d="M12 12c-3 0-5.5 1.8-5.5 4.2 0 2.3 2.3 3.8 5.5 3.8s5.5-1.5 5.5-3.8c0-2.4-2.5-4.2-5.5-4.2z"/></g></g><g transform="translate(8,118) scale(2.5)"><g fill="none" stroke="%23D9A441" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" opacity="0.11"><path d="M5.5,3 L3.5,0.3 L6.5,2.2 Z"/><path d="M9.5,2.2 L11.5,0 L10.5,3.2 Z"/><circle cx="7.5" cy="6" r="3.2"/><path d="M4.6,7.8 C3,10 2.3,13 2.7,16 C3,18.3 4.5,19.7 6.5,20 L9.3,20 C11.3,19.5 12.7,17.3 12.5,15 C12.3,11.6 15,9 18,9 C19.6,9 20.7,10.1 20.4,11.4 C20.1,12.6 18.9,13 17.8,12.6"/><path d="M9,13 C8,15 8,18 9,20"/></g></g><g transform="translate(110,150) scale(1.4583333333333333)"><g fill="none" stroke="%23F5A623" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.11"><ellipse cx="6" cy="10" rx="1.8" ry="2.4"/><ellipse cx="10" cy="7" rx="2" ry="2.6"/><ellipse cx="14.5" cy="7" rx="2" ry="2.6"/><ellipse cx="18.5" cy="10" rx="1.8" ry="2.4"/><path d="M12 12c-3 0-5.5 1.8-5.5 4.2 0 2.3 2.3 3.8 5.5 3.8s5.5-1.5 5.5-3.8c0-2.4-2.5-4.2-5.5-4.2z"/></g></g><g transform="translate(165,138) scale(2.9166666666666665)"><g fill="none" stroke="%23D9A441" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" opacity="0.11"><path d="M5.5,3 L3.5,0.3 L6.5,2.2 Z"/><path d="M9.5,2.2 L11.5,0 L10.5,3.2 Z"/><circle cx="7.5" cy="6" r="3.2"/><path d="M4.6,7.8 C3,10 2.3,13 2.7,16 C3,18.3 4.5,19.7 6.5,20 L9.3,20 C11.3,19.5 12.7,17.3 12.5,15 C12.3,11.6 15,9 18,9 C19.6,9 20.7,10.1 20.4,11.4 C20.1,12.6 18.9,13 17.8,12.6"/><path d="M9,13 C8,15 8,18 9,20"/></g></g></svg>'),
            radial-gradient(circle at 12% 18%, rgba(255, 224, 158, 0.85) 0%, transparent 40%),
            radial-gradient(circle at 88% 12%, rgba(255, 200, 87, 0.55) 0%, transparent 35%),
            radial-gradient(circle at 20% 70%, rgba(255, 241, 214, 0.9) 0%, transparent 45%),
            radial-gradient(circle at 85% 80%, rgba(245, 166, 35, 0.18) 0%, transparent 45%) !important;
        background-attachment: fixed !important;
    }

    /* 🐾 背景貓咪紋理緩慢漂浮動畫（只套在單一根節點，避免影響效能） */
    @keyframes bgPatternDrift {
        0%, 100% { background-position: 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%; }
        50%      { background-position: 4% 4%, 0% 0%, 0% 0%, 0% 0%, 0% 0%; }
    }
    .stApp { animation: bgPatternDrift 24s ease-in-out infinite !important; }
    
    /* 🚫 徹底隱藏 Streamlit 官方 Logo、頂端選單與頁尾 */
    #MainMenu, footer, header, [data-testid="stHeader"] { visibility: hidden !important; display: none !important; }
    div[data-testid="stStatusWidget"], a[href*="streamlit.app"], .stAppToolbar, [data-testid="stToolbar"], [data-testid="stDecoration"], div[class*="viewerBadge"] { display: none !important; }
    [data-testid="stAppViewContainer"] { background: transparent !important; }

    /* 📱 限制最大寬度為手機尺寸 */
    .block-container {
        max-width: 480px !important; margin: 0 auto !important; padding: 1rem 0.5rem 3rem 0.5rem !important;
    }

    /* 🚀 解鎖 Streamlit 原生阻擋，讓日曆可以完美置頂！ */
    html, body { overflow-y: auto !important; }
    .stApp, .main, .block-container, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"], div[role="tabpanel"], div[role="tabpanel"] > div { overflow: visible !important; }

    /* 📌 日曆永遠置頂 */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sticky-marker) {
        position: -webkit-sticky !important; position: sticky !important; top: 0px !important; z-index: 99999 !important;
        backdrop-filter: blur(14px) !important; background: rgba(253, 249, 245, 0.97) !important; margin-top: -10px !important;
        border-radius: 0 0 16px 16px !important; box-shadow: 0 6px 16px rgba(160, 120, 85, 0.12) !important; border-bottom: 2px solid #F5DFAE !important;
    }

    /* 🚀 手機橫向不折行霸道 CSS 覆寫 */
    @media screen and (max-width: 1024px) {
        html body .stApp div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; width: 100% !important; gap: 4px !important; }
        html body .stApp div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"], html body .stApp div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { width: 0 !important; min-width: 0 !important; flex: 1 1 0% !important; padding: 0 1px !important; }
    }

    /* 📲 Popover 彈窗安全高度與 iOS 原生滑動支援 (大幅增加底部留白防遮擋) */
    div[data-testid="stPopoverBody"] { 
        max-height: 65vh !important; 
        overflow-y: auto !important; 
        -webkit-overflow-scrolling: touch !important; 
        padding: 16px 16px 100px 16px !important; 
    }
    div[data-testid="stPopoverBody"] div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; flex-direction: column !important; }
    div[data-testid="stPopoverBody"] div[data-testid="stColumn"], div[data-testid="stPopoverBody"] div[data-testid="column"] { width: 100% !important; flex: none !important; }
    div[data-testid="stPopoverBody"] form { margin-bottom: 20px !important; padding-bottom: 20px !important; }

    /* 📌 容器卡片統一樣式 */
    div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #FFFDF3 !important; border-radius: 16px !important; padding: 8px 10px !important; margin-bottom: 8px !important; border: 1px solid #F5DFAE !important; box-shadow: 0 2px 6px rgba(160, 120, 85, 0.05) !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] p { margin-bottom: 0 !important; }

    /* 📂 收放功能 (Expander) 樣式美化 */
    [data-testid="stExpander"] { border: 1px solid #F5DFAE !important; border-radius: 16px !important; background-color: transparent !important; margin-bottom: 12px !important; }
    [data-testid="stExpander"] summary p { font-size: 16px !important; font-weight: 800 !important; color: #C2410C !important; }

    /* 🔘 按鈕視覺優化 */
    .stButton > button, div[data-testid="stPopover"] > button { -webkit-appearance: none !important; appearance: none !important; background-color: #FFFFFF !important; color: #3D322C !important; border: 1px solid #F5DFAE !important; border-radius: 12px !important; font-weight: 800 !important; font-size: 14px !important; padding: 0 !important; width: 100% !important; min-height: 34px !important; box-shadow: 0 2px 4px rgba(160, 120, 85, 0.04) !important; display: inline-flex !important; justify-content: center !important; align-items: center !important; -webkit-tap-highlight-color: transparent !important; transition: transform 0.12s ease, box-shadow 0.12s ease !important; }
    .stButton > button:hover, div[data-testid="stPopover"] > button:hover { background-color: #FFF8E7 !important; }
    .stButton > button:active, div[data-testid="stPopover"] > button:active { transform: scale(0.90) !important; box-shadow: 0 1px 2px rgba(160, 120, 85, 0.08) !important; }
    .stButton > button[kind="primary"] { background-color: #F5A623 !important; color: #FFFFFF !important; border: 1px solid #F5A623 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sticky-marker) .stButton > button { -webkit-appearance: none !important; appearance: none !important; border-radius: 10px !important; background-color: #FFFFFF !important; color: #8A5A2B !important; border: 1px solid #F5DFAE !important; box-shadow: 0 2px 4px rgba(160,120,85,0.05) !important; height: 38px !important; width: 38px !important; min-width: 38px !important; aspect-ratio: 1 / 1 !important; box-sizing: border-box !important; padding: 0 !important; margin: 0 auto !important; font-size: 14px !important; -webkit-tap-highlight-color: transparent !important; transition: transform 0.12s ease !important; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sticky-marker) .stButton > button:active { transform: scale(0.82) !important; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.sticky-marker) .stButton > button[kind="primary"] { background-color: #F5A623 !important; color: #FFFFFF !important; border: 1px solid #F5A623 !important; }
    div[data-testid="stDateInput"] label { font-size: 16px !important; font-weight: 800 !important; color: #C2410C !important; }
    /* 🚫 下拉選單的輸入框直接關閉點擊互動，改由外層容器接收點擊來開啟選單 —— 這樣鍵盤在物理上就不可能被叫出來 */
    input[role="combobox"] { pointer-events: none !important; caret-color: transparent !important; }
    /* 📱 底部固定分頁列 (Bottom Tab Bar，取代原本頂部橫向導覽列) */
    .stTabs [data-baseweb="tab-list"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 100% !important;
        max-width: 480px !important;
        z-index: 999999 !important;
        gap: 2px !important;
        background-color: #FFFDF3 !important;
        border-top: 1px solid #F5DFAE !important;
        border-radius: 20px 20px 0 0 !important;
        box-shadow: 0 -6px 18px rgba(245, 166, 35, 0.16) !important;
        padding: 8px 4px calc(10px + env(safe-area-inset-bottom, 0px)) 4px !important;
        margin-bottom: 0 !important;
        justify-content: space-around !important;
    }
    .stTabs [data-baseweb="tab"] {
        flex-direction: column !important;
        gap: 2px !important;
        flex: 1 1 0 !important;
        border-radius: 14px !important;
        padding: 6px 2px !important;
        color: #A9895C !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        min-width: 0 !important;
    }
    .stTabs [aria-selected="true"] { background-color: #FFF1D6 !important; color: #E4572E !important; }
    /* 讓內容區底部留出空間，避免被固定分頁列遮住 */
    .block-container { padding-bottom: 92px !important; }
    div[data-testid="stTabsContent"], div[role="tabpanel"] { padding-bottom: 4px !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# ⚡ 隱藏 JavaScript: 僅啟動金額數字鍵盤、日期輸入框防鍵盤、與平台浮標隱藏（保證日曆 100% 靈敏點擊）
# ==========================================
components.html(
    r"""
    <script>
    const doc = window.parent.document;

    // 📲 iOS Safari 預設不會觸發 :active 樣式，除非頁面上有註冊 touchstart 監聽，這裡補上讓按壓縮放效果生效
    doc.addEventListener('touchstart', function () {}, { passive: true });

    // 🚫 最終防線：只要任何輸入框「一被點擊聚焦」，立刻鎖成唯讀不跳鍵盤，不管它是什麼時候才出現在畫面上的
    // （比 MutationObserver／輪詢都更即時，直接在聚焦當下攔截）
    doc.addEventListener('focusin', function (e) {
        const el = e.target;
        if (el && el.tagName === 'INPUT') {
            const inSelect = el.matches('input[role="combobox"]');
            const inDate = el.closest('div[data-testid="stDateInput"]');
            if ((inSelect || inDate) && !el.hasAttribute('readonly')) {
                el.setAttribute('readonly', 'readonly');
                el.setAttribute('inputmode', 'none');
            }
        }
    }, true);

    // 🗓️ 日曆日期按鈕改圓角正方形 + 所有輸入框防鍵盤跳出（獨立成函式，供 MutationObserver 即時呼叫，不用等輪詢）
    function fixCalendarButtons() {
        doc.querySelectorAll('.stButton > button').forEach(btn => {
            const txt = (btn.textContent || '').trim();
            const inPopover = btn.closest('div[data-testid="stPopoverBody"]');

            // 🗓️ 日曆日期按鈕（不在彈窗裡）：固定 38x38 圓角正方形
            if (!inPopover && /^\d{1,2}$/.test(txt)) {
                btn.style.setProperty('width', '38px', 'important');
                btn.style.setProperty('height', '38px', 'important');
                btn.style.setProperty('min-width', '38px', 'important');
                btn.style.setProperty('max-width', '38px', 'important');
                btn.style.setProperty('min-height', '38px', 'important');
                btn.style.setProperty('max-height', '38px', 'important');
                btn.style.setProperty('border-radius', '10px', 'important');
                btn.style.setProperty('aspect-ratio', '1 / 1', 'important');
                btn.style.setProperty('padding', '0', 'important');
                btn.style.setProperty('-webkit-appearance', 'none', 'important');
                btn.style.setProperty('appearance', 'none', 'important');
            }
        });

        // 日期輸入框：禁止跳出鍵盤，只允許點選日曆
        doc.querySelectorAll('div[data-testid="stDateInput"] input').forEach(input => {
            if (!input.hasAttribute('readonly')) {
                input.setAttribute('readonly', 'readonly');
                input.setAttribute('inputmode', 'none');
            }
        });

        // 所有下拉選單（含日曆上方「切換年份／切換月份」）：禁止跳出鍵盤，只允許點選選項
        doc.querySelectorAll('input[role="combobox"]').forEach(input => {
            if (!input.hasAttribute('readonly')) {
                input.setAttribute('readonly', 'readonly');
                input.setAttribute('inputmode', 'none');
            }
        });
    }

    function optimizeMobileInputs() {
        // 1. 金額輸入框：維持一般文字鍵盤（不要用電話鍵盤，那個只有數字跟 +，沒有 -、*、/，
        //    無法輸入完整的加減乘除算式；一般鍵盤可以切換到符號頁打出完整運算式）

        fixCalendarButtons();
        
        // 2. 安全隱藏 Streamlit 平台浮標
        doc.querySelectorAll('a[href*="streamlit.app"], div[class*="viewerBadge"], [data-testid="stStatusWidget"], [data-testid="stToolbar"], #MainMenu, footer, header').forEach(el => {
            el.style.display = 'none';
            el.style.opacity = '0';
            el.style.pointerEvents = 'none';
        });
    }

    // ⚡ 用 MutationObserver 即時監看畫面變化：一旦 Streamlit 重新渲染出新的按鈕，馬上套用樣式，
    // 不用等下一次 setInterval，避免點擊後短暫「打回原型」的閃爍
    fixCalendarButtons();
    const observer = new MutationObserver(() => { fixCalendarButtons(); });
    observer.observe(doc.body, { childList: true, subtree: true });

    setInterval(optimizeMobileInputs, 600); 
    </script>
    """,
    height=0, width=0
)

# ==========================================
# 🧠 金額算式解析輔助工具
# ==========================================
def parse_math_expr(expr_str):
    try:
        allowed = "0123456789+-*/. "
        cleaned = "".join(c for c in str(expr_str) if c in allowed)
        if not cleaned: return 0.0
        return float(eval(cleaned))
    except:
        return 0.0

# ==========================================
# 3. Session State 初始化預設值
# ==========================================
today_date = date.today()
if "start_date" not in st.session_state: st.session_state.start_date = date(today_date.year, today_date.month, 1)
if "end_date" not in st.session_state: st.session_state.end_date = date(today_date.year, today_date.month, calendar.monthrange(today_date.year, today_date.month)[1])
if "members" not in st.session_state: st.session_state.members = ["🐱 鼠寶", "🐱 熊寶"]
if "expense_categories" not in st.session_state: st.session_state.expense_categories = ["🍽️ 餐費", "🛋️ 居家日用", "🚗 交通費", "🏠 水電瓦斯網路費", "🎬 休閒娛樂", "🏥 醫療健康", "📦 其他"]
if "income_categories" not in st.session_state: st.session_state.income_categories = ["💰 薪資收入", "🎁 獎金紅包", "📈 投資理財", "🤝 副業兼職", "💵 其他收入"]
if "cal_selected_date" not in st.session_state: st.session_state.cal_selected_date = date.today()
if "filter_to_single_day" not in st.session_state: st.session_state.filter_to_single_day = False
if "category_filter" not in st.session_state: st.session_state.category_filter = "全部類別"
if "person_filter" not in st.session_state: st.session_state.person_filter = "全部成員"
if "memos" not in st.session_state: st.session_state.memos = [{"id": 1, "text": "確認下個月水電費轉帳帳號"}]
if "shopping_list" not in st.session_state: st.session_state.shopping_list = [{"id": 101, "item": "鮮奶 🥛"}]
# 新增功能：設定儲存狀態
if "category_budgets" not in st.session_state: st.session_state.category_budgets = {}
if "fixed_transactions" not in st.session_state: st.session_state.fixed_transactions = []
if "projects" not in st.session_state: st.session_state.projects = ["無"]
if "sync_error" not in st.session_state: st.session_state.sync_error = None

# ==========================================
# 4. 連接 Google Sheets & 絕對可靠的雲端同步機制
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def _background_sync(final_df):
    """實際寫入 Google Sheets 的動作，丟到背景執行緒跑，不卡住畫面更新"""
    try:
        conn.update(data=final_df)
        st.cache_data.clear() # 🚀 儲存後強制清除快取
        st.session_state.sync_error = None
    except Exception as e:
        st.session_state.sync_error = str(e)

def save_and_sync():
    """準備好要寫入的資料後，交給背景執行緒非同步上傳，UI 立刻可以繼續、不必等待雲端回應"""
    settings_dict = {
        "members": st.session_state.members,
        "expense_categories": st.session_state.expense_categories,
        "income_categories": st.session_state.income_categories,
        "memos": st.session_state.memos,
        "shopping_list": st.session_state.shopping_list,
        "category_budgets": st.session_state.category_budgets,
        "fixed_transactions": st.session_state.fixed_transactions,
        "projects": st.session_state.projects
    }
    
    settings_df = pd.DataFrame([{
        "ID": "SYS_SETTINGS", "日期": "2099-12-31", "類型": "系統", 
        "類別": "系統", "項目": "設定檔", "金額": 0, 
        "記帳人": "系統", "備註": json.dumps(settings_dict, ensure_ascii=False),
        "結帳狀態": "", "結帳單號": "", "已同意人": "", "專案": ""
    }])
    
    df_core = st.session_state.expenses_df[st.session_state.expenses_df["ID"] != "SYS_SETTINGS"]
    final_df = pd.concat([df_core, settings_df], ignore_index=True)
    
    sync_thread = threading.Thread(target=_background_sync, args=(final_df,), daemon=True)
    add_script_run_ctx(sync_thread)  # 讓背景執行緒能安全存取 session_state
    sync_thread.start()

def trigger_auto_fixed_transactions():
    """獨立防撞檢查並觸發固定收支自動記帳"""
    try:
        today = date.today()
        current_ym = f"{today.year}-{today.month:02d}"
        triggered = False
        
        for ft in st.session_state.fixed_transactions:
            s_date_str = ft.get('start_date', '2000-01-01')
            e_date_str = ft.get('end_date', '2099-12-31')
            try: s_date = datetime.strptime(s_date_str, "%Y-%m-%d").date()
            except: s_date = date(2000, 1, 1)
            try: e_date = datetime.strptime(e_date_str, "%Y-%m-%d").date()
            except: e_date = date(2099, 12, 31)

            if s_date <= today <= e_date:
                if today.day >= ft.get('day', 1) and ft.get('last_month') != current_ym:
                    new_id = f"{'EXP' if ft.get('type')=='支出' else 'INC'}-AUTO-{int(datetime.now().timestamp()*1000)}"
                    new_row = pd.DataFrame([{
                        "ID": new_id, "日期": str(today), "類型": ft.get("type", "支出"), "類別": ft.get("category", ""),
                        "項目": f"🔄 {ft.get('item', '')}", "金額": float(ft.get("amount", 0)), "記帳人": ft.get("payer", ""),
                        "備註": "系統自動記帳", "結帳狀態": "未結帳", "結帳單號": "", "已同意人": "", "專案": "無"
                    }])
                    st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_row], ignore_index=True)
                    ft['last_month'] = current_ym
                    triggered = True
                
        if triggered: save_and_sync()
    except Exception:
        pass 

def load_data_and_recover_settings():
    """從雲端載入資料，並還原設定檔"""
    try:
        df = conn.read(ttl="10m") 
        cols = ["ID", "日期", "類型", "類別", "項目", "金額", "記帳人", "備註", "結帳狀態", "結帳單號", "已同意人", "專案"]
        for c in cols:
            if c not in df.columns: df[c] = ""
        # 強制把所有「文字類」欄位轉成字串型態，避免空白欄位被 pandas 誤判成數字型態，
        # 導致之後寫入文字時被新版 pandas 的嚴格型態檢查擋下來報錯
        text_cols = ["ID", "日期", "類型", "類別", "項目", "記帳人", "備註", "結帳狀態", "結帳單號", "已同意人", "專案"]
        for c in text_cols:
            df[c] = df[c].fillna("").astype(str)
            df.loc[df[c].isin(["nan", "None", "NaN"]), c] = ""
        df["類型"] = df["類型"].replace("", "支出")
        df["金額"] = pd.to_numeric(df["金額"], errors="coerce").fillna(0)
        
        settings_row = df[df["ID"] == "SYS_SETTINGS"]
        if not settings_row.empty:
            try:
                settings = json.loads(settings_row["備註"].iloc[0])
                if "members" in settings: st.session_state.members = settings["members"]
                if "expense_categories" in settings: st.session_state.expense_categories = settings["expense_categories"]
                if "income_categories" in settings: st.session_state.income_categories = settings["income_categories"]
                if "memos" in settings: st.session_state.memos = settings["memos"]
                if "shopping_list" in settings: st.session_state.shopping_list = settings["shopping_list"]
                if "category_budgets" in settings: st.session_state.category_budgets = settings["category_budgets"]
                if "fixed_transactions" in settings: st.session_state.fixed_transactions = settings["fixed_transactions"]
                if "projects" in settings: st.session_state.projects = settings["projects"]
            except: pass
            
        st.session_state.expenses_df = df[df["ID"] != "SYS_SETTINGS"].copy()
        trigger_auto_fixed_transactions() 
    except Exception:
        st.session_state.expenses_df = pd.DataFrame(columns=["ID", "日期", "類型", "類別", "項目", "金額", "記帳人", "備註", "結帳狀態", "結帳單號", "已同意人", "專案"])

if "expenses_df" not in st.session_state:
    load_data_and_recover_settings()

# ⚠️ 檢查上一次背景同步是否失敗，若失敗則跳出警告提示（顯示一次後清除）
if st.session_state.get("sync_error"):
    st.toast(f"⚠️ 雲端同步失敗，資料僅暫存在畫面上，請檢查網路後重新操作一次：{st.session_state.sync_error}", icon="⚠️")
    st.session_state.sync_error = None

# ==========================================
# 4.5 記支出／記收入彈窗（獨立成 @st.fragment，鍵盤按鈕只重跑這一小塊，不用整支程式全部重算，減少延遲）
# ==========================================
@st.fragment
def expense_entry_fragment():
    st.markdown("### 💸 新增支出")
    e_date = st.date_input("支出日期", st.session_state.cal_selected_date, key="e_date_input")
    e_payer = st.selectbox("付款人", st.session_state.members, key="e_payer_input")
    e_cat = st.selectbox("支出分類", st.session_state.expense_categories, key="e_cat_input")
    e_item = st.text_input("消費項目", placeholder="例如：麵包", key="e_item_input")
    e_amount_str = st.text_input("金額 ($)", key="e_amount_str_input", placeholder="可輸入算式，如 120+35")
    e_proj = st.selectbox("專案目標 (選填)", st.session_state.projects, key="e_proj_input")
    e_note = st.text_input("備註 (非必填)", key="e_note_input")
    if st.button("確認新增", type="primary", use_container_width=True, key="e_submit_btn"):
        st.toast("💾 儲存中...", icon="⏳")
        e_amount = parse_math_expr(e_amount_str)
        new_row = pd.DataFrame([{"ID": f"EXP-{int(datetime.now().timestamp())}", "日期": str(e_date), "類型": "支出", "類別": str(e_cat), "項目": e_item.strip() if e_item else "未填寫", "金額": float(e_amount), "記帳人": str(e_payer), "備註": str(e_note), "結帳狀態": "未結帳", "結帳單號": "", "已同意人": "", "專案": str(e_proj) if e_proj != "無" else ""}])
        st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_row], ignore_index=True)
        save_and_sync()
        st.session_state.pop("e_item_input", None)
        st.session_state.pop("e_note_input", None)
        st.session_state.pop("e_amount_str_input", None)
        st.toast("🎉 支出新增成功！")
        st.rerun()  # 這裡要整頁重跑，讓外面的明細清單／總計立刻反映新增的這一筆

@st.fragment
def income_entry_fragment():
    st.markdown("### ✨ 新增收入")
    i_date = st.date_input("收入日期", st.session_state.cal_selected_date, key="i_date_input")
    i_receiver = st.selectbox("收款人", st.session_state.members, key="i_receiver_input")
    i_cat = st.selectbox("收入分類", st.session_state.income_categories, key="i_cat_input")
    i_item = st.text_input("收入項目", placeholder="例如：薪資", key="i_item_input")
    i_amount_str = st.text_input("金額 ($)", key="i_amount_str_input", placeholder="可輸入算式，如 1000+500")
    i_proj = st.selectbox("專案目標 (選填)", st.session_state.projects, key="i_proj_input")
    i_note = st.text_input("備註 (非必填)", key="i_note_input")
    if st.button("確認新增", type="primary", use_container_width=True, key="i_submit_btn"):
        st.toast("💾 儲存中...", icon="⏳")
        i_amount = parse_math_expr(i_amount_str)
        new_row = pd.DataFrame([{"ID": f"INC-{int(datetime.now().timestamp())}", "日期": str(i_date), "類型": "收入", "類別": str(i_cat), "項目": i_item.strip() if i_item else "未填寫", "金額": float(i_amount), "記帳人": str(i_receiver), "備註": str(i_note), "結帳狀態": "未結帳", "結帳單號": "", "已同意人": "", "專案": str(i_proj) if i_proj != "無" else ""}])
        st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_row], ignore_index=True)
        save_and_sync()
        st.session_state.pop("i_item_input", None)
        st.session_state.pop("i_note_input", None)
        st.session_state.pop("i_amount_str_input", None)
        st.toast("🎉 收入新增成功！")
        st.rerun()  # 這裡要整頁重跑，讓外面的明細清單／總計立刻反映新增的這一筆

# ==========================================
# 5. 主選單 Header & 分頁
# ==========================================
st.markdown("<h2 style='color:#C2410C; font-weight:900; margin-bottom:10px;'>🏠 小窩記帳 🐾</h2>", unsafe_allow_html=True)

tab_home, tab_charts, tab_memo, tab_shopping, tab_settings = st.tabs([
    "🏠 主頁", "📊 圖表", "💬 備忘", "🛒 購物", "⚙️ 設定"
])

# ==========================================
# TAB 1: 🏠 主頁記帳
# ==========================================
with tab_home:
    # 📌 置頂區塊：緊湊日曆 (含獨立年份、月份選單)
    with st.container(border=True):
        st.markdown("<span class='sticky-marker'></span>", unsafe_allow_html=True)
        
        cal_head_1, cal_head_2, cal_head_3 = st.columns([1.5, 0.9, 0.7])
        with cal_head_1:
            st.markdown(f"<div style='font-weight:900; font-size:19px; color:#3D322C; padding-top:4px;'>📅 {st.session_state.cal_selected_date.strftime('%Y年%m月')}</div>", unsafe_allow_html=True)
        with cal_head_2:
            year_list = list(range(2020, 2035))
            sel_year = st.selectbox("切換年份", year_list, index=year_list.index(st.session_state.cal_selected_date.year), label_visibility="collapsed")
        with cal_head_3:
            sel_month = st.selectbox("切換月份", list(range(1, 13)), index=st.session_state.cal_selected_date.month - 1, label_visibility="collapsed")
            
        if sel_year != st.session_state.cal_selected_date.year or sel_month != st.session_state.cal_selected_date.month:
            st.session_state.cal_selected_date = date(sel_year, sel_month, 1)
            st.rerun()

        w_cols = st.columns(7)
        for idx, w_name in enumerate(["日", "一", "二", "三", "四", "五", "六"]):
            w_cols[idx].markdown(f"<div style='text-align:center; font-size:12px; color:#A9895C; font-weight:800;'>{w_name}</div>", unsafe_allow_html=True)

        cal = calendar.Calendar(firstweekday=6)
        for week in cal.monthdayscalendar(int(sel_year), int(sel_month)):
            cols = st.columns(7)
            for day_idx, day_num in enumerate(week):
                if day_num == 0:
                    cols[day_idx].write("")
                else:
                    curr_d = date(int(sel_year), int(sel_month), day_num)
                    btn_type = "primary" if curr_d == st.session_state.cal_selected_date else "secondary"
                    if cols[day_idx].button(str(day_num), key=f"c_day_{curr_d}", type=btn_type):
                        st.session_state.cal_selected_date = curr_d
                        st.session_state.filter_to_single_day = True
                        st.rerun()

    # 🍵 三大功能按鈕區塊
    with st.container(border=False):
        top_col1, top_col2, top_col3 = st.columns(3)
        with top_col1:
            with st.popover("💸 記支出", use_container_width=True):
                expense_entry_fragment()
        with top_col2:
            with st.popover("✨ 記收入", use_container_width=True):
                income_entry_fragment()
        with top_col3:
            with st.popover("🐾 算算帳", use_container_width=True):
                st.markdown("### 🐾 結帳專區")
                unsettled_df = st.session_state.expenses_df[st.session_state.expenses_df["結帳狀態"] != "已結帳"].copy()
                if unsettled_df.empty:
                    st.info("目前無待結帳筆數。")
                else:
                    st.write(f"待結帳：**{len(unsettled_df)}** 筆")
                    chk_cols = st.columns(len(st.session_state.members))
                    agreed_flags = [chk_cols[i].checkbox(f"{m}", key=f"settle_chk_{m}") for i, m in enumerate(st.session_state.members)]
                    if st.button("🤝 完成結帳", type="primary", use_container_width=True, disabled=(not all(agreed_flags))):
                        st.toast("💾 儲存中...", icon="⏳")
                        st.session_state.expenses_df.loc[unsettled_df.index, "結帳狀態"] = "已結帳"
                        st.session_state.expenses_df.loc[unsettled_df.index, "結帳單號"] = f"SETTLE-{datetime.now().strftime('%Y%m%d%H%M')}"
                        save_and_sync()
                        st.success("🎉 已完成結帳！")
                        st.rerun()

    # 📌 顯示當前檢視區間標題
    if st.session_state.filter_to_single_day:
        display_title = f"📅 {st.session_state.cal_selected_date}"
    else:
        start_str = st.session_state.start_date.strftime('%Y-%m-%d')
        end_str = st.session_state.end_date.strftime('%Y-%m-%d')
        display_title = f"📅 {start_str}" if start_str == end_str else f"📅 {start_str} ~ {end_str}"
    
    st.markdown(f"<h2 style='text-align:center; color:#C2410C; font-weight:900; font-size:18px; margin:10px 0 6px 0;'>{display_title}</h2>", unsafe_allow_html=True)

    # 🔍 篩選查詢：日期區間、類別、成員整合在同一個區塊，設定好按「套用篩選」一次套用
    with st.container(border=True):
        st.markdown("<h3 style='color:#C2410C; margin-bottom:8px; font-size:16px;'>🔍 篩選查詢</h3>", unsafe_allow_html=True)
        picked_range = st.date_input("日期區間", value=(st.session_state.start_date, st.session_state.end_date), key="unified_date_picker")

        DIVIDER_EXPENSE = "── 支出 ──"
        DIVIDER_INCOME = "── 收入 ──"
        all_categories = ["全部類別", DIVIDER_EXPENSE] + st.session_state.expense_categories + [DIVIDER_INCOME] + st.session_state.income_categories
        all_people = ["全部成員"] + st.session_state.members
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            picked_category = st.selectbox(
                "篩選類別", all_categories,
                index=all_categories.index(st.session_state.category_filter) if st.session_state.category_filter in all_categories else 0
            )
        with f_col2:
            picked_person = st.selectbox(
                "篩選成員", all_people,
                index=all_people.index(st.session_state.person_filter) if st.session_state.person_filter in all_people else 0
            )

        q_col1, q_col2 = st.columns(2)
        if q_col1.button("✅ 套用篩選", type="primary", use_container_width=True):
            if isinstance(picked_range, tuple) and len(picked_range) == 2:
                st.session_state.start_date, st.session_state.end_date = picked_range[0], picked_range[1]
            elif isinstance(picked_range, tuple) and len(picked_range) == 1:
                st.session_state.start_date = st.session_state.end_date = picked_range[0]
            # 「── 支出 ──」「── 收入 ──」只是清單裡的分隔標題，不是真的分類，選到就當作沒篩選
            st.session_state.category_filter = picked_category if picked_category not in (DIVIDER_EXPENSE, DIVIDER_INCOME) else "全部類別"
            st.session_state.person_filter = picked_person
            st.session_state.filter_to_single_day = False
            st.rerun()

        if q_col2.button("↺ 重置全部", use_container_width=True):
            today = date.today()
            st.session_state.start_date = date(today.year, today.month, 1)
            st.session_state.end_date = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
            st.session_state.category_filter = "全部類別"
            st.session_state.person_filter = "全部成員"
            st.session_state.filter_to_single_day = False
            st.rerun()

    # 📊 取得過濾資料
    df_current = st.session_state.expenses_df.copy()
    if not df_current.empty:
        df_current["日期_dt"] = pd.to_datetime(df_current["日期"]).dt.date
        if st.session_state.filter_to_single_day:
            filtered_df = df_current[df_current["日期_dt"] == st.session_state.cal_selected_date]
        else:
            filtered_df = df_current[(df_current["日期_dt"] >= st.session_state.start_date) & (df_current["日期_dt"] <= st.session_state.end_date)]
        if st.session_state.category_filter != "全部類別":
            filtered_df = filtered_df[filtered_df["類別"] == st.session_state.category_filter]
        if st.session_state.person_filter != "全部成員":
            filtered_df = filtered_df[filtered_df["記帳人"] == st.session_state.person_filter]
    else:
        filtered_df = pd.DataFrame()

    if not filtered_df.empty: filtered_df = filtered_df.sort_values(by="日期", ascending=False)
    week_days_tw = ["一", "二", "三", "四", "五", "六", "日"]

    # ==========================================
    # 📊 各成員收支總計面板與預算警戒線
    # ==========================================
    if not filtered_df.empty:
        total_exp = filtered_df[filtered_df["類型"] == "支出"]["金額"].sum()
        total_inc = filtered_df[filtered_df["類型"] == "收入"]["金額"].sum()
        
        st.markdown("<div style='background-color:#FFFDF3; border-radius:12px; padding:12px 14px; border:1px solid #F5DFAE; margin-bottom:12px; box-shadow: 0 2px 6px rgba(160,120,85,0.05);'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:15px; font-weight:900; color:#C2410C; margin-bottom:8px; border-bottom:1px solid #F5DFAE; padding-bottom:4px;'>📊 區間收支總計</div>", unsafe_allow_html=True)
        
        for member in st.session_state.members:
            mem_df = filtered_df[filtered_df["記帳人"] == member]
            mem_exp = mem_df[mem_df["類型"] == "支出"]["金額"].sum()
            mem_inc = mem_df[mem_df["類型"] == "收入"]["金額"].sum()
            st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:6px; font-size:14px;'><span style='font-weight:800; color:#3D322C;'>{member}</span><span><span style='color:#E4572E;'>支 {mem_exp:,.0f}</span>&nbsp;&nbsp;|&nbsp;&nbsp;<span style='color:#558B6E;'>收 {mem_inc:,.0f}</span></span></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='display:flex; justify-content:space-between; margin-top:8px; padding-top:6px; border-top:1px dashed #F5DFAE; font-size:14px;'><span style='font-weight:900; color:#C2410C;'>🏠 小窩總計</span><span style='font-weight:800;'><span style='color:#E4572E;'>支 {total_exp:,.0f}</span>&nbsp;&nbsp;|&nbsp;&nbsp;<span style='color:#558B6E;'>收 {total_inc:,.0f}</span></span></div>", unsafe_allow_html=True)
        
        current_month_mask = (pd.to_datetime(df_current["日期"]).dt.year == sel_year) & (pd.to_datetime(df_current["日期"]).dt.month == sel_month)
        curr_m_exp = df_current[current_month_mask & (df_current["類型"] == "支出")]
        
        has_budget = any(b > 0 for b in st.session_state.category_budgets.values())
        if has_budget:
            st.markdown("<div style='font-size:15px; font-weight:900; color:#C2410C; margin-top:16px; margin-bottom:8px; border-bottom:1px solid #F5DFAE; padding-bottom:4px;'>⚠️ 本月分類預算警戒線</div>", unsafe_allow_html=True)
            for cat, budget in st.session_state.category_budgets.items():
                if budget > 0:
                    spent = curr_m_exp[curr_m_exp["類別"] == cat]["金額"].sum()
                    pct = (spent / budget) * 100
                    color = "#558B6E" if pct < 70 else "#E9C46A" if pct < 90 else "#E07A5F"
                    st.markdown(f"""
                    <div style='margin-bottom: 10px;'>
                        <div style='display:flex; justify-content:space-between; font-size:13px; font-weight:700; color:#8A5A2B; margin-bottom:4px;'>
                            <span>{cat} ({pct:.1f}%)</span><span>{spent:,.0f} / {budget:,.0f}</span>
                        </div>
                        <div style='width: 100%; background-color: #F5DFAE; border-radius: 6px; height: 8px; overflow:hidden;'>
                            <div style='width: {min(pct, 100)}%; background-color: {color}; height: 100%; border-radius: 6px;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 📝 可摺疊 (Expander) 收支明細區塊 (已移除 nan 標籤、品項字體微縮小)
    # ==========================================
    with st.expander("📝 展開 / 收起各項明細", expanded=True):
        if filtered_df.empty:
            st.info("此區間內無紀錄。")
        else:
            for idx, row in filtered_df.iterrows():
                r_date = datetime.strptime(row["日期"], "%Y-%m-%d")
                day_week_str = week_days_tw[r_date.weekday()]
                
                with st.container(border=True):
                    c_name, c_amt, c_edit, c_del = st.columns([4, 2.6, 0.7, 0.7])
                    
                    with c_name:
                        proj_val = row.get('專案', '')
                        proj_str = str(proj_val) if proj_val is not None else ''
                        has_proj = proj_str and proj_str.strip() != "" and proj_str.lower() != "nan" and proj_str != "無"
                        proj_tag = f"<span style='color:#F5A623; font-size:11px; border:1px solid #F0C888; padding:1px 4px; border-radius:4px; margin-right:4px; white-space:nowrap;'>{proj_str}</span>" if has_proj else ""
                        
                        # 品項名稱改成可換行顯示，避免在較窄的手機螢幕上被裁切看不到完整內容
                        st.markdown(f"<div style='font-size:15px; font-weight:800; color:#3D322C; line-height:1.3; word-break:break-word; overflow-wrap:break-word;'>{proj_tag}{row['項目']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:11px; color:#A9895C; margin-top:4px;'>{row['記帳人']} · {r_date.month}/{r_date.day}</div>", unsafe_allow_html=True)
                        
                    with c_amt:
                        amt_color = "#558B6E" if row["類型"] == "收入" else "#E07A5F"
                        display_amt = int(row['金額']) if row['金額'] % 1 == 0 else row['金額']
                        st.markdown(f"<div style='font-size:17px; font-weight:900; color:{amt_color}; margin-top:4px; text-align:right;'>{'+' if row['類型'] == '收入' else ''}{display_amt:,}</div>", unsafe_allow_html=True)
                    
                    with c_edit:
                        with st.popover("✏️"):
                            with st.form(f"edit_form_{row['ID']}"):
                                e_date_val = st.date_input("日期", r_date)
                                e_type_val = st.radio("類型", ["支出", "收入"], index=0 if row["類型"] == "支出" else 1)
                                
                                cats = st.session_state.expense_categories if e_type_val == "支出" else st.session_state.income_categories
                                cat_idx = cats.index(row["類別"]) if row["類別"] in cats else 0
                                e_cat_val = st.selectbox("分類", cats, index=cat_idx)
                                
                                e_item_val = st.text_input("項目", value=row["項目"])
                                e_amt_val_str = st.text_input("金額 (支援算式)", value=str(display_amt))
                                
                                p_val = row.get("專案", "無")
                                if pd.isna(p_val) or p_val == "": p_val = "無"
                                proj_idx = st.session_state.projects.index(p_val) if p_val in st.session_state.projects else 0
                                e_proj_val = st.selectbox("專案標籤", st.session_state.projects, index=proj_idx)
                                
                                mem_idx = st.session_state.members.index(row["記帳人"]) if row["記帳人"] in st.session_state.members else 0
                                e_payer_val = st.selectbox("成員", st.session_state.members, index=mem_idx)
                                e_note_val = st.text_input("備註", value=row["備註"])
                                
                                if st.form_submit_button("儲存修改", type="primary", use_container_width=True):
                                    st.toast("💾 儲存中...", icon="⏳")
                                    e_amt_val = parse_math_expr(e_amt_val_str)
                                    edit_mask = st.session_state.expenses_df["ID"] == row["ID"]
                                    # 新版 pandas 對「一次寫入多個混合型態欄位」的檢查變嚴格，改成一欄一欄分開寫，避免 dtype 衝突報錯
                                    st.session_state.expenses_df.loc[edit_mask, "日期"] = str(e_date_val)
                                    st.session_state.expenses_df.loc[edit_mask, "類型"] = e_type_val
                                    st.session_state.expenses_df.loc[edit_mask, "類別"] = e_cat_val
                                    st.session_state.expenses_df.loc[edit_mask, "項目"] = e_item_val
                                    st.session_state.expenses_df.loc[edit_mask, "金額"] = float(e_amt_val)
                                    st.session_state.expenses_df.loc[edit_mask, "記帳人"] = e_payer_val
                                    st.session_state.expenses_df.loc[edit_mask, "備註"] = e_note_val
                                    st.session_state.expenses_df.loc[edit_mask, "專案"] = str(e_proj_val) if e_proj_val != "無" else ""
                                    save_and_sync()
                                    st.rerun()
                    with c_del:
                        if st.button("🗑️", key=f"del_btn_{row['ID']}"):
                            st.toast("💾 刪除中...", icon="🗑️")
                            st.session_state.expenses_df = st.session_state.expenses_df[st.session_state.expenses_df["ID"] != row["ID"]]
                            save_and_sync()
                            st.rerun()



# ==========================================
# TAB 2~5: 統計、備忘錄、購物、設定 
# ==========================================
with tab_charts:
    st.subheader("📊 統計圖表視覺化分析")
    
    # 📌 圖表區：新增分析區間選擇器
    with st.container(border=True):
        st.markdown("<div style='font-size:15px; font-weight:800; color:#C2410C; margin-bottom:8px;'>📅 選擇分析區間</div>", unsafe_allow_html=True)
        ch_col1, ch_col2 = st.columns(2)
        chart_start = ch_col1.date_input("起始日期", st.session_state.start_date, key="chart_start")
        chart_end = ch_col2.date_input("結束日期", st.session_state.end_date, key="chart_end")
        
    current_df = st.session_state.expenses_df.copy()
    if not current_df.empty:
        current_df["日期_dt"] = pd.to_datetime(current_df["日期"]).dt.date
        chart_df = current_df[(current_df["日期_dt"] >= chart_start) & (current_df["日期_dt"] <= chart_end)]
    else:
        chart_df = pd.DataFrame()

    if chart_df.empty: 
        st.info("此區間內尚無數據。")
    else:
        exp_df = chart_df[chart_df["類型"] == "支出"]
        if not exp_df.empty:
            # 1. 圓餅圖：支出類別比例
            st.markdown("<h4 style='text-align:center; color:#E4572E; margin-top:20px;'>🍕 支出類別比例</h4>", unsafe_allow_html=True)
            fig_pie = px.pie(exp_df, names="類別", values="金額", hole=0.45, color_discrete_sequence=["#F5A623", "#FFC857", "#E4572E", "#C2410C", "#FFD37D"])
            fig_pie.update_layout(font=dict(size=14), legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
            st.divider()
            
            # 2. 長條圖：各分類累積支出 (依金額由高到低排序)
            st.markdown("<h4 style='text-align:center; color:#E4572E;'>📊 各分類累積支出</h4>", unsafe_allow_html=True)
            cat_sum = exp_df.groupby("類別")["金額"].sum().reset_index().sort_values(by="金額", ascending=False)
            fig_bar = px.bar(cat_sum, x="類別", y="金額", color_discrete_sequence=["#F5A623"], text_auto=',.0f')
            fig_bar.update_layout(font=dict(size=14), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
            st.divider()
            
            # 3. 專案目標統計
            proj_exp = exp_df[(exp_df["專案"].notna()) & (exp_df["專案"] != "無") & (exp_df["專案"] != "")]
            if not proj_exp.empty:
                st.markdown("<h4 style='text-align:center; color:#E4572E;'>🎯 專案目標花費統計</h4>", unsafe_allow_html=True)
                proj_sum = proj_exp.groupby("專案")["金額"].sum().reset_index().sort_values(by="金額", ascending=False)
                fig_proj = px.bar(proj_sum, x="專案", y="金額", text_auto=',.0f', color_discrete_sequence=["#E07A5F"])
                fig_proj.update_layout(font=dict(size=14), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_proj, use_container_width=True, config={'displayModeBar': False})

with tab_memo:
    st.subheader("💬 備忘錄")
    with st.form("add_memo_form", clear_on_submit=True):
        col_m1, col_m2 = st.columns([3, 1])
        new_memo_text = col_m1.text_input("輸入備忘", label_visibility="collapsed")
        if col_m2.form_submit_button("➕ 新增", type="primary") and new_memo_text:
            st.toast("💾 儲存中...", icon="⏳")
            st.session_state.memos.append({"id": int(datetime.now().timestamp()*1000), "text": new_memo_text})
            save_and_sync()
            st.rerun()
            
    for memo in list(st.session_state.memos):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([0.8, 4.5, 1.5, 1.5])
            if c1.checkbox("", key=f"mc_{memo['id']}"):
                st.session_state.memos.remove(memo)
                save_and_sync()
                st.rerun()
            c2.markdown(f"• {memo['text']}")
            with c3:
                with st.popover("✏️"):
                    new_text = st.text_input("修改", value=memo["text"], key=f"mi_{memo['id']}")
                    if st.button("儲存", key=f"ms_{memo['id']}", type="primary", use_container_width=True):
                        st.toast("💾 儲存中...", icon="⏳")
                        memo["text"] = new_text
                        save_and_sync()
                        st.rerun()
            with c4:
                st.write("")

with tab_shopping:
    st.subheader("🛒 購物清單")
    with st.form("add_shop_form", clear_on_submit=True):
        col_s1, col_s2 = st.columns([3, 1])
        new_shop_item = col_s1.text_input("輸入商品", label_visibility="collapsed")
        if col_s2.form_submit_button("➕ 新增", type="primary") and new_shop_item:
            st.toast("💾 儲存中...", icon="⏳")
            st.session_state.shopping_list.append({"id": int(datetime.now().timestamp()*1000), "item": new_shop_item})
            save_and_sync()
            st.rerun()
            
    for item in list(st.session_state.shopping_list):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([0.8, 4.5, 1.5, 1.5])
            if c1.checkbox("", key=f"sc_{item['id']}"):
                st.session_state.shopping_list.remove(item)
                save_and_sync()
                st.rerun()
            c2.markdown(f"🛒 {item['item']}")
            with c3:
                with st.popover("✏️"):
                    new_item = st.text_input("修改", value=item["item"], key=f"si_{item['id']}")
                    if st.button("儲存", key=f"ss_{item['id']}", type="primary", use_container_width=True):
                        st.toast("💾 儲存中...", icon="⏳")
                        item["item"] = new_item
                        save_and_sync()
                        st.rerun()
            with c4:
                st.write("")

with tab_settings:
    st.subheader("⚙️ 小窩進階設定")
    
    # --- 1. 預算設定 (Expander) ---
    with st.expander("⚠️ 分類預算設定", expanded=False):
        for c in st.session_state.expense_categories:
            with st.container(border=True):
                b_col1, b_col2 = st.columns([3, 2])
                current_b = st.session_state.category_budgets.get(c, 0)
                b_col1.write(f"**{c}**")
                b_col1.markdown(f"<div style='font-size:12px; color:#A9895C;'>目前預算: ${current_b:,}</div>", unsafe_allow_html=True)
                with b_col2:
                    with st.popover("設定預算", use_container_width=True):
                        new_b = st.number_input(f"設定 {c} 月預算", min_value=0, value=current_b, step=500)
                        btn1, btn2 = st.columns(2)
                        if btn1.button("儲存", key=f"btn_bud_{c}", type="primary", use_container_width=True):
                            st.toast("💾 儲存中...", icon="⏳")
                            st.session_state.category_budgets[c] = new_b
                            save_and_sync()
                            st.rerun()
                        if btn2.button("清除", key=f"btn_clr_{c}", use_container_width=True):
                            st.toast("💾 清除中...", icon="⏳")
                            st.session_state.category_budgets[c] = 0
                            save_and_sync()
                            st.rerun()

    # --- 2. 固定收支設定 (Expander) ---
    with st.expander("📅 固定收支自動記帳", expanded=False):
        with st.popover("➕ 新增自動記帳", use_container_width=True):
            f_type = st.radio("收支類型", ["支出", "收入"], horizontal=True)
            f_cat = st.selectbox("分類", st.session_state.expense_categories if f_type == "支出" else st.session_state.income_categories)
            f_day = st.number_input("每月執行日 (1-31號)", min_value=1, max_value=31, value=1)
            f_item = st.text_input("項目名稱 (例如：Netflix 或 房租)")
            f_amt_str = st.text_input("金額 (支援算式)", value="0")
            f_payer = st.selectbox("記帳人", st.session_state.members)
            
            f_start = st.date_input("開始日期", date.today())
            f_has_end = st.checkbox("設定結束日期")
            if f_has_end:
                f_end = st.date_input("結束日期", date.today())
            else:
                f_end = date(2099, 12, 31)

            if st.button("確認新增", type="primary", use_container_width=True):
                if f_item:
                    st.toast("💾 儲存中...", icon="⏳")
                    f_amt = parse_math_expr(f_amt_str)
                    st.session_state.fixed_transactions.append({
                        "id": int(datetime.now().timestamp()*1000), "day": f_day, "type": f_type,
                        "category": f_cat, "item": f_item.strip(), "amount": f_amt, "payer": f_payer, 
                        "start_date": str(f_start), "end_date": str(f_end), "last_month": ""
                    })
                    save_and_sync()
                    st.rerun()
                    
        for ft in list(st.session_state.fixed_transactions):
            with st.container(border=True):
                f1, f2 = st.columns([4.5, 1.5])
                f1.markdown(f"<div style='font-size:14px; font-weight:700; color:#3D322C;'>每月 {ft.get('day', 1)} 日 | {ft.get('item', '')}</div>", unsafe_allow_html=True)
                
                s_d = ft.get('start_date', '')
                e_d = ft.get('end_date', '')
                date_str = "📅 "
                if s_d: date_str += f"從 {s_d} 起 "
                if e_d and e_d != '2099-12-31': date_str += f"至 {e_d} 止"
                elif s_d: date_str += "(無結束日)"
                else: date_str += "舊資料無日期限制"
                    
                f1.markdown(f"<div style='font-size:11px; color:#F5A623; margin-bottom:2px;'>{date_str}</div>", unsafe_allow_html=True)
                f1.markdown(f"<div style='font-size:12px; color:#A9895C;'>{ft.get('type', '')} - {ft.get('category', '')} (${ft.get('amount', 0):,})</div>", unsafe_allow_html=True)
                
                if f2.button("🗑️", key=f"del_ft_{ft.get('id', '')}"):
                    st.toast("💾 刪除中...", icon="🗑️")
                    st.session_state.fixed_transactions.remove(ft)
                    save_and_sync()
                    st.rerun()

    # --- 3. 專案/目標標籤設定 (Expander) ---
    with st.expander("🎯 專案/目標標籤", expanded=False):
        with st.form("add_proj_form", clear_on_submit=True):
            col_proj, col_btn = st.columns([3, 1])
            new_proj = col_proj.text_input("新增專案 (例如：🇯🇵 東京旅遊)", label_visibility="collapsed")
            if col_btn.form_submit_button("➕ 新增", type="primary") and new_proj:
                st.toast("💾 儲存中...", icon="⏳")
                st.session_state.projects.append(new_proj.strip())
                save_and_sync()
                st.rerun()
        for idx, p in enumerate(st.session_state.projects):
            if p == "無": continue
            with st.container(border=True):
                p1, p2 = st.columns([4.5, 1.5])
                p1.write(f"• **{p}**")
                if p2.button("🗑️", key=f"del_p_{idx}"):
                    st.toast("💾 刪除中...", icon="🗑️")
                    st.session_state.projects.pop(idx)
                    save_and_sync()
                    st.rerun()

    # --- 4. 成員管理 (Expander) ---
    with st.expander("🐱 成員管理", expanded=False):
        with st.form("add_member_form", clear_on_submit=True):
            col_icon, col_name = st.columns([1, 2])
            new_m_icon = col_icon.text_input("Icon", value="🐱")
            new_m_name = col_name.text_input("名稱")
            if st.form_submit_button("➕ 新增", type="primary") and new_m_name:
                st.toast("💾 儲存中...", icon="⏳")
                st.session_state.members.append(f"{new_m_icon.strip()} {new_m_name.strip()}")
                save_and_sync()
                st.rerun()
        for idx, m in enumerate(st.session_state.members):
            with st.container(border=True):
                m_col1, c_edit, c_del = st.columns([4.5, 1.5, 1.5])
                m_col1.write(f"• **{m}**")
                with c_edit:
                    with st.popover("✏️"):
                        parts = m.split(" ", 1)
                        edit_icon = st.text_input("Icon", value=parts[0] if len(parts)>1 else "🐱", key=f"m_i_{idx}")
                        edit_name = st.text_input("名稱", value=parts[1] if len(parts)>1 else parts[0], key=f"m_n_{idx}")
                        if st.button("儲存", key=f"s_m_{idx}", type="primary", use_container_width=True):
                            st.toast("💾 儲存中...", icon="⏳")
                            old_m = st.session_state.members[idx]
                            new_m = f"{edit_icon.strip()} {edit_name.strip()}"
                            st.session_state.members[idx] = new_m
                            st.session_state.expenses_df.loc[st.session_state.expenses_df["記帳人"] == old_m, "記帳人"] = new_m
                            save_and_sync()
                            st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"d_m_{idx}") and len(st.session_state.members) > 1:
                        st.toast("💾 刪除中...", icon="🗑️")
                        st.session_state.members.pop(idx)
                        save_and_sync()
                        st.rerun()

    # --- 5. 支出類別 (Expander) ---
    with st.expander("🏷️ 支出類別", expanded=False):
        with st.form("add_exp_cat_form", clear_on_submit=True):
            col_icon, col_name = st.columns([1, 2])
            new_e_icon = col_icon.text_input("Icon", value="📦")
            new_e_name = col_name.text_input("名稱")
            if st.form_submit_button("➕ 新增", type="primary") and new_e_name:
                st.toast("💾 儲存中...", icon="⏳")
                st.session_state.expense_categories.append(f"{new_e_icon.strip()} {new_e_name.strip()}")
                save_and_sync()
                st.rerun()
        for idx, c in enumerate(st.session_state.expense_categories):
            with st.container(border=True):
                c_col1, c_edit, c_del = st.columns([4.5, 1.5, 1.5])
                c_col1.write(f"• **{c}**")
                with c_edit:
                    with st.popover("✏️"):
                        parts = c.split(" ", 1)
                        edit_icon = st.text_input("Icon", value=parts[0] if len(parts)>1 else "📦", key=f"e_i_{idx}")
                        edit_name = st.text_input("名稱", value=parts[1] if len(parts)>1 else parts[0], key=f"e_n_{idx}")
                        if st.button("儲存", key=f"s_e_{idx}", type="primary", use_container_width=True):
                            st.toast("💾 儲存中...", icon="⏳")
                            old_c = st.session_state.expense_categories[idx]
                            new_c = f"{edit_icon.strip()} {edit_name.strip()}"
                            st.session_state.expense_categories[idx] = new_c
                            st.session_state.expenses_df.loc[(st.session_state.expenses_df["類別"] == old_c) & (st.session_state.expenses_df["類型"] == "支出"), "類別"] = new_c
                            save_and_sync()
                            st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"d_e_{idx}") and len(st.session_state.expense_categories) > 1:
                        st.toast("💾 刪除中...", icon="🗑️")
                        st.session_state.expense_categories.pop(idx)
                        save_and_sync()
                        st.rerun()

    # --- 6. 收入類別 (Expander) ---
    with st.expander("💰 收入類別", expanded=False):
        with st.form("add_inc_cat_form", clear_on_submit=True):
            col_icon, col_name = st.columns([1, 2])
            new_i_icon = col_icon.text_input("Icon", value="💵")
            new_i_name = col_name.text_input("名稱")
            if st.form_submit_button("➕ 新增", type="primary") and new_i_name:
                st.toast("💾 儲存中...", icon="⏳")
                st.session_state.income_categories.append(f"{new_i_icon.strip()} {new_i_name.strip()}")
                save_and_sync()
                st.rerun()
        for idx, ic in enumerate(st.session_state.income_categories):
            with st.container(border=True):
                ic_col1, c_edit, c_del = st.columns([4.5, 1.5, 1.5])
                ic_col1.write(f"• **{ic}**")
                with c_edit:
                    with st.popover("✏️"):
                        parts = ic.split(" ", 1)
                        edit_icon = st.text_input("Icon", value=parts[0] if len(parts)>1 else "💵", key=f"i_i_{idx}")
                        edit_name = st.text_input("名稱", value=parts[1] if len(parts)>1 else parts[0], key=f"i_n_{idx}")
                        if st.button("儲存", key=f"s_i_{idx}", type="primary", use_container_width=True):
                            st.toast("💾 儲存中...", icon="⏳")
                            old_ic = st.session_state.income_categories[idx]
                            new_ic = f"{edit_icon.strip()} {edit_name.strip()}"
                            st.session_state.income_categories[idx] = new_ic
                            st.session_state.expenses_df.loc[(st.session_state.expenses_df["類別"] == old_ic) & (st.session_state.expenses_df["類型"] == "收入"), "類別"] = new_ic
                            save_and_sync()
                            st.rerun()
                with c_del:
                    if st.button("🗑️", key=f"d_i_{idx}") and len(st.session_state.income_categories) > 1:
                        st.toast("💾 刪除中...", icon="🗑️")
                        st.session_state.income_categories.pop(idx)
                        save_and_sync()
                        st.rerun()

    # --- 7. 雲端資料表快速連結 (Expander) ---
    with st.expander("☁️ 雲端資料表", expanded=False):
        st.markdown("<div style='font-size:13px; color:#A9895C; margin-bottom:8px;'>點下方按鈕，直接在 Google Sheet 開啟你的記帳資料表（新分頁）。</div>", unsafe_allow_html=True)
        
        sheet_url = None
        try:
            sheet_url = st.secrets["connections"]["gsheets"].get("spreadsheet")
        except Exception:
            sheet_url = None
        
        if not sheet_url:
            # 抓不到 secrets 設定時，讓使用者手動貼一次網址（存在 session_state 裡，之後同一次連線期間都能用）
            if "manual_sheet_url" not in st.session_state:
                st.session_state.manual_sheet_url = ""
            st.session_state.manual_sheet_url = st.text_input(
                "找不到自動偵測的試算表網址，請手動貼上一次：",
                value=st.session_state.manual_sheet_url,
                placeholder="https://docs.google.com/spreadsheets/d/xxxxxxxx/edit"
            )
            sheet_url = st.session_state.manual_sheet_url

        if sheet_url:
            st.link_button("📄 開啟 Google Sheet", sheet_url, type="primary", use_container_width=True)
        else:
            st.caption("尚未設定網址，請先在上方貼上。")
