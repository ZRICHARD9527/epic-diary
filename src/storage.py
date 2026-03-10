import os
import re
import json
from datetime import datetime
from config_loader import DIARY_DIR

def ensure_dir(path=DIARY_DIR):
    if not os.path.exists(path):
        os.makedirs(path)

def save_entry(raw, drama="[无史诗转换]", emoji="📝", weather="🌫️ 天气未知", ts=None):
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    timestamp = ts if ts else now.strftime("%H-%M-%S")
    
    date_path = os.path.join(DIARY_DIR, today)
    ensure_dir(date_path)
    
    file_path = os.path.join(date_path, f"{timestamp}.md")
    entry_content = f"TIMESTAMP: {timestamp.replace('-', ':')}\nWEATHER: {weather}\nREAL: {raw}\nDRAMA: {drama}\nEMOJI: {emoji}\n"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(entry_content)
    
    # 【新增】清空当日的心情缓存，因为数据变了，需要重新统计
    mood_cache = os.path.join(date_path, "mood_report.json")
    if os.path.exists(mood_cache):
        os.remove(mood_cache)
        
    return timestamp.replace('-', ':')

def update_entry(date_folder, timestamp, new_data):
    file_name = timestamp.replace(':', '-') + ".md"
    folder_name = date_folder.replace(".md", "")
    path = os.path.join(DIARY_DIR, folder_name, file_name)
    if not os.path.exists(path): return
    entry = parse_single_file(path)
    entry.update(new_data)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"TIMESTAMP: {entry['ts']}\nWEATHER: {entry['weather']}\nREAL: {entry['real']}\nDRAMA: {entry['drama']}\nEMOJI: {entry['emoji']}\n")

def parse_single_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        b = f.read()
    entry = {}
    ts = re.search(r'TIMESTAMP: (.*?)\n', b)
    wea = re.search(r'WEATHER: (.*?)\n', b)
    real = re.search(r'REAL: (.*?)\nDRAMA:', b, re.DOTALL)
    drama = re.search(r'DRAMA: (.*?)\nEMOJI:', b, re.DOTALL)
    emoji = re.search(r'EMOJI: (.*?)$', b, re.DOTALL)
    entry['ts'] = ts.group(1).strip() if ts else "未知"
    entry['weather'] = wea.group(1).strip() if wea else "🌫️ 天气未知"
    entry['real'] = real.group(1).strip() if real else ""
    entry['drama'] = drama.group(1).strip() if drama else ""
    entry['emoji'] = emoji.group(1).strip() if emoji else ""
    return entry

def parse_entries(date_path_or_folder):
    folder_name = os.path.basename(date_path_or_folder).replace(".md", "")
    target_dir = os.path.join(DIARY_DIR, folder_name)
    if not os.path.exists(target_dir) or not os.path.isdir(target_dir): return []
    entries = []
    files = sorted([f for f in os.listdir(target_dir) if f.endswith(".md")], reverse=True)
    for f in files:
        entries.append(parse_single_file(os.path.join(target_dir, f)))
    return entries

def get_all_diary_files():
    ensure_dir()
    dirs = sorted([d for d in os.listdir(DIARY_DIR) if os.path.isdir(os.path.join(DIARY_DIR, d))], reverse=True)
    return dirs

def delete_entry(date_folder, timestamp):
    folder_name = date_folder.replace(".md", "")
    file_name = timestamp.replace(':', '-') + ".md"
    path = os.path.join(DIARY_DIR, folder_name, file_name)
    if os.path.exists(path):
        os.remove(path)
    target_dir = os.path.join(DIARY_DIR, folder_name)
    if os.path.exists(target_dir) and not os.listdir(target_dir):
        os.rmdir(target_dir)

# 【新增】心情报告存储逻辑
def save_mood_report(date_folder, report_data):
    date_path = os.path.join(DIARY_DIR, date_folder)
    if not os.path.exists(date_path): return
    with open(os.path.join(date_path, "mood_report.json"), "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

def load_mood_report(date_folder):
    path = os.path.join(DIARY_DIR, date_folder, "mood_report.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
