import os
import re
from datetime import datetime
from config_loader import DIARY_DIR

def ensure_dir():
    if not os.path.exists(DIARY_DIR):
        os.makedirs(DIARY_DIR)

def save_entry(raw, drama="[无史诗转换]", emoji="📝", weather="🌫️ 天气未知", ts=None):
    ensure_dir()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    timestamp = ts if ts else now.strftime("%H:%M:%S")
    file_path = os.path.join(DIARY_DIR, f"{today}.md")
    
    entry_block = f"\n---ENTRY_START---\nTIMESTAMP: {timestamp}\nWEATHER: {weather}\nREAL: {raw}\nDRAMA: {drama}\nEMOJI: {emoji}\n---ENTRY_END---\n"
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(entry_block)
    return timestamp

def update_entry(date_file, timestamp, new_data):
    path = os.path.join(DIARY_DIR, date_file)
    entries = parse_entries(path)
    for e in entries:
        if e['ts'] == timestamp:
            e.update(new_data)
    rewrite_file(path, entries)

def parse_entries(file_path):
    if not os.path.exists(file_path): return []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    blocks = re.findall(r'---ENTRY_START---(.*?)---ENTRY_END---', content, re.DOTALL)
    entries = []
    for b in blocks:
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
        entries.append(entry)
    return entries[::-1]

def rewrite_file(file_path, entries):
    with open(file_path, "w", encoding="utf-8") as f:
        for e in entries[::-1]:
            f.write(f"\n---ENTRY_START---\nTIMESTAMP: {e['ts']}\nWEATHER: {e['weather']}\nREAL: {e['real']}\nDRAMA: {e['drama']}\nEMOJI: {e['emoji']}\n---ENTRY_END---\n")

def get_all_diary_files():
    ensure_dir()
    return sorted([f for f in os.listdir(DIARY_DIR) if f.endswith(".md")], reverse=True)

def delete_entry(date_file, timestamp):
    path = os.path.join(DIARY_DIR, date_file)
    entries = parse_entries(path)
    new_entries = [e for e in entries if e['ts'] != timestamp]
    rewrite_file(path, new_entries)
    return len(new_entries)
