import streamlit as st
import os
import time
from datetime import datetime
import utils
import storage
import api_service
from config_loader import UI_SETTINGS, AI_SETTINGS

# 设置页面配置 (从配置读取)
st.set_page_config(
    page_title=UI_SETTINGS.get("page_title", "EpicDiary"), 
    page_icon=UI_SETTINGS.get("page_icon", "📖"), 
    layout="wide"
)

# 动态生成 CSS (从配置读取圆角等)
radius = UI_SETTINGS.get("button_border_radius", "4px")
st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    .stTextArea textarea {{ font-size: 1.1rem !important; }}
    .detail-card {{ padding: 2rem; border-radius: 15px; background-color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
    .time-tag {{ color: #888; font-size: 0.85rem; }}
    .weather-tag {{ color: #007bff; font-size: 0.85rem; margin-left: 10px; font-weight: bold; }}
    .stButton button {{ border-radius: {radius}; }}
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 5px !important;
    }}
    [data-testid="stHorizontalBlock"] > div {{
        width: auto !important;
        min-width: fit-content !important;
        flex: none !important;
        padding-right: 0px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏 ---
st.sidebar.title("📜 史诗档案库")

with st.sidebar.expander("⚙️ 应用设置"):
    default_city = AI_SETTINGS.get("default_city", "北京")
    saved_city = st.text_input("当前城市", value=st.session_state.get('user_city', default_city))
    st.session_state.user_city = saved_city

st.sidebar.markdown("---")
search_q = st.sidebar.text_input("🔍 搜索记忆...", placeholder="输入关键字")
all_files = storage.get_all_diary_files()
selected_date_file = st.sidebar.selectbox("选择日期", all_files if all_files else ["尚无记录"])

if selected_date_file != "尚无记录":
    entries = storage.parse_entries(os.path.join(storage.DIARY_DIR, selected_date_file))
    if search_q:
        entries = [e for e in entries if search_q.lower() in e['real'].lower() or search_q.lower() in e['drama'].lower()]
    
    st.sidebar.markdown(f"**记录点 ({len(entries)})**")
    for i, e in enumerate(entries):
        snippet = e['real'][:12] + "..." if len(e['real']) > 12 else e['real']
        if st.sidebar.button(f"{e['ts']} | {e['emoji']} | {snippet}", key=f"side_{i}"):
            st.session_state.selected_ts = e['ts']
            st.session_state.current_date = selected_date_file

# --- 主界面 ---
st.title("📖 EpicDiary")

st.write("### ✨ 记录新日记 (Ctrl+Enter 提交)")
with st.form("diary_form", clear_on_submit=True):
    user_input = st.text_area("发生了什么？", height=100, label_visibility="collapsed")
    c1, c2, _ = st.columns([1, 1, 5])
    with c1: submit_magic = st.form_submit_button("🪄 魔法转换")
    with c2: submit_pure = st.form_submit_button("💾 纯净保存")
    
    if (submit_magic or submit_pure) and user_input.strip():
        ts = storage.save_entry(user_input)
        if submit_pure:
            st.toast("✅ 已快速存入史册！")
            st.rerun()
        else:
            with st.spinner(f"🔮 正在同步 {st.session_state.user_city} 天气并编织史诗..."):
                w, d, e = api_service.generate_full_package(user_input, st.session_state.user_city)
                storage.update_entry(datetime.now().strftime("%Y-%m-%d.md"), ts, {'drama': d, 'emoji': e, 'weather': w})
                st.success("🎉 史诗编织完成！")
                st.session_state.selected_ts = ts
                st.session_state.current_date = datetime.now().strftime("%Y-%m-%d.md")
                st.rerun()

st.markdown("---")

if 'selected_ts' in st.session_state:
    target_date = st.session_state.current_date
    current_entries = storage.parse_entries(os.path.join(storage.DIARY_DIR, target_date))
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
            st.markdown(f"""
            <div class="detail-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="time-tag">📅 {target_date.replace('.md','')} | ⏰ {entry['ts']}</span>
                        <span class="weather-tag">{entry['weather']}</span>
                    </div>
                    <span style="font-size: 1.5rem;">{entry['emoji']}</span>
                </div>
                <p style="font-size: 1.1rem; color: #444; margin-top:15px;"><b>现实回响：</b><br>{entry['real']}</p>
                <div style="background-color: #fff9db; padding: 20px; border-radius: 10px; border-left: 5px solid #fab005; margin: 20px 0;">
                    <p style="font-family: 'serif'; font-size: 1.1rem; line-height: 1.6; color: #665c00; margin:0;">
                        <i>“{entry['drama']}”</i>
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c_edit, c_del, _ = st.columns([1, 1, 10])
            if c_edit.button("✏️ 编辑", key=f"e_{entry['ts']}"): st.session_state.editing = True; st.rerun()
            if c_del.button("🗑️ 删除", key=f"d_{entry['ts']}"):
                storage.delete_entry(target_date, entry['ts'])
                del st.session_state.selected_ts
                st.rerun()
else:
    st.info("👈 请从左侧档案中选择一段记忆碎片。")
