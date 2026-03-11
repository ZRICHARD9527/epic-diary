import os
import re
import json
from datetime import datetime
from config_loader import DIARY_DIR
import database

def ensure_dir(path=DIARY_DIR):
    if not os.path.exists(path):
        os.makedirs(path)

# 轻量级元数据缓存
_entries_cache = {}

def save_entry(raw, drama="[无史诗转换]", emoji="📝", weather="🌫️ 天气未知", ts=None):
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    
    # 强制清除对应日期的缓存
    if today in _entries_cache: del _entries_cache[today]
    
    timestamp = ts if ts else now.strftime("%H-%M-%S")
    date_path = os.path.join(DIARY_DIR, today)
    ensure_dir(date_path)
    
    file_path = os.path.join(date_path, f"{timestamp.replace(':', '-')}.md")
    # 标准化格式：使用明确的分隔符确保多行解析
    entry_content = (
        f"TIMESTAMP: {timestamp.replace('-', ':')}\n"
        f"WEATHER: {weather}\n"
        f"REAL: {raw}\n"
        f"DRAMA: {drama}\n"
        f"EMOJI: {emoji}\n"
    )
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(entry_content)
    
    # 同时索引到数据库 (加速搜索和关联)
    try:
        db = database.get_database()
        db.index_entry(today, timestamp.replace('-', ':'), weather, raw, drama, emoji)
    except Exception as e:
        import logging
        logging.error(f"Failed to index entry {timestamp}: {e}")

    return timestamp.replace('-', ':')

def update_entry(date_folder, timestamp, new_data):
    """精准字段更新，支持多行内容"""
    file_name = timestamp.replace(':', '-') + ".md"
    path = os.path.join(DIARY_DIR, date_folder, file_name)
    if not os.path.exists(path):
        return False
    
    # 清除对应日期的缓存
    if date_folder in _entries_cache: del _entries_cache[date_folder]
    
    try:
        # 读取完整内容
        entry = parse_single_file(path)
        if not entry: return False
        
        # 应用更新
        for k, v in new_data.items():
            if k in entry: entry[k] = v
            
        # 写回文件
        save_entry(entry['real'], entry['drama'], entry['emoji'], entry['weather'], timestamp.replace(':', '-'))
        return True
    except Exception as e:
        import logging
        logging.error(f"Failed to update entry {path}: {e}")
        return False

def parse_single_file(file_path):
    """使用正则表达式进行非贪婪多行匹配，确保 REAL/DRAMA 完整提取"""
    if not os.path.exists(file_path): return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        def fetch(pattern, text):
            res = re.search(pattern, text, re.DOTALL)
            return res.group(1).strip() if res else ""

        # 核心逻辑：从 REAL 匹配到 DRAMA，从 DRAMA 匹配到 EMOJI
        return {
            'ts': fetch(r'TIMESTAMP: (.*?)\n', content),
            'weather': fetch(r'WEATHER: (.*?)\n', content),
            'real': fetch(r'REAL: (.*?)\nDRAMA:', content),
            'drama': fetch(r'DRAMA: (.*?)\nEMOJI:', content),
            'emoji': fetch(r'EMOJI: (.*?)(?:\n|$)', content)
        }
    except Exception as e:
        import logging
        logging.error(f"Error parsing file {file_path}: {e}")
        return None

def parse_entries(date_folder):
    if date_folder in _entries_cache:
        return _entries_cache[date_folder]
        
    target_dir = os.path.join(DIARY_DIR, date_folder)
    if not os.path.exists(target_dir): return []
    entries = []
    try:
        files = [f for f in os.listdir(target_dir) if f.endswith(".md") and len(f.split('-')) == 3]
        files.sort(reverse=True) 
        for f in files:
            res = parse_single_file(os.path.join(target_dir, f))
            if res: entries.append(res)
        _entries_cache[date_folder] = entries
    except Exception as e:
        import logging
        logging.error(f"Error parsing entries in {date_folder}: {e}")
    return entries

def get_all_diary_files():
    ensure_dir()
    return sorted([d for d in os.listdir(DIARY_DIR) if os.path.isdir(os.path.join(DIARY_DIR, d))], reverse=True)

def get_related_entries(date_folder, timestamp, limit=3):
    """通过 SQLite 数据库寻找相关条目 (极速关联)"""
    try:
        db = database.get_database()
        # 寻找与当前条目 real 内容关键词重叠的历史记录
        results = db.get_related_entries(date_folder, timestamp.replace('-', ':'), limit)
        # 格式化输出为前端需要的字段
        return [{
            "date": r['date'],
            "ts": r['ts'],
            "preview": r['real'][:45] + "...",
            "score": r.get('score', 1)
        } for r in results]
    except Exception as e:
        import logging
        logging.error(f"Failed to fetch related entries from DB: {e}")
        return []

def delete_entry(date_folder, timestamp):
    """从磁盘和数据库中抹除这段记忆"""
    file_name = timestamp.replace(':', '-') + ".md"
    path = os.path.join(DIARY_DIR, date_folder, file_name)
    
    # 1. 删除文件
    if os.path.exists(path):
        os.remove(path)
    
    # 2. 清理缓存
    if date_folder in _entries_cache:
        del _entries_cache[date_folder]
        
    # 3. 从数据库中删除
    try:
        db = database.get_database()
        db.delete_entry(date_folder, timestamp.replace('-', ':'))
    except Exception as e:
        import logging
        logging.error(f"Failed to delete database entry: {e}")
        
    # 4. 如果文件夹空了，删除文件夹
    target_dir = os.path.join(DIARY_DIR, date_folder)
    if os.path.exists(target_dir) and not os.listdir(target_dir):
        os.rmdir(target_dir)
