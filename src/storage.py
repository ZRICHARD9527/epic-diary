import os
import re
from datetime import datetime
from config_loader import DIARY_DIR

def ensure_dir(path=DIARY_DIR):
    if not os.path.exists(path):
        os.makedirs(path)

def save_entry(raw, drama="[无史诗转换]", emoji="📝", weather="🌫️ 天气未知", ts=None):
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    timestamp = ts if ts else now.strftime("%H-%M-%S") # 使用横杠防止路径非法
    
    # 创建日期文件夹
    date_path = os.path.join(DIARY_DIR, today)
    ensure_dir(date_path)
    
    file_path = os.path.join(date_path, f"{timestamp}.md")
    
    # 单独存储的结构 (更简洁，不再需要 START/END 标记)
    entry_content = f"TIMESTAMP: {timestamp.replace('-', ':')}\nWEATHER: {weather}\nREAL: {raw}\nDRAMA: {drama}\nEMOJI: {emoji}\n"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(entry_content)
    return timestamp.replace('-', ':')

def update_entry(date_folder, timestamp, new_data):
    # 兼容处理：将 20:44:26 转回文件名 20-44-26
    file_name = timestamp.replace(':', '-') + ".md"
    # 兼容处理：如果传入的是 "2026-03-09.md"，去掉后缀
    folder_name = date_folder.replace(".md", "")
    
    path = os.path.join(DIARY_DIR, folder_name, file_name)
    if not os.path.exists(path):
        return
    
    # 读取并更新数据
    entry = parse_single_file(path)
    entry.update(new_data)
    
    # 重新写入
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"TIMESTAMP: {entry['ts']}\nWEATHER: {entry['weather']}\nREAL: {entry['real']}\nDRAMA: {entry['drama']}\nEMOJI: {entry['emoji']}\n")

def parse_single_file(file_path):
    """解析单个日记文件"""
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
    """扫描文件夹下的所有日记文件并汇总"""
    # 兼容旧代码：如果传入的是全路径或带.md的文件名
    folder_name = os.path.basename(date_path_or_folder).replace(".md", "")
    target_dir = os.path.join(DIARY_DIR, folder_name)
    
    if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
        return []
    
    entries = []
    files = sorted([f for f in os.listdir(target_dir) if f.endswith(".md")], reverse=True)
    for f in files:
        entries.append(parse_single_file(os.path.join(target_dir, f)))
    return entries

def get_all_diary_files():
    """获取所有日期文件夹"""
    ensure_dir()
    # 返回文件夹列表 (YYYY-MM-DD)
    dirs = sorted([d for d in os.listdir(DIARY_DIR) if os.path.isdir(os.path.join(DIARY_DIR, d))], reverse=True)
    return dirs

def delete_entry(date_folder, timestamp):
    folder_name = date_folder.replace(".md", "")
    file_name = timestamp.replace(':', '-') + ".md"
    path = os.path.join(DIARY_DIR, folder_name, file_name)
    
    if os.path.exists(path):
        os.remove(path)
        
    # 如果文件夹空了，删除文件夹
    target_dir = os.path.join(DIARY_DIR, folder_name)
    if not os.listdir(target_dir):
        os.rmdir(target_dir)
