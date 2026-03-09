import streamlit as st
import os
import time
from datetime import datetime
import utils
import storage
import api_service
import config_loader
from config_loader import UI_SETTINGS, AI_SETTINGS

# 加载实时配置
config = config_loader.load_config()

# 设置页面配置
st.set_page_config(
    page_title=UI_SETTINGS.get("page_title", "EpicDiary"), 
    page_icon=UI_SETTINGS.get("page_icon", "📖"), 
    layout="wide"
)

# --- 深度定制 CSS ---
radius = UI_SETTINGS.get("button_border_radius", "4px")
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&display=swap');
    
    .main {{ background-color: #f0f2f5; }}

    /* 【UI 优化】整体上移，减小顶部留白 */
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 0rem !important;
    }}

    /* 侧边栏按钮左对齐与省略号 */
    [data-testid="stSidebar"] button {{
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 15px !important;
    }}
    [data-testid="stSidebar"] button div p {{
        display: block !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        width: 100% !important;
        text-align: left !important;
    }}

    /* 详情卡片与动画 */
    .fade-in {{ animation: fadeIn 0.5s ease-out; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

    .detail-card {{
        padding: 2.5rem;
        border-radius: 18px;
        background-color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.02);
        text-align: left !important;
    }}
    
    .epic-drama {{
        font-family: 'Noto Serif SC', 'serif';
        font-size: 1.25rem;
        line-height: 1.8;
        color: #2c3e50;
        margin: 2rem 0;
        padding-left: 20px;
        border-left: 4px solid #4CAF50;
        background: linear-gradient(to right, #f9fff9, transparent);
    }}

    /* 按钮锁定逻辑 (防止走位) */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 8px !important;
    }}
    [data-testid="stHorizontalBlock"] > div {{
        width: auto !important;
        min-width: fit-content !important;
        flex: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏 ---
with st.sidebar:
    # 1. 设置按钮放到最顶部
    with st.popover("⚙️ 应用设置"):
        st.write("### ⚙️ 设置")
        current_city = config['ai_settings'].get('default_city', '北京')
        new_city = st.text_input("当前城市", value=current_city)
        if new_city != current_city:
            config_loader.update_setting('ai_settings', 'default_city', new_city)
            st.success(f"已保存: {new_city}")
            time.sleep(1)
            st.rerun()
    
    st.title("📜 史诗档案库")
    st.markdown("---")
    search_q = st.text_input("🔍 搜索记忆...", placeholder="输入关键词...")
    all_files = storage.get_all_diary_files()
    selected_date_file = st.selectbox("选择日期", all_files if all_files else ["尚无记录"])

    if selected_date_file != "尚无记录":
        entries = storage.parse_entries(selected_date_file)
        if search_q:
            entries = [e for e in entries if search_q.lower() in e['real'].lower() or search_q.lower() in e['drama'].lower()]
        
        st.markdown(f"**记录点 ({len(entries)})**")
        for i, e in enumerate(entries):
            snippet = e['real'][:15] + "..." if len(e['real']) > 15 else e['real']
            btn_label = f"{e['ts']} | {e['emoji']} | {snippet}"
            if st.button(btn_label, key=f"side_{i}", use_container_width=True):
                st.session_state.selected_ts = e['ts']
                st.session_state.current_date = selected_date_file

# --- 主界面 ---
st.title("📖 EpicDiary")

# 撰写区
st.write("### ✨ 记录新日记 (Ctrl+Enter 提交)")
with st.form("diary_form", clear_on_submit=True):
    user_input = st.text_area("发生了什么？", height=100, label_visibility="collapsed")
    btn_col1, btn_col2, _ = st.columns([1.2, 1.2, 5])
    with btn_col1: submit_magic = st.form_submit_button("🪄 魔法转换")
    with btn_col2: submit_pure = st.form_submit_button("💾 纯净保存")
    
    if (submit_magic or submit_pure) and user_input.strip():
        ts = storage.save_entry(user_input)
        if submit_pure:
            st.toast("✅ 已快速存入史册！")
            st.rerun()
        else:
            active_city = config['ai_settings'].get('default_city', '北京')
            with st.spinner(f"🔮 正在同步 {active_city} 天气并编织史诗..."):
                w, d, e = api_service.generate_full_package(user_input, active_city)
                storage.update_entry(datetime.now().strftime("%Y-%m-%d"), ts, {'drama': d, 'emoji': e, 'weather': w})
                st.success("🎉 史诗编织完成！")
                st.session_state.selected_ts = ts
                st.session_state.current_date = datetime.now().strftime("%Y-%m-%d")
                st.rerun()

st.markdown("---")

# 详情展示区
if 'selected_ts' in st.session_state:
    target_date = st.session_state.current_date
    current_entries = storage.parse_entries(target_date)
    entry = next((e for e in current_entries if e['ts'] == st.session_state.selected_ts), None)
    
    if entry:
        if st.session_state.get('editing'):
            with st.form("edit_form"):
                st.write("### ✏️ 修改此条记忆")
                e_real = st.text_input("原话", value=entry['real'])
                e_drama = st.text_area("史诗内容", value=entry['drama'], height=200)
                e_emoji = st.text_input("Emoji", value=entry['emoji'])
                if st.form_submit_button("保存"):
                    storage.update_entry(target_date, entry['ts'], {'real': e_real, 'drama': e_drama, 'emoji': e_emoji})
                    st.session_state.editing = False
                    st.rerun()
                if st.form_submit_button("取消"):
                    st.session_state.editing = False
                    st.rerun()
        else:
            with st.container():
                st.markdown(f"""
                <div class="fade-in">
                    <div class="detail-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 15px;">
                            <div>
                                <span class="time-tag">📅 {target_date} | ⏰ {entry['ts']}</span>
                                <span class="weather-tag" style="margin-left:15px; color:#4CAF50; font-weight:bold;">{entry['weather']}</span>
                            </div>
                            <span style="font-size: 1.8rem;">{entry['emoji']}</span>
                        </div>
                        <div style="font-size: 1.05rem; color: #555; margin-top: 1.5rem; line-height: 1.6;">
                            <b>现实回响：</b><br>{entry['real']}
                        </div>
                        <div class="epic-drama">
                            “{entry['drama']}”
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                action_col1, action_col2, _ = st.columns([1.2, 1.2, 10])
                if action_col1.button("✏️ 编辑", key=f"e_{entry['ts']}"): 
                    st.session_state.editing = True
                    st.rerun()
                if action_col2.button("🗑️ 删除", key=f"d_{entry['ts']}"):
                    storage.delete_entry(target_date, entry['ts'])
                    del st.session_state.selected_ts
                    st.rerun()
else:
    st.info("👈 请从左侧档案中选择一段记忆碎片，开启您的史诗之旅。")
